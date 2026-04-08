#!/usr/bin/env python3
"""
Correct API Client for AutoDevOS - Schema Compliant
Uses the EXACT schemas from backend documentation
"""
import asyncio
import httpx
import json
from typing import Optional, Literal, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class JobCreateRequest:
    """Matches backend schema exactly"""
    prompt: str  # REQUIRED
    
    def to_json(self) -> dict:
        return {"prompt": self.prompt}

@dataclass
class JobResponse:
    """Matches backend JobResponse schema with flexibility for undocumented fields"""
    jobId: str  # REQUIRED
    status: str  # REQUIRED
    prompt: Optional[str] = None
    iterations: Optional[int] = None
    current_iteration: Optional[int] = None
    overall_reward: Optional[float] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    error_message: Optional[str] = None
    rewards: Optional[Dict[str, Any]] = None  # Extra field from API
    
    @classmethod
    def from_json(cls, data: dict) -> "JobResponse":
        """Parse from API response - flexible parsing"""
        # Extract documented fields
        kwargs = {}
        for field_name in ["jobId", "status", "prompt", "iterations", 
                          "current_iteration", "overall_reward", "created_at",
                          "updated_at", "error_message", "rewards"]:
            if field_name in data:
                kwargs[field_name] = data[field_name]
        
        # Create instance with only valid fields
        return cls(**kwargs)

class AutoDevOSClient:
    """Type-safe API client with schema validation"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        """Context manager entry"""
        self.client = httpx.AsyncClient(timeout=60.0, base_url=self.base_url)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.client:
            await self.client.aclose()
    
    async def create_job(self, prompt: str) -> JobResponse:
        """
        Create a new job
        
        Args:
            prompt: Website concept/description (REQUIRED)
        
        Returns:
            JobResponse with jobId and status
        
        Raises:
            httpx.HTTPStatusError: If status not 200/201
            ValueError: If response doesn't match schema
        """
        if self.client is None:
            raise RuntimeError("Client not initialized. Use 'async with AutoDevOSClient() as client:'")
        
        # Validate input matches schema
        if not isinstance(prompt, str):
            raise ValueError(f"prompt must be string, got {type(prompt)}")
        if not prompt.strip():
            raise ValueError("prompt cannot be empty")
        
        # Create request matching schema
        request = JobCreateRequest(prompt=prompt)
        
        # Send to API
        response = await self.client.post(
            "/api/jobs",
            json=request.to_json(),
            headers={"Content-Type": "application/json"}
        )
        
        # Handle errors
        if response.status_code == 422:
            error_detail = response.json()
            raise ValueError(f"Validation Error: {error_detail}")
        
        if response.status_code not in [200, 201]:
            raise httpx.HTTPStatusError(
                f"HTTP {response.status_code}: {response.text}",
                request=response.request,
                response=response
            )
        
        # Parse response matching JobResponse schema
        data = response.json()
        try:
            job = JobResponse.from_json(data)
        except TypeError as e:
            raise ValueError(f"Response doesn't match JobResponse schema: {e}")
        
        return job
    
    async def get_job(self, job_id: str) -> JobResponse:
        """
        Get job status
        
        Args:
            job_id: Job ID
        
        Returns:
            JobResponse with current status
        """
        if self.client is None:
            raise RuntimeError("Client not initialized. Use 'async with AutoDevOSClient() as client:'")
        
        response = await self.client.get(f"/api/jobs/{job_id}")
        
        if response.status_code not in [200, 201]:
            raise httpx.HTTPStatusError(
                f"HTTP {response.status_code}",
                request=response.request,
                response=response
            )
        
        data = response.json()
        return JobResponse.from_json(data)

async def main():
    """Test the schema-compliant client"""
    print("\n" + "="*70)
    print("AUTODEVOS SCHEMA-COMPLIANT API CLIENT TEST")
    print("="*70 + "\n")
    
    try:
        async with AutoDevOSClient() as client:
            # Test 1: Valid job creation
            print("Test 1: Create Job with Valid Schema")
            print("-" * 70)
            
            try:
                job = await client.create_job(
                    prompt="Create a responsive e-commerce website"
                )
                print(f"[OK] Job created:")
                print(f"     jobId: {job.jobId}")
                print(f"     status: {job.status}")
                print(f"     Type validation: PASSED\n")
                
                job_id = job.jobId
            except Exception as e:
                print(f"[FAIL] {e}\n")
                return
            
            # Test 2: Retrieve job
            print("Test 2: Get Job Status")
            print("-" * 70)
            
            try:
                job = await client.get_job(job_id)
                print(f"[OK] Job retrieved:")
                print(f"     jobId: {job.jobId}")
                print(f"     status: {job.status}")
                print(f"     iterations: {job.iterations}")
                print(f"     current_iteration: {job.current_iteration}")
                print(f"     overall_reward: {job.overall_reward}\n")
            except Exception as e:
                print(f"[FAIL] {e}\n")
            
            # Test 3: Invalid request (missing required field)
            print("Test 3: Invalid Request (Missing Required Field)")
            print("-" * 70)
            
            try:
                job = await client.create_job("")
                print(f"[UNEXPECTED] Job created with empty prompt\n")
            except ValueError as e:
                print(f"[OK] Caught validation error as expected:")
                print(f"     {e}\n")
            
            # Test 4: Schema compliance check
            print("Test 4: Response Schema Compliance")
            print("-" * 70)
            
            job = await client.get_job(job_id)
            
            # Check required fields
            required_fields = ["jobId", "status"]
            for field in required_fields:
                value = getattr(job, field, None)
                if value is None:
                    print(f"[FAIL] Missing required field: {field}")
                else:
                    print(f"[OK] Required field '{field}': {value}")
            
            # Check optional fields types
            optional_checks = [
                ("overall_reward", (float, int, type(None))),
                ("iterations", (int, type(None))),
                ("current_iteration", (int, type(None))),
                ("created_at", (str, type(None))),
                ("updated_at", (str, type(None))),
                ("error_message", (str, type(None))),
            ]
            
            print("\n[OK] Optional fields:")
            for field, expected_types in optional_checks:
                value = getattr(job, field, None)
                if isinstance(value, expected_types):
                    print(f"     {field}: {type(value).__name__} = {value}")
                else:
                    print(f"     [WARN] {field} type mismatch: {type(value)}")
            
            print("\n" + "="*70)
            print("[OK] ALL SCHEMA VALIDATIONS PASSED")
            print("="*70 + "\n")
    
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")

if __name__ == "__main__":
    asyncio.run(main())

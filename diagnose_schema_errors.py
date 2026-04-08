#!/usr/bin/env python3
"""Diagnose schema validation errors from backend"""
import asyncio
import httpx
import json

async def diagnose_errors():
    """Test and capture exact error responses"""
    base_url = "http://localhost:8000"
    
    print("\n" + "="*70)
    print("SCHEMA VALIDATION ERROR DIAGNOSIS")
    print("="*70 + "\n")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test 1: Try creating a job with minimal request
        print("Test 1: Create Job with JSONRequest")
        print("-" * 70)
        
        payload = {"prompt": "test"}
        print(f"Sending: {json.dumps(payload)}")
        
        response = await client.post(
            f"{base_url}/api/jobs",
            json=payload
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
        if response.status_code != 200 and response.status_code != 201:
            error_data = response.json()
            print(f"\nERROR DETAILS:")
            print(json.dumps(error_data, indent=2))
        
        # Test 2: Check current backend configuration
        print("\n\nTest 2: Check Backend API Schema")
        print("-" * 70)
        
        response = await client.get(f"{base_url}/openapi.json")
        if response.status_code == 200:
            schema = response.json()
            
            # Find JobCreateRequest schema
            if "components" in schema and "schemas" in schema["components"]:
                schemas = schema["components"]["schemas"]
                
                if "JobCreateRequest" in schemas:
                    print("JobCreateRequest schema:")
                    print(json.dumps(schemas["JobCreateRequest"], indent=2))
                
                if "JobResponse" in schemas:
                    print("\nJobResponse schema:")
                    print(json.dumps(schemas["JobResponse"], indent=2))
        
        # Test 3: Try with no data
        print("\n\nTest 3: Create Job with Empty Body")
        print("-" * 70)
        
        response = await client.post(f"{base_url}/api/jobs", json={})
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:500]}")

if __name__ == "__main__":
    asyncio.run(diagnose_errors())

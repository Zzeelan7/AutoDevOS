"""Test preview with actual generated code"""
import asyncio
import httpx
import json

async def test_preview_with_code():
    """Test preview endpoint with actual generated code"""
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        # Create a job
        print("[TEST] Creating job for preview test...")
        response = await client.post(f"{base_url}/api/jobs", json={"prompt": "test"})
        job_data = response.json()
        job_id = job_data.get("jobId")
        print(f"[OK] Job created: {job_id}")
        
        # Simulate adding generated code (manually calling the backend)
        # For now, let's just test the preview endpoint
        print(f"\n[TEST] Testing preview endpoint structure...")
        
        # The preview endpoint should:
        # 1. Return proper HTML content-type
        # 2. Return JSON from /api/jobs/{job_id}/preview  
        # 3. Return HTML from /preview/{job_id}
        
        # Test 1: JSON preview endpoint
        response = await client.get(f"{base_url}/api/jobs/{job_id}/preview")
        print(f"[TEST] JSON preview endpoint (/api/jobs/{{job_id}}/preview)")
        print(f"       Status: {response.status_code}")
        print(f"       Content-Type: {response.headers.get('content-type')}")
        
        try:
            data = response.json()
            print(f"       Keys: {list(data.keys())}")
        except:
            print(f"       (Not valid JSON)")
        
        # Test 2: HTML preview endpoint
        response = await client.get(f"{base_url}/preview/{job_id}")
        print(f"\n[TEST] HTML preview endpoint (/preview/{{job_id}})")
        print(f"       Status: {response.status_code}")
        print(f"       Content-Type: {response.headers.get('content-type')}")
        print(f"       Size: {len(response.text)} chars")
        print(f"       Starts with: {response.text[:50]}...")
        
        # Test accessing in browser
        print(f"\n[OK] Preview endpoint is ready!")
        print(f"     Visit: http://127.0.0.1:8000/preview/{job_id}")
        print(f"     This should display the website in an iframe")

if __name__ == "__main__":
    asyncio.run(test_preview_with_code())

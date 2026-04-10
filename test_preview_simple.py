"""Test preview endpoint with a pre-generated job"""
import asyncio
import httpx

async def test_preview_static():
    """Test preview endpoint with a manually created job"""
    base_url = "http://localhost:8000"
    
    # First, create a job with some pre-generated code
    job_id = "preview-test-" + str(int(__import__('time').time() * 1000))
    
    # Access the storage directly through a POST request
    async with httpx.AsyncClient() as client:
        # Create a job
        print("[TEST] Creating static test job...")
        response = await client.post(f"{base_url}/api/jobs", json={"prompt": "test"})
        job_data = response.json()
        job_id = job_data.get("jobId")
        print(f"[OK] Job created: {job_id}")
        
        # Simulate adding generated code to the job by fetching it first
        response = await client.get(f"{base_url}/api/jobs/{job_id}")
        print(f"[DEBUG] Job before update: {response.json()}")
        
        # Now test the preview endpoint - should return "Job not complete" message
        print(f"\n[TEST] Fetching preview for incomplete job...")
        response = await client.get(f"{base_url}/preview/{job_id}")
        
        if response.status_code == 200:
            html = response.text
            print("[OK] Preview endpoint responded")
            print(f"     Response size: {len(html)} chars")
            print(f"     Content type: {response.headers.get('content-type')}")
            
            # Check if it's HTML
            if html.startswith("<html") or html.startswith("<!DOCTYPE"):
                print("[OK] Response is valid HTML")
                
                # Print first 500 chars
                print("\n[PREVIEW] First 500 chars of response:")
                print(html[:500])
                print("...")
            else:
                print("[FAIL] Response is not HTML")
                print(html[:500])
        else:
            print(f"[FAIL] Preview fetch failed: {response.status_code}")
            print(response.text)

if __name__ == "__main__":
    asyncio.run(test_preview_static())

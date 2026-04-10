"""Test preview endpoint rendering"""
import asyncio
import httpx
import json

async def test_preview():
    base_url = "http://localhost:8000"
    
    # Create a job with test prompt
    prompt = "Create a simple colorful button with gradient background and hover effect"
    
    print("[TEST] Creating job with preview test prompt...")
    
    async with httpx.AsyncClient() as client:
        # Create job
        response = await client.post(f"{base_url}/api/jobs", json={"prompt": prompt})
        if response.status_code != 200:
            print(f"[FAIL] Job creation failed: {response.status_code}")
            print(response.text)
            return
        
        job_data = response.json()
        job_id = job_data.get("jobId") or job_data.get("job_id")
        print(f"[OK] Job created: {job_id}")
        print(f"     Response keys: {list(job_data.keys())}")
        
        # Wait for generation to complete
        print("[WAIT] Waiting for code generation...")
        max_wait = 30
        waited = 0
        
        while waited < max_wait:
            response = await client.get(f"{base_url}/api/jobs/{job_id}")
            job = response.json()
            status = job.get("status")
            
            if status == "completed":
                print(f"[OK] Generation complete! Reward: {job.get('overall_reward', 0):.2f}/10")
                print(f"     HTML: {len(job.get('generated_html', ''))} chars")
                print(f"     CSS:  {len(job.get('generated_css', ''))} chars")
                print(f"     JS:   {len(job.get('generated_js', ''))} chars")
                break
            
            await asyncio.sleep(1)
            waited += 1
        
        if waited >= max_wait:
            print(f"[TIMEOUT] Generation took too long")
            return
        
        # Test preview endpoint
        print(f"\n[TEST] Fetching preview HTML...")
        response = await client.get(f"{base_url}/preview/{job_id}")
        
        if response.status_code != 200:
            print(f"[FAIL] Preview fetch failed: {response.status_code}")
            print(response.text[:500])
            return
        
        html_content = response.text
        
        # Check for required elements
        checks = {
            "HTML starts correctly": html_content.startswith("<!DOCTYPE html") or html_content.startswith("<html"),
            "CSS injected": "<style>" in html_content,
            "Contains body": "<body" in html_content,
            "Contains script": "<script>" in html_content,
            "Has content": len(html_content) > 500,
        }
        
        print("[OK] Preview HTML response received")
        print(f"     Response size: {len(html_content)} chars")
        
        for check, passed in checks.items():
            status = "✓" if passed else "✗"
            print(f"     {status} {check}")
        
        if all(checks.values()):
            print("\n[COMPLETE] Preview endpoint working correctly!")
            print(f"\nPreview URL: http://localhost:8000/preview/{job_id}")
            print("Open in browser to see rendered website")
        else:
            print("\n[FAIL] Some checks failed")
            print("\nFirst 1000 chars of response:")
            print(html_content[:1000])

if __name__ == "__main__":
    asyncio.run(test_preview())

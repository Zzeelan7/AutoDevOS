#!/usr/bin/env python3
"""Test that LLM generation works without fallback template"""
import asyncio
import aiohttp
import json
import time

async def test_code_generation():
    """Test LLM code generation"""
    
    # Create a job with a simple prompt
    prompt = "Create a modern dark theme portfolio website with a hero section, project gallery, and contact form"
    
    print("[TEST] Creating job with prompt...")
    print(f"[PROMPT] {prompt[:100]}...")
    
    async with aiohttp.ClientSession() as session:
        # 1. Create job
        res = await session.post(
            "http://127.0.0.1:8000/api/jobs",
            json={"prompt": prompt}
        )
        
        if res.status != 200:
            print(f"[ERROR] Failed to create job: {res.status}")
            return
        
        job_data = await res.json()
        job_id = job_data.get("jobId")
        print(f"[SUCCESS] Job created: {job_id}")
        
        # 2. Connect to WebSocket and wait for generation
        print(f"[TEST] Connecting to WebSocket...")
        uri = f"ws://127.0.0.1:8000/ws/{job_id}"
        
        try:
            async with session.ws_connect(uri) as ws:
                # Collect events
                events = []
                error_occurred = False
                
                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        try:
                            event = json.loads(msg.data)
                            events.append(event)
                            
                            # Print event
                            event_type = event.get("type", "unknown")
                            if event_type == "error":
                                print(f"[ERROR] {event.get('message', 'Unknown error')}")
                                error_occurred = True
                            elif event_type == "event":
                                print(f"[EVENT] {event.get('message', '')}")
                                if "code_stats" in event:
                                    stats = event["code_stats"]
                                    print(f"       HTML: {stats['html_chars']} chars")
                                    print(f"       CSS:  {stats['css_chars']} chars")
                                    print(f"       JS:   {stats['js_chars']} chars")
                            elif event_type == "complete":
                                print(f"[COMPLETE] Job finished!")
                                job = event.get("job", {})
                                reward = job.get("overall_reward", 0)
                                print(f"           Reward: {reward:.2f}/10")
                                
                                # Get actual generated code from preview
                                await asyncio.sleep(0.5)
                                preview_res = await session.get(
                                    f"http://127.0.0.1:8000/api/jobs/{job_id}/preview"
                                )
                                if preview_res.status == 200:
                                    preview = await preview_res.json()
                                    html = preview.get("html", "")
                                    
                                    # Check if it's the fallback template
                                    if prompt[:50] in html[:200]:
                                        print("[WARNING] Prompt text found in HTML - might be fallback template")
                                    
                                    # Check for actual content
                                    if "<!DOCTYPE html>" in html:
                                        print("[SUCCESS] Real HTML generated!")
                                        # Print first 200 chars
                                        print(f"[PREVIEW] {html[:200]}...")
                                    else:
                                        print("[ERROR] No valid HTML in preview")
                                
                                break
                        except json.JSONDecodeError:
                            print(f"[ERROR] Failed to parse WebSocket message: {msg.data}")
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        print(f"[ERROR] WebSocket error: {ws.exception()}")
                        break
                    elif msg.type == aiohttp.WSMsgType.CLOSED:
                        print(f"[INFO] WebSocket closed")
                        break
        
        except Exception as e:
            print(f"[ERROR] WebSocket connection failed: {e}")

if __name__ == "__main__":
    print("[TEST] Starting LLM generation test...")
    print("[INFO] Testing that NO fallback template is used\n")
    asyncio.run(test_code_generation())
    print("\n[TEST] Complete!")

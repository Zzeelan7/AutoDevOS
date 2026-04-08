#!/usr/bin/env python3
"""Watch job completion and measure time"""
import asyncio
import httpx
import time
from datetime import datetime
import sys

# Fix encoding issues on Windows
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def watch_job_completion(job_id='ab7d2466'):
    base_url = 'http://localhost:8000'
    
    start_time = time.time()
    start_dt = datetime.now()
    
    print(f'\n⏱️  TIMING JOB COMPLETION')
    print(f'{"="*70}')
    print(f'Job ID: {job_id}')
    print(f'Start Time: {start_dt.strftime("%H:%M:%S")}')
    print(f'{"="*70}\n')
    
    async with httpx.AsyncClient(timeout=180.0) as client:
        last_status = None
        last_iteration = None
        check_count = 0
        
        while True:
            try:
                response = await client.get(f'{base_url}/api/jobs/{job_id}')
                if response.status_code == 200:
                    data = response.json()
                    status = data.get('status')
                    iteration = data.get('current_iteration')
                    reward = data.get('overall_reward', 0)
                    elapsed = time.time() - start_time
                    check_count += 1
                    
                    # Print status changes
                    if status != last_status or iteration != last_iteration:
                        print(f'[{elapsed:6.1f}s | Poll #{check_count:3d}] Status: {status:10s} | Iter: {iteration}/3 | Reward: {reward:.2f}')
                        last_status = status
                        last_iteration = iteration
                    
                    # Check if completed
                    if status == 'completed':
                        elapsed = time.time() - start_time
                        minutes = int(elapsed // 60)
                        seconds = elapsed % 60
                        print(f'\n{"="*70}')
                        print(f'✅ JOB COMPLETED')
                        print(f'Total Time: {elapsed:.1f} seconds ({minutes}m {seconds:.0f}s)')
                        print(f'Total Polls: {check_count}')
                        print(f'Final Status: {status}')
                        print(f'Final Reward: {reward:.2f}/10')
                        print(f'{"="*70}\n')
                        break
                    elif status == 'failed':
                        error = data.get('error_message', 'Unknown error')
                        elapsed = time.time() - start_time
                        print(f'\n❌ JOB FAILED after {elapsed:.1f}s')
                        print(f'Error: {error}')
                        break
                    
                    # Poll every 2 seconds
                    await asyncio.sleep(2)
            except Exception as e:
                print(f'Error checking job: {e}')
                await asyncio.sleep(2)

if __name__ == '__main__':
    asyncio.run(watch_job_completion())

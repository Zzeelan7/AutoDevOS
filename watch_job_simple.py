#!/usr/bin/env python3
"""Watch job completion"""
import asyncio
import httpx
import time
from datetime import datetime
import sys

async def watch_job(job_id='a5acebb6'):
    base_url = 'http://localhost:8000'
    
    start_time = time.time()
    start_dt = datetime.now()
    
    print(f'\nTIMING JOB COMPLETION')
    print(f'{"="*70}')
    print(f'Job ID: {job_id}')
    print(f'Start Time: {start_dt.strftime("%H:%M:%S")}')
    print(f'{"="*70}\n')
    
    async with httpx.AsyncClient(timeout=180.0) as client:
        last_status = None
        check_count = 0
        
        while True:
            try:
                response = await client.get(f'{base_url}/api/jobs/{job_id}')
                if response.status_code == 200:
                    data = response.json()
                    status = data.get('status')
                    reward = data.get('overall_reward', 0)
                    elapsed = time.time() - start_time
                    check_count += 1
                    
                    if status != last_status:
                        print(f'[{elapsed:6.1f}s | Poll #{check_count:3d}] Status: {status:10s} | Reward: {reward:.2f}')
                        last_status = status
                    
                    if status == 'completed':
                        elapsed = time.time() - start_time
                        minutes = int(elapsed // 60)
                        seconds = elapsed % 60
                        print(f'\n{"="*70}')
                        print(f'[SUCCESS] JOB COMPLETED')
                        print(f'Total Time: {elapsed:.1f} seconds ({minutes}m {seconds:.0f}s)')
                        print(f'Total Polls: {check_count}')
                        print(f'Final Reward: {reward:.2f}/10')
                        print(f'{"="*70}\n')
                        break
                    elif status == 'failed':
                        error = data.get('error_message', 'Unknown error')
                        elapsed = time.time() - start_time
                        print(f'\n[FAILED] after {elapsed:.1f}s: {error}')
                        break
                    
                    await asyncio.sleep(2)
            except Exception as e:
                print(f'Error: {e}')
                await asyncio.sleep(2)

if __name__ == '__main__':
    import sys
    job_id = sys.argv[1] if len(sys.argv) > 1 else 'a5acebb6'
    asyncio.run(watch_job(job_id))

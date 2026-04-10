import asyncio
import httpx
import sys

async def check_servers():
    """Check if both servers are responding"""
    
    print("Waiting for servers to start (checking every 2 seconds for 30s)...")
    print()
    
    backend_url = "http://localhost:8000/docs"
    frontend_url = "http://localhost:3000"
    
    for attempt in range(15):
        try:
            async with httpx.AsyncClient(timeout=2) as client:
                # Check backend
                try:
                    resp = await client.get(backend_url)
                    if resp.status_code == 200:
                        print(f"✓ Backend (8000): READY")
                except:
                    print(f"• Backend (8000): Starting... {attempt+1}/15")
                
                # Check frontend
                try:
                    resp = await client.get(frontend_url)
                    if resp.status_code == 200:
                        print(f"✓ Frontend (3000): READY")
                except:
                    print(f"• Frontend (3000): Starting... {attempt+1}/15")
                    
        except Exception as e:
            pass
        
        await asyncio.sleep(2)
    
    print()
    print("Access your application at: http://localhost:3000")

asyncio.run(check_servers())

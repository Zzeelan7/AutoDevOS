#!/usr/bin/env python3
import asyncio
import sys
sys.path.insert(0, 'backend')
from llm_generator import generate_production_code

async def test():
    try:
        print('[TEST] Testing LLM generation with llama3...')
        code = await generate_production_code('Create a simple website')
        if code.get('html') and len(code['html']) > 50:
            print(f'[SUCCESS] Generated {len(code["html"])} chars of HTML')
            print(f'[SUCCESS] Generated {len(code["css"])} chars of CSS')
            print(f'[SUCCESS] Generated {len(code["js"])} chars of JS')
            print(f'[PREVIEW HTML]:\n{code["html"][:300]}...\n')
        else:
            print('[FAILED] No valid code generated')
            print(f'HTML length: {len(code.get("html", ""))}')
            print(f'CSS length: {len(code.get("css", ""))}')
            print(f'JS length: {len(code.get("js", ""))}')
    except Exception as e:
        print(f'[ERROR] {e}')
        import traceback
        traceback.print_exc()

asyncio.run(test())

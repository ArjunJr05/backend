import httpx
import time
from typing import Optional, Dict, Any

async def call_team_endpoint(endpoint_url: str, payload: Dict[str, Any], timeout: int = 5, max_retries: int = 1) -> Optional[Dict[str, Any]]:
    for attempt in range(max_retries + 1):
        try:
            start_time = time.time()
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(endpoint_url, json=payload)
                latency = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    result = response.json()
                    result['latency_ms'] = latency
                    return result
                else:
                    if attempt == max_retries:
                        return None
        except httpx.TimeoutException:
            if attempt == max_retries:
                return None
        except Exception as e:
            if attempt == max_retries:
                return None
    
    return None

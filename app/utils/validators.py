import httpx
from typing import Tuple

async def validate_endpoint(url: str) -> Tuple[bool, str]:
    if not url.startswith("https://") and not url.startswith("http://"):
        return False, "Endpoint must use HTTP or HTTPS protocol"
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(url, json={"inputs": [{"test": 1}]})
            if response.status_code in [200, 201]:
                return True, "Endpoint is reachable"
            elif response.status_code == 405:
                response = await client.get(url)
                if response.status_code == 200:
                    return True, "Endpoint is reachable"
                else:
                    return False, f"Endpoint returned status code {response.status_code}"
            else:
                return False, f"Endpoint returned status code {response.status_code}"
    except httpx.TimeoutException:
        return False, "Endpoint request timed out"
    except httpx.RequestError as e:
        return False, f"Cannot reach endpoint: {str(e)}"
    except Exception as e:
        return False, f"Validation error: {str(e)}"

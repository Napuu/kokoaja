from fastapi import HTTPException, Request
from config import get_ip_whitelist

async def check_ip_is_allowed(request: Request):
    allowed_ips = get_ip_whitelist()
    client_ip = request.headers.get('x-real-ip', request.client.host)
    if client_ip not in allowed_ips:
        raise HTTPException(status_code=403, detail="🗿")
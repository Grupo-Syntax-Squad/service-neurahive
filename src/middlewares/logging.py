import time
import logging
from fastapi import Request

logger = logging.getLogger(__name__)


async def log_requests(request: Request, call_next):
    idem = f"{request.method} {request.url.path}"

    logger.info(f"🟡 {idem}")

    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000

    logger.info(f"🟢 {idem} - Response {response.status_code} in {process_time:.2f}ms")

    return response

from uuid import uuid4
from fastapi import Request

def get_trace_id(request: Request) -> str:
    """Return trace_id from headers or generate a new one."""
    return request.headers.get("X-Trace-Id", str(uuid4()))


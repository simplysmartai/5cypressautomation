---
description: Scaffold a new API endpoint for SMB automation
---

Create a new FastAPI endpoint following the 3-layer architecture.

## Requirements
$ARGUMENTS

## Instructions

1. **Check existing patterns** in `execution/` for similar endpoints
2. **Create Pydantic models** for request/response validation
3. **Implement the endpoint** with proper error handling
4. **Add to appropriate router** or create new module in `execution/`

## Architecture Rules

- Use async/await for all I/O operations
- Validate ALL inputs with Pydantic models
- Return structured JSON responses
- Log all operations with context
- Handle errors gracefully with HTTPException

## Template

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import logging

router = APIRouter()
log = logging.getLogger(__name__)

class RequestModel(BaseModel):
    # Define request fields with validation
    pass

class ResponseModel(BaseModel):
    # Define response fields
    status: str
    data: dict

@router.post("/api/endpoint", response_model=ResponseModel)
async def endpoint_name(request: RequestModel):
    """
    Endpoint description.
    """
    try:
        # 1. Validate business rules
        # 2. Call external APIs if needed
        # 3. Return response

        log.info("Operation completed", extra={"request_id": "..."})
        return ResponseModel(status="success", data={})

    except ExternalAPIError as e:
        log.error("External API failed", extra={"error": str(e)})
        raise HTTPException(status_code=502, detail="External service error")
    except Exception as e:
        log.exception("Unexpected error")
        raise HTTPException(status_code=500, detail="Internal error")
```

## After Creating

- [ ] Add endpoint to relevant directive in `directives/`
- [ ] Write tests with pytest
- [ ] Update `.claude/settings.local.json` if new script permissions needed

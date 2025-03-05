from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
from app.routes import loan_routes
from app.routes import pool_routes  # Import pool routes

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Initialize FastAPI app
app = FastAPI()

# ✅ Include API routes
app.include_router(loan_routes.router)
app.include_router(pool_routes.router, prefix="/pool")  

# ✅ CORS Configuration (if required)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to ABSecure Backend"}

# ✅ Improved Exception Handling (Returns JSON Instead of Plain Text)
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.error(f"HTTP Exception at {request.url}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code},
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception at {request.url}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "detail": str(exc)},
    )

"""
# Changes Implemented after first review:
1. **Replaced plain text error responses with structured JSON** for consistent API responses.
2. **Integrated logging for exception handling**, improving debugging and issue tracking.
3. **Enhanced error handling logic**:
   - Captures general exceptions and logs them appropriately.
   - Logs the request URL for better traceability.
4. **Ensured uniform response structure** across all endpoints for API reliability.
"""

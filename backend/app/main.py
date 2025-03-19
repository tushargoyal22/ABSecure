from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
from app.routes import loan_routes
from app.routes import pool_routes  # Import pool routes
from app.config.database import initialize_default_thresholds
from app.services.celery_worker import check_cpi_spike

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# ✅ Include API routes
@app.on_event("startup")
def startup_event():
    initialize_default_thresholds()

@app.get("/")
def read_root():
    return {"message": "Macro Notification System Running"}

@app.post("/trigger-cpi-check")
def trigger_cpi_check(background_tasks: BackgroundTasks):
    # This adds the Celery task to the queue
    background_tasks.add_task(check_cpi_spike.delay)
    return {"message": "CPI spike check triggered in background."}
app.include_router(loan_routes.router)
app.include_router(pool_routes.router, prefix="/pool")  

# CORS Configuration (if required)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to ABSecure Backend"}

# Improved Exception Handling (Returns JSON Instead of Plain Text)
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("ml.main:app", host="0.0.0.0", port=8000, reload=True)


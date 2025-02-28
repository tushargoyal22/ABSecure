from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.routes import loan_routes,pool_routes # ✅ Import both route modules


app = FastAPI()
app.include_router(pool_routes.router, prefix="/pool")
# 🔹 Allow frontend access (Update if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to ["http://localhost:3000"] if using a frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Include API routes
app.include_router(loan_routes.router)


@app.get("/")
async def root():
    return {"message": "Welcome to ABSecure Backend"}

# ✅ Handle HTTP exceptions properly
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    print(f"HTTP Exception: {exc.detail}")  # Debugging print
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)

# ✅ Handle validation errors (e.g., invalid input)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(f"Validation Error: {exc.errors()}")  # Debugging print
    return PlainTextResponse(str(exc), status_code=400)

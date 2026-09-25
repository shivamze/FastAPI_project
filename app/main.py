from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from app.db.database import SessionLocal
from app.modules.auth.router import router as auth_router

app = FastAPI(
    title="Authentication check",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # Update with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}



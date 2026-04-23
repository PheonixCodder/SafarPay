from fastapi import FastAPI
from auth.api.router import router as auth_router
from sp.core.observability.logging import setup_logging

app = FastAPI(title="SafarPay Auth Service")

# Setup logging
setup_logging()

# Include auth routes
app.include_router(auth_router)

@app.get("/")
def health_check():
    return {"status": "ok", "service": "auth"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="[IP_ADDRESS]", port=8000, reload=True)

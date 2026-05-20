import uvicorn
from fastapi_app.app.core.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "fastapi_app.app.main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=True
    )
    
import uvicorn
from fastapi import FastAPI

from router import router as api_router

app = FastAPI()

app.include_router(api_router)

if __name__ == "__main__":
    import webbrowser

    webbrowser.open("http://127.0.0.1:8000/")
    uvicorn.run(app)

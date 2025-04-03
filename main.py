import uvicorn

from src.main.app import create_app

if __name__ == "__main__":
    app = create_app()
    uvicorn.run(app)

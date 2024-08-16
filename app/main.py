import os

import uvicorn
from fastapi import FastAPI

from app.routers import router


def create_app() -> FastAPI:
    """
        Function to create the FastAPI application instance with configured middleware and routers.

        Returns:
            FastAPI: FastAPI application instance.

        Usage:
            This function is called to instantiate the FastAPI application with middleware and routers configured.
            It includes middleware setup, router inclusion, and lifecycle event handling.
        """
    app_ = FastAPI(
        title="Face detect app",
        description="Face detect app"
    )

    app_.include_router(router)

    return app_


app = create_app()


@app.get("/")
def root():
    return {"message": "Hello ROOT !!!"}


if __name__ == "__main__":
    os.system('alembic upgrade head')
    uvicorn.run("main:app", port=8000, host="0.0.0.0", reload=True)

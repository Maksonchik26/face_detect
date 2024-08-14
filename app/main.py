import os

import uvicorn
from fastapi import FastAPI, APIRouter

# fromrouters.projects import router as projects_router
# from app.routers.users import router as users_router


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
        title="Bot Farm",
        description="Bot Farm Application"
    )

    router = APIRouter()
    # router.include_router(projects_router)
    # router.include_router(users_router)

    app_.include_router(router)

    return app_


app = create_app()


@app.get("/")
def root():
    return {"message": "Hello ROOT !!!"}


if __name__ == "__main__":
    os.system('alembic upgrade head')
    uvicorn.run("main:app", port=8000, host="0.0.0.0", reload=True)

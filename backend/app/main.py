from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import close_mongo_connection, connect_to_mongo
from app.crud.user import user_crud
from app.routes import auth_router
from app.routes.events import router as events_router
from app.routes.payments import router as payments_router
from app.routes.expenditures import router as expenditures_router
from app.routes.notifications import router as notifications_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    await user_crud.create_admin_user()
    yield
    await close_mongo_connection()


app = FastAPI(
    title="New Year's Event API",
    description="API for organizing New Year's events",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(events_router)
app.include_router(payments_router)
app.include_router(expenditures_router)
app.include_router(notifications_router)


@app.get("/")
async def root():
    return {"message": "New Year's Event API is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

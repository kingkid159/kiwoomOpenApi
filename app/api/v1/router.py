from fastapi import APIRouter
from .test import router as test_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(test_router)

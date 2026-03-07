from fastapi import APIRouter
from api.opportunities import router as opportunities_router
from api.profile import router as profile_router
from api.proposals import router as proposals_router
from auth.auth_router import router as auth_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(opportunities_router)
api_router.include_router(profile_router)
api_router.include_router(proposals_router)

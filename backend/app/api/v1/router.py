from fastapi import APIRouter

from app.api.v1 import auth, xray, predict, doctors, reports, chat

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(xray.router)
api_router.include_router(predict.router)
api_router.include_router(doctors.router)
api_router.include_router(reports.router)
api_router.include_router(chat.router)

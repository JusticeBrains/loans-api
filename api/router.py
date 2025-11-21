from fastapi import APIRouter

from api.v1.company import router as company_router
from api.v1.user import router as user_router
from api.v1.employee import router as employee_router
from api.v1.period_year import router as period_year_router
from api.v1.periods import router as period_router

api_router = APIRouter()

api_router.include_router(company_router, prefix="/v1")
api_router.include_router(user_router, prefix="/v1")
api_router.include_router(employee_router, prefix="/v1")
api_router.include_router(period_year_router, prefix="/v1")
api_router.include_router(period_router, prefix="/v1")


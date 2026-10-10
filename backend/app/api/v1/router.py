from fastapi import APIRouter

from app.api.v1.endpoints import webhook, employees, departments, tasks, payroll

api_router = APIRouter()

api_router.include_router(webhook.router, prefix="/webhook", tags=["WhatsApp Webhook"])
api_router.include_router(departments.router, prefix="/departments", tags=["Departments"])
api_router.include_router(employees.router, prefix="/employees", tags=["Employees"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["Daily Tasks"])
api_router.include_router(payroll.router, prefix="/payroll", tags=["Payroll"])

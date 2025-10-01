from app.api.company import router as company_router
from app.api.control_materials import router as control_materials_router
from app.api.nfc import router as nfc_router
from app.api.objects import router as objects_router
from app.api.remarks import router as remarks_router
from app.api.users import router as users_router
from app.api.violations import router as violations_router

all_routers = [
    users_router,
    objects_router,
    company_router,
    nfc_router,
    remarks_router,
    violations_router,
    control_materials_router
]
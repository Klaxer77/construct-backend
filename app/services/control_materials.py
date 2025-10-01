

import uuid

from fastapi import UploadFile

from app.dependencies.unitofwork import UnitOfWork
from app.exceptions.control_materials import CategoryMaterialNotFoundExc
from app.exceptions.objects import ObjectNotFoundExc
from app.models.control_materials import CategoriesMaterials
from app.models.objects import Objects
from app.repositories.api import ApiRepository
from app.schemas.control_materials import (
    SCreateMaterials,
    SLlmResponse,
    SMaterials,
    SMaterialsList,
    SMaterialsListDetail,
)


class MaterialService:
    
    async def list_materials_detail(
        self,
        uow: UnitOfWork,
        object_id: uuid.UUID,
        category_id: uuid.UUID
    ) -> list[SMaterialsListDetail]:
        async with uow:
            check_category: CategoriesMaterials | None = await uow.categories_materials.find_one_or_none(
                id=category_id
            )
            if not check_category:
                raise CategoryMaterialNotFoundExc
            
            check_object: Objects | None = await uow.objects.find_one_or_none(id=object_id)
            if not check_object:
                raise ObjectNotFoundExc
            
            materials = await uow.materials.find_all(
                object_id=object_id,
                category_id=category_id
            )
            return [SMaterialsListDetail.model_validate(m) for m in materials]
    
    async def list_materials(
        self, 
        uow: UnitOfWork
    ) -> list[SMaterialsList]:
        async with uow:
            categories = await uow.categories_materials.list_materials()
            if not categories:
                raise CategoryMaterialNotFoundExc
            
            return [SMaterialsList.model_validate(c) for c in categories]
    
    async def create_material(
        self,
        uow: UnitOfWork,
        user_data: SCreateMaterials,
        category_id: uuid.UUID,
        object_id: uuid.UUID,
    ) -> SMaterials:
        async with uow:
            check_category: CategoriesMaterials | None = await uow.categories_materials.find_one_or_none(
                id=category_id
            )
            if not check_category:
                raise CategoryMaterialNotFoundExc
            
            check_object: Objects | None = await uow.objects.find_one_or_none(id=object_id)
            if not check_object:
                raise ObjectNotFoundExc
            
            new_material = await uow.materials.insert_by_data({
                "sender": user_data.sender,
                "date": user_data.date,
                "request_number": user_data.request_number,
                "receiver": user_data.receiver,
                "item_name": user_data.item_name,
                "size": user_data.size,
                "quantity": user_data.quantity,
                "net_weight": user_data.net_weight,
                "gross_weight": user_data.gross_weight,
                "volume": user_data.volume,
                "carrier": user_data.carrier,
                "vehicle": user_data.vehicle,
                "object_id": object_id,
                "category_id": category_id
            })
            
            await uow.commit()
            return SMaterials.model_validate(new_material)
    
    async def llm(self, upload_file: UploadFile) -> SLlmResponse:
        return await ApiRepository().llm_query(upload_file)
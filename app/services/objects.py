import uuid

from fastapi import UploadFile

from app.dependencies.unitofwork import UnitOfWork
from app.exceptions.company import CompanyNotFoundExc
from app.exceptions.objects import (
    ActNotFoundExc,
    ActObjectIsExistsExc,
    ActObjectIsNotExistsExc,
    ObjectActNotRequiredExc,
    ObjectCategoryNotFoundExc,
    ObjectNotFoundExc,
)
from app.exceptions.users import ContractorNotFoundExc, InvalidCoordsUserExc
from app.models.company import Company
from app.models.enums import (
    ActObjectsActionEnum,
    ActStatusEnum,
    ObjectStatusesEnum,
    ObjectTypeEnum,
    ObjectTypeFilter,
    UserRoleEnum,
)
from app.models.objects import Acts, Objects, ObjectsCategories
from app.models.users import User
from app.schemas.objects import (
    SActCreate,
    SActDetail,
    SActSuccessCreated,
    SCategoriesObjects,
    SCountObjects,
    SObject,
    SObjectCreate,
    SObjectDetail,
    SObjectGEOCheck,
    SObjectsList,
    SObjectUpdated,
)
from app.utils.create_geom import create_geom_from_coords
from app.utils.generate_nfc_uid import generate_nfc_uid
from app.utils.generate_using_id import using_id
from app.utils.nfc_label import number_to_label_nfc


class ObjectsService:
    
    async def check_geo(
        self, 
        uow: UnitOfWork, 
        object_id: uuid.UUID, 
        latitude: float,
        longitude: float
        ) -> SObjectGEOCheck:
        async with uow:
            check_object: Objects | None = await uow.objects.find_one_or_none(id=object_id)
            if not check_object:
                raise ObjectNotFoundExc
            
            validate_coords: bool = await uow.users.validate_coords(check_object.id, latitude, longitude)
            if not validate_coords:
                raise InvalidCoordsUserExc
            
            return SObjectGEOCheck.model_validate({"result": "success"})
    
    async def object_check_list(self, uow: UnitOfWork, object_id: uuid.UUID) -> SActDetail:
        async with uow:
            check_object: Objects | None = await uow.objects.find_one_or_none(id=object_id)
            if not check_object:
                raise ObjectNotFoundExc
            
            act = await uow.acts.get_act_detail(object_id)
            if not act:
                raise ActObjectIsNotExistsExc

            dto = SActDetail.model_validate(act).model_dump()
            dto["responsible_fio"] = act.object.responsible_user.fio if act.object and act.object.responsible_user else None #noqa
            dto["contractor_title"] = act.object.contractor.title if act.object and act.object.contractor else None #noqa
            
            return SActDetail(**dto)
    
    async def get_object_detail(self, uow: UnitOfWork, object_id: uuid.UUID) -> SObjectDetail:
        async with uow:
            check_object: Objects | None = await uow.objects.find_one_or_none(id=object_id)
            if not check_object:
                raise ObjectNotFoundExc
            
            object_detail = await uow.objects.get_object_detail(object_id)
            return SObjectDetail.model_validate(object_detail)
    
    async def send_file(
        self, 
        uow: UnitOfWork, 
        object_id: uuid.UUID,
        upload_file: UploadFile
        ) -> SActSuccessCreated:
        async with uow:
            check_object: Objects | None = await uow.objects.find_one_or_none(id=object_id)
            if not check_object:
                raise ObjectNotFoundExc
            
            if check_object.status != ObjectStatusesEnum.ACT:
                raise ObjectActNotRequiredExc
            
            get_act: Acts = await uow.acts.find_one_or_none(object_id=object_id)
            
            path_folder = "objects/files"
            ext = upload_file.filename.split(".")[-1].lower()
            object_name = f"{path_folder}/{uuid.uuid4()}.{ext}"
            url = await uow.images.upload_any_file(upload_file, object_name)
            
            await uow.objects.update_by_filter({
                "status": ObjectStatusesEnum.PLAN,
                "object_type": ObjectTypeEnum.ACTIVE
            }, id=object_id)
            updated_act = await uow.acts.update_by_filter({
                "file_url": url,
            }, id=get_act.id)
            
            await uow.commit()
            return SActSuccessCreated.model_validate(updated_act)
    
    async def act_change(
        self, 
        uow: UnitOfWork, 
        object_id: uuid.UUID, 
        action: ActObjectsActionEnum
        ) -> SObjectUpdated:
        async with uow:
            check_object: Objects | None = await uow.objects.find_one_or_none(id=object_id)
            if not check_object:
                raise ObjectNotFoundExc
            
            get_act: Acts | None = await uow.acts.find_one_or_none(object_id=check_object.id)
            if not get_act:
                raise ActNotFoundExc
            
            if action == ActObjectsActionEnum.ACCEPT:
                updated_object = await uow.objects.update_by_filter({
                    "status": ObjectStatusesEnum.ACT,
                    "object_type": ObjectTypeEnum.ACT_OPENING           
                }, id=object_id)
                await uow.acts.update_by_filter({
                    "status": ActStatusEnum.VERIFIED
                }, object_id=object_id)
                
            elif action == ActObjectsActionEnum.DENY:
                ...
                
            await uow.commit()
            return SObjectUpdated.model_validate(updated_object)
    
    async def activate_object_check_list(
        self, 
        uow: UnitOfWork, 
        object_id: uuid.UUID,
        user_data: SActCreate
    ) -> SActSuccessCreated:
        async with uow:
            check_object: Objects | None = await uow.objects.find_one_or_none(id=object_id)
            if not check_object:
                raise ObjectNotFoundExc
            
            check_contractor: User | None = await uow.users.find_one_or_none(
                id=user_data.contractor_id,
                role=UserRoleEnum.CONTRACTOR
            )
            if not check_contractor:
                raise ContractorNotFoundExc
            
            check_exists_act = await uow.acts.find_one_or_none(object_id=object_id)
            if check_exists_act:
                raise ActObjectIsExistsExc
            
            await uow.objects.update_by_filter(
                {
                    "responsible_user_id": user_data.contractor_id,
                    "contractor_id": check_contractor.company_id,
                    "object_type": ObjectTypeEnum.AGREEMENT
                },
                id=object_id
            )
            
            new_act: Acts = await uow.acts.insert_by_data({
                "object_id": check_object.id,
                "date_verification": user_data.date_verification,
                "status": ActStatusEnum.NOT_VERIFIED
            })
            
            for doc in user_data.act_docx:
                await uow.act_document.insert_by_data({
                    "act_id": new_act.id,
                    "code": doc.code,
                    "title": doc.title,
                    "status": doc.status,
                    "description": doc.description
                })
            
            await uow.commit()
            return SActSuccessCreated.model_validate(new_act)
    
    async def get_all_objects_by_filter(
        self, 
        uow: UnitOfWork, 
        filter_by: ObjectTypeFilter,
        company_id: uuid.UUID,
        user: User
        ) -> list[SObjectsList]:
        async with uow:
            check_company: Company | None = await uow.company.find_one_or_none(id=company_id)
            if not check_company:
                raise CompanyNotFoundExc
            
            objects = await uow.objects.get_all_objects_by_filter(filter_by, company_id, user)
            return [SObjectsList.model_validate(o) for o in objects]

    
    async def get_all_categories_objects(self, uow: UnitOfWork) -> list[SCategoriesObjects]:
        async with uow:
            categories = await uow.objects_categories.find_all()
            return [SCategoriesObjects.model_validate(category) for category in categories]
    
    async def count_objects(
        self, 
        uow: UnitOfWork, 
        category_id: uuid.UUID | None,
        filter_by: ObjectTypeEnum,
        company_id: uuid.UUID,
        user: User
        ) -> SCountObjects:
        async with uow:
            check_category: ObjectsCategories | None = await uow.objects_categories.find_one_or_none(id=category_id)
            if not check_category:
                raise ObjectCategoryNotFoundExc
            
            check_company: Company | None = await uow.company.find_one_or_none(id=company_id)
            if not check_company:
                raise CompanyNotFoundExc
            
            count = await uow.objects.count_objects(category_id, filter_by, company_id, user)
            return SCountObjects.model_validate({"count": count})
    
    async def create(
        self, 
        uow: UnitOfWork, 
        user_data: SObjectCreate, 
        user: User,
        company_id: uuid.UUID
        ) -> SObject:
        async with uow:
            check_company: Company | None = await uow.company.find_one_or_none(id=company_id)
            if not check_company:
                raise CompanyNotFoundExc
            
            geom = create_geom_from_coords(user_data.coords)
            new_object: Objects = await uow.objects.insert_by_data(
                {
                    "using_id": using_id(),
                    "company_id": company_id,
                    "general_info": user_data.general_info,
                    "title": user_data.title,
                    "city": user_data.city,
                    "responsible_user_id": None,
                    "contractor_id": None,
                    "category_id": "e03fc0b0-5202-4864-97c1-4e59530d6841",
                    "date_delivery_verification": user_data.date_delivery_verification,
                    "start_date": user_data.start_date,
                    "status": ObjectStatusesEnum.KNOWN,
                    "object_type": ObjectTypeEnum.NOT_ACTIVE,
                    "geom": geom
                }
            )
            
            # ИСКЛЮЧИТЕЛЬНО В РАМКАХ ХАКАТОНА
            # -------
            count = await uow.object_nfc.count_by_filter(object_id=new_object.id)
            label = number_to_label_nfc(count + 1)
            await uow.object_nfc.insert_by_data({
                "nfc_uid": generate_nfc_uid(),
                "object_id": new_object.id,
                "label": label
            })
            # -------
            
            await uow.commit()
            return SObject(
                id=new_object.id,
                using_id=new_object.using_id,
                status=new_object.status,
                object_type=new_object.object_type,
                created_at=new_object.created_at,
                updated_at=new_object.updated_at,
                general_info=new_object.general_info,
                title=user_data.title,
                city=user_data.city,
                date_delivery_verification=user_data.date_delivery_verification,
                start_date=user_data.start_date,
                coords=user_data.coords
            )
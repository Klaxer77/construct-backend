

import uuid
from decimal import ROUND_HALF_UP, Decimal

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.dependencies.unitofwork import UnitOfWork
from app.models.control_materials import ListOfWorks, ProgressWork, StageProgressWork, StageProgressWorkPhoto
from app.models.enums import (
    ListOfWorksStatusEnum,
    StageProgressWorkMainStatusEnum,
    StageProgressWorkSecondStatusEnum,
    WorkActionEnum,
)
from app.repositories.api import ApiRepository
from app.schemas.control_materials import (
    SCreateDeliveryWorks,
    SCreateMaterials,
    SDetailStageWork,
    SLlmResponse,
    SMaterials,
    SMaterialsWorkCreate,
    SMaterialsWorkRead,
    SPhotosListOfWorks,
    SProgressObject,
    SWorkAction,
    SWorkBegin,
    SWorkChangeStatus,
    SWorkDelivery,
)


class MaterialService:
    
    async def object_progress(self, uow: UnitOfWork, object_id: uuid.UUID) -> SProgressObject:
        async with uow:
            progress: int = await uow.progress_work.progress(object_id)
            return SProgressObject.model_validate({"progress": progress})
    
    async def list_materials_stage(
        self, 
        uow: UnitOfWork, 
        stage_progress_work_id: uuid.UUID
        ) -> list[SMaterials]:
        async with uow:
            meterials = await uow.materials.find_all_by_filter(
                stage_progress_work_id=stage_progress_work_id
                )
            return [SMaterials.model_validate(m) for m in meterials]
    
    async def detail_stage_work(
        self, 
        uow: UnitOfWork, 
        stage_progress_work_id: uuid.UUID
    ) -> SDetailStageWork:
        async with uow:
            stage = await uow.stage_progress_work.detail(stage_progress_work_id)

            total_volume = Decimal(stage.get("volume") or 1)
            list_of_works = stage.get("list_of_works", [])

            passed_volume = Decimal(
                sum(lw["volume"] for lw in list_of_works if lw["status"] == ListOfWorksStatusEnum.PASSED)
            )

            percent = passed_volume / total_volume
            percent = max(Decimal("0.0"), min(percent, Decimal("1.0"))).quantize(
                Decimal("0.0001"), rounding=ROUND_HALF_UP
            )

            volume_percent = (total_volume * percent).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            volume_percent = int(volume_percent)

            data = {
                "id": stage.get("id"),
                "stage": stage.get("stage"),
                "percent": stage.get("percent"),
                "title": stage.get("title"),
                "status_main": stage.get("status_main"),
                "status_second": stage.get("status_second"),
                "date_from": stage.get("date_from"),
                "date_to": stage.get("date_to"),
                "kpgz": stage.get("kpgz"),
                "volume": stage.get("volume"),
                "unit": stage.get("unit"),
                "volume_percent": volume_percent,
                "list_of_works": stage.get("list_of_works"),
            }

            return SDetailStageWork.model_validate(data)
    
    async def action_work(
        self, 
        uow: UnitOfWork,
        list_of_work_id: uuid.UUID,
        user_data: SWorkChangeStatus,
    ) -> SWorkAction:
        async with uow:
            list_work: ListOfWorks | None = await uow.list_of_works.find_one_or_none(id=list_of_work_id)

            stage: StageProgressWork | None = await uow.stage_progress_work.find_one_or_none(
                id=list_work.stage_progress_work_id
            )

            if user_data.action == WorkActionEnum.ACCEPT:
                list_work.status = ListOfWorksStatusEnum.PASSED
            elif user_data.action == WorkActionEnum.DENY:
                list_work.status = ListOfWorksStatusEnum.VERIFICATION_REJECTED

            uow.session.add(list_work)
            await uow.session.flush()

            list_of_works = await uow.list_of_works.find_all(stage_progress_work_id=stage.id)
            total_volume = stage.volume or 1
            passed_volume = sum(lw.volume for lw in list_of_works if lw.status == ListOfWorksStatusEnum.PASSED)

            stage.percent = Decimal(passed_volume) / Decimal(total_volume)
            stage.percent = max(Decimal("0.0"), min(stage.percent, Decimal("1.0"))).quantize(
                Decimal("0.0001"), rounding=ROUND_HALF_UP
            )

            if passed_volume >= total_volume:
                stage.status_main = StageProgressWorkMainStatusEnum.PASSED
            else:
                stage.status_main = StageProgressWorkMainStatusEnum.WORK

            if user_data.action == WorkActionEnum.ACCEPT:
                stage.status_second = StageProgressWorkSecondStatusEnum.NONE
            elif user_data.action == WorkActionEnum.DENY:
                stage.status_second = StageProgressWorkSecondStatusEnum.VERIFICATION_REJECTED
            else:
                if any(lw.status == ListOfWorksStatusEnum.AWAITING_VERIFICATION for lw in list_of_works):
                    stage.status_second = StageProgressWorkSecondStatusEnum.AWAITING_VERIFICATION
                else:
                    stage.status_second = StageProgressWorkSecondStatusEnum.NONE

            uow.session.add(stage)
            await uow.session.flush()

            progress_work: ProgressWork | None = await uow.progress_work.find_one_or_none(id=stage.progress_work_id)
            if progress_work:
                stages = await uow.stage_progress_work.find_all(progress_work_id=progress_work.id)
                if stages:
                    avg_percent = sum([float(s.percent or 0) for s in stages]) / len(stages)
                    progress_work.percent = Decimal(avg_percent).quantize(Decimal("0.0001"))
                    uow.session.add(progress_work)

            await uow.commit()

            return SWorkAction.model_validate({"result": "success"})

    async def delivery_work(
        self,
        uow: UnitOfWork,
        work_data: SCreateDeliveryWorks,
        stage_progress_work_id: uuid.UUID,
        files: list[UploadFile] | None,
    ) -> SWorkDelivery:
        async with uow:
            
            check_progress_work: StageProgressWork = await uow.stage_progress_work.find_one_or_none(
                id=stage_progress_work_id
            )

            new_work = ListOfWorks(
                volume=work_data.volume,
                desc=work_data.desc,
                stage_progress_work_id=stage_progress_work_id,
                status=ListOfWorksStatusEnum.AWAITING_VERIFICATION
            )
            uow.session.add(new_work)
            await uow.session.flush()
            
            files_map = {file.filename: file for file in files} if files else {}

            photos = []

            for key in work_data.photos_keys:
                upload_file = files_map.get(key)
                if upload_file:
                    path_folder = "images/work_delivery"
                    ext = upload_file.filename.split(".")[-1].lower()
                    object_name = f"{path_folder}/{uuid.uuid4()}.{ext}"

                    url: str = await uow.images.upload_any_file(upload_file, object_name)

                    photo = StageProgressWorkPhoto(
                        list_of_works_id=new_work.id,
                        file_path=url,
                    )
                    uow.session.add(photo)
                    photos.append(photo)
                    
            await uow.stage_progress_work.update_by_filter(
                {
                    "status_second": StageProgressWorkSecondStatusEnum.AWAITING_VERIFICATION
                }, id=check_progress_work.id
            )

            await uow.commit()

            return SWorkDelivery(
                id=str(new_work.id),
                created_at=new_work.created_at,
                status=new_work.status,
                volume=new_work.volume,
                desc=new_work.desc,
                photos=[SPhotosListOfWorks(file_path=p.file_path) for p in photos],
            )
    
    async def begin_work(self, uow: UnitOfWork, stage_progress_work_id: uuid.UUID) -> SWorkBegin:
        async with uow:
            await uow.stage_progress_work.update_by_filter({
                "status_main": StageProgressWorkMainStatusEnum.WORK
            }, id=stage_progress_work_id)
            await uow.commit()
            return SWorkBegin.model_validate({"result": "success"})
    
    async def list_work(self, uow: UnitOfWork, object_id: uuid.UUID) -> list[SMaterialsWorkRead]:
        async with uow:
            works = await uow.progress_work.list_work(object_id)
            return [SMaterialsWorkRead.model_validate(w) for w in works]
    
    async def create_work(self, uow: UnitOfWork, object_id: uuid.UUID, user_data: SMaterialsWorkCreate):
        async with uow:
            new_work = ProgressWork(
                title=user_data.title,
                date_from=user_data.date_from,
                date_to=user_data.date_to,
                object_id=object_id,
                percent=0.00,
                stages=[
                    StageProgressWork(
                        title=stage.title,
                        date_from=stage.date_from,
                        date_to=stage.date_to,
                        kpgz=stage.kpgz,
                        volume=stage.volume,
                        unit=stage.unit,
                        percent=0.00,
                        status_main="not_started",
                        status_second="none",
                    )
                    for stage in user_data.stages
                ],
            )

            uow.session.add(new_work)
            await uow.commit()

            result = await uow.session.execute(
                select(ProgressWork)
                .options(selectinload(ProgressWork.stages))
                .where(ProgressWork.id == new_work.id)
            )
            new_work_full = result.scalar_one()

            return SMaterialsWorkRead.model_validate(new_work_full)
    
    async def create_material(
        self,
        uow: UnitOfWork,
        user_data: SCreateMaterials,
        stage_progress_work_id: uuid.UUID,
    ) -> SMaterials:
        async with uow:
            
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
                "stage_progress_work_id": stage_progress_work_id
            })
            
            await uow.commit()
            return SMaterials.model_validate(new_material)
    
    async def llm(self, upload_file: UploadFile) -> SLlmResponse:
        return await ApiRepository().llm_query(upload_file)
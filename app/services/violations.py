import uuid
from datetime import UTC, datetime

from fastapi import UploadFile

from app.dependencies.unitofwork import UnitOfWork
from app.exceptions.objects import ObjectNotFoundExc
from app.exceptions.users import InvalidCoordsUserExc, UserIsNotActivatedExc
from app.exceptions.violations import ViolationAnswerIsExistsExc, ViolationNotFoundExc
from app.models.enums import ViolationActionEnum, ViolationStatusEnum
from app.models.objects import Objects
from app.models.users import User, UserObjectAccess
from app.models.violations import ViolationAnswer, ViolationAnswerFile, ViolationPhoto, Violations, ViolationsItem
from app.schemas.violations import (
    SVialationAnswer,
    SVialationAnswerCreate,
    SVialationAnswerFile,
    SViolation,
    SViolationChangedSuccess,
    SViolationChangeStatus,
    SViolationCreate,
    SViolationsDetail,
    SViolationsList,
)


class ViolationsService:
    
    async def answer_vialation(
        self,
        uow: UnitOfWork,
        vialation_data: SVialationAnswerCreate,
        files: list[UploadFile],
        vialation_id: uuid.UUID,
        object_id: uuid.UUID,
        user: User,
    ) -> SVialationAnswer:
        async with uow:
            check_object: Objects | None = await uow.objects.find_one_or_none(id=object_id)
            if not check_object:
                raise ObjectNotFoundExc

            check_vialation: ViolationsItem | None = await uow.violations_item.find_one_or_none(id=vialation_id)
            if not check_vialation:
                raise ViolationNotFoundExc
            
            check_vialation_answer: ViolationAnswer | None = await uow.violation_answer.find_one_or_none(
                violation_item_id=vialation_id
                )
            if check_vialation_answer:
                raise ViolationAnswerIsExistsExc

            check_user_object: UserObjectAccess | None = await uow.user_object_access.find_one_or_none(
                user_id=user.id,
                object_id=object_id
            )
            if not check_user_object or not check_user_object.is_active:
                raise UserIsNotActivatedExc

            if (
                check_user_object.access_expires_at 
                and check_user_object.access_expires_at < datetime.now(UTC)
            ):
                await uow.user_object_access.delete_by_filter(user_id=user.id, object_id=object_id)
                raise UserIsNotActivatedExc

            new_answer = ViolationAnswer(
                violation_item_id=vialation_id,
                comment=vialation_data.comment
            )
            uow.session.add(new_answer)
            await uow.session.flush()

            saved_files: list[ViolationAnswerFile] = []
            if files:
                path_folder = "images/violation_answers"

                for upload_file in files:
                    ext = upload_file.filename.split(".")[-1].lower()
                    object_name = f"{path_folder}/{uuid.uuid4()}.{ext}"

                    url: str = await uow.images.upload_any_file(upload_file, object_name)

                    file_record = ViolationAnswerFile(
                        answer_id=new_answer.id,
                        file_path=url
                    )
                    uow.session.add(file_record)
                    saved_files.append(file_record)

            await uow.commit()

            return SVialationAnswer(
                id=new_answer.id,
                comment=new_answer.comment,
                created_at=new_answer.created_at,
                files=[SVialationAnswerFile(file_path=f.file_path) for f in saved_files]
            )
    
    async def violations_change_status(
        self, 
        uow: UnitOfWork, 
        violation_id: uuid.UUID,
        user_data: SViolationChangeStatus
    ) -> SViolationChangedSuccess:
        async with uow:
            check_violation: ViolationsItem | None = await uow.violations_item.find_one_or_none(id=violation_id)
            if not check_violation:
                raise ViolationNotFoundExc

            if user_data.action == ViolationActionEnum.ACCEPT:
                await uow.violations_item.update_many_by_filter(
                    {"status": ViolationStatusEnum.FIXED},
                    id=violation_id
                )
            elif user_data.action == ViolationActionEnum.DENY:
                await uow.violations_item.update_many_by_filter(
                    {"status": ViolationStatusEnum.NOT_FIXED},
                    id=violation_id
                )

            all_items: list[ViolationsItem] = await uow.violations_item.find_all(
                violations_id=check_violation.violations_id
            )

            statuses = {item.status for item in all_items}

            if statuses == {ViolationStatusEnum.FIXED}:
                new_status = ViolationStatusEnum.FIXED
            elif ViolationStatusEnum.REVIEW in statuses:
                new_status = ViolationStatusEnum.REVIEW
            elif ViolationStatusEnum.NOT_FIXED in statuses:
                new_status = ViolationStatusEnum.NOT_FIXED
            else:
                new_status = check_violation.violations.status

            await uow.violations.update_many_by_filter(
                {"status": new_status},
                id=check_violation.violations_id
            )

            await uow.commit()
            return SViolationChangedSuccess.model_validate({"result": "success"})
    
    async def get_violations_detail(
        self,
        uow: UnitOfWork,
        violation_id: uuid.UUID
    ) -> SViolationsDetail:
        async with uow:
            check_violation: Violations | None = await uow.violations.find_one_or_none(id=violation_id)
            if not check_violation:
                raise ViolationNotFoundExc
                
            violations = await uow.violations.get_violations_detail(violation_id)
            return SViolationsDetail.model_validate(violations)
    
    async def get_all_violations(
        self, uow: UnitOfWork, object_id: uuid.UUID
    ) -> list[SViolationsList]:
        async with uow:
            check_object = await uow.objects.find_one_or_none(id=object_id)
            if not check_object:
                raise ObjectNotFoundExc

            violations_rows = await uow.violations.get_all_violations(object_id)

            user_ids = [r.responsible_user_id for r in violations_rows if r.responsible_user_id]
            users = {}
            if user_ids:
                rows = await uow.users.get_users_by_ids(user_ids)
                users = {u.id: u.fio for u in rows}

            return [
                SViolationsList(
                    id=row.id,
                    object_name=row.object_name,
                    responsible_user_name=users.get(row.responsible_user_id),
                    status=row.status,
                    date_violation=row.date_violation,
                    expiration_date=row.expiration_date
                )
                for row in violations_rows
            ]
    
    async def create_violation(
        self,
        uow: UnitOfWork,
        data: list[SViolationCreate],
        files: list[UploadFile],
        object_id: uuid.UUID,
        latitude: float,
        longitude: float,
        user: User,
    ):
        async with uow:
            check_object: Objects | None = await uow.objects.find_one_or_none(id=object_id)
            if not check_object:
                raise ObjectNotFoundExc
            
            check_user_object: UserObjectAccess | None = await uow.user_object_access.find_one_or_none(
                user_id=user.id,
                object_id=object_id
            )
            if not check_user_object:
                raise UserIsNotActivatedExc
            
            if check_user_object.is_active == False:  #noqa
                raise UserIsNotActivatedExc
            
            if check_user_object.access_expires_at and check_user_object.access_expires_at < datetime.now(UTC):
                await uow.user_object_access.delete_by_filter(user_id=user.id, object_id=object_id)
                raise UserIsNotActivatedExc
            
            validate_coords: bool = await uow.users.validate_coords(check_object.id, latitude, longitude)
            if not validate_coords:
                raise InvalidCoordsUserExc

            created: list[ViolationsItem] = []

            now = datetime.now(UTC)
            earliest_expiration = min((d.expiration_date for d in data), default=now)
            violations_container = Violations(
                responsible_user_id=check_object.responsible_user_id,
                date_violation=now,
                expiration_date=earliest_expiration,
                status=ViolationStatusEnum.NOT_FIXED
            )
            uow.session.add(violations_container)
            await uow.session.flush()

            files_map = {file.filename: file for file in files} if files else {}

            for violation_data in data:
                violation_item = ViolationsItem(
                    responsible_user_id=check_object.responsible_user_id,
                    object_id=object_id,
                    violations=violation_data.violations,
                    name_regulatory_docx=violation_data.name_regulatory_docx,
                    expiration_date=violation_data.expiration_date,
                    date_violation=datetime.now(UTC),
                    comment=violation_data.comment,
                    status=ViolationStatusEnum.NOT_FIXED,
                    violations_id=violations_container.id,
                )
                uow.session.add(violation_item)
                created.append(violation_item)

                for key in violation_data.photos_keys:
                    upload_file = files_map.get(key)
                    if upload_file:
                        path_folder = "images/violations"
                        ext = upload_file.filename.split(".")[-1].lower()
                        object_name = f"{path_folder}/{uuid.uuid4()}.{ext}"

                        url: str = await uow.images.upload_any_file(upload_file, object_name)

                        photo = ViolationPhoto(file_path=url, violation_item=violation_item)
                        uow.session.add(photo)

            await uow.commit()

            return [SViolation.model_validate(r) for r in created]




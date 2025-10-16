import uuid
from datetime import UTC, datetime

from fastapi import UploadFile

from app.dependencies.unitofwork import UnitOfWork
from app.exceptions.objects import ObjectNotFoundExc
from app.exceptions.remarks import RemarkAnswerIsExistsExc, RemarkNotFoundExc
from app.exceptions.users import UserIsNotActivatedExc
from app.models.enums import RemarkActionEnum, RemarkStatusEnum
from app.models.objects import Objects
from app.models.remarks import RemarkAnswer, RemarkAnswerFile, RemarkPhoto, Remarks, RemarksItem
from app.models.users import User, UserObjectAccess
from app.schemas.remarks import (
    SRemark,
    SRemarkAnswer,
    SRemarkAnswerCreate,
    SRemarkAnswerFile,
    SRemarkChangedSuccess,
    SRemarkChangeStatus,
    SRemarkCreate,
    SRemarksDetail,
    SRemarksList,
)


class RemarksService:
    
    async def answer_remarks(
        self,
        uow: UnitOfWork,
        remark_data: SRemarkAnswerCreate,
        files: list[UploadFile],
        remark_id: uuid.UUID,
        object_id: uuid.UUID,
        user: User,
    ) -> SRemarkAnswer:
        async with uow:
            check_object: Objects | None = await uow.objects.find_one_or_none(id=object_id)
            if not check_object:
                raise ObjectNotFoundExc

            check_remark: RemarksItem | None = await uow.remarks_item.find_one_or_none(id=remark_id)
            if not check_remark:
                raise RemarkNotFoundExc
            
            check_remark_answer: RemarkAnswer | None = await uow.remark_answer.find_one_or_none(
                remark_item_id=remark_id
                )
            if check_remark_answer:
                raise RemarkAnswerIsExistsExc

            new_answer = RemarkAnswer(
                remark_item_id=remark_id,
                comment=remark_data.comment
            )
            uow.session.add(new_answer)
            await uow.session.flush()

            saved_files: list[RemarkAnswerFile] = []
            if files:
                path_folder = "images/remark_answers"

                for upload_file in files:
                    ext = upload_file.filename.split(".")[-1].lower()
                    object_name = f"{path_folder}/{uuid.uuid4()}.{ext}"

                    url: str = await uow.images.upload_any_file(upload_file, object_name)

                    file_record = RemarkAnswerFile(
                        answer_id=new_answer.id,
                        file_path=url
                    )
                    uow.session.add(file_record)
                    saved_files.append(file_record)

            await uow.remarks_item.update_by_filter({
                "status": RemarkStatusEnum.REVIEW
            }, id=remark_id)
            await uow.commit()

            return SRemarkAnswer(
                id=new_answer.id,
                comment=new_answer.comment,
                created_at=new_answer.created_at,
                files=[SRemarkAnswerFile(file_path=f.file_path) for f in saved_files]
            )

    
    async def remarks_change_status(
        self, 
        uow: UnitOfWork, 
        remark_id: uuid.UUID,
        user_data: SRemarkChangeStatus
    ) -> SRemarkChangedSuccess:
        async with uow:
            check_remark: RemarksItem | None = await uow.remarks_item.find_one_or_none(id=remark_id)
            if not check_remark:
                raise RemarkNotFoundExc

            if user_data.action == RemarkActionEnum.ACCEPT:
                await uow.remarks_item.update_many_by_filter(
                    {"status": RemarkStatusEnum.FIXED},
                    id=remark_id
                )
            elif user_data.action == RemarkActionEnum.DENY:
                await uow.remarks_item.update_many_by_filter(
                    {"status": RemarkStatusEnum.NOT_FIXED},
                    id=remark_id
                )
                await uow.remark_answer.delete_by_filter(remark_item_id=remark_id)

            all_items: list[RemarksItem] = await uow.remarks_item.find_all(
                remarks_id=check_remark.remarks_id
            )

            statuses = {item.status for item in all_items}

            if statuses == {RemarkStatusEnum.FIXED}:
                new_status = RemarkStatusEnum.FIXED
            elif RemarkStatusEnum.REVIEW in statuses:
                new_status = RemarkStatusEnum.REVIEW
            elif RemarkStatusEnum.NOT_FIXED in statuses:
                new_status = RemarkStatusEnum.NOT_FIXED
            else:
                new_status = check_remark.remarks.status

            await uow.remarks.update_many_by_filter(
                {"status": new_status},
                id=check_remark.remarks_id
            )

            await uow.commit()
            return SRemarkChangedSuccess.model_validate({"result": "success"})
    
    async def get_remarks_detail(
        self,
        uow: UnitOfWork,
        remark_id: uuid.UUID
    ) -> SRemarksDetail:
        async with uow:
            check_remark: Remarks | None = await uow.remarks.find_one_or_none(id=remark_id)
            if not check_remark:
                raise RemarkNotFoundExc
                
            remarks = await uow.remarks.get_remarks_detail(remark_id)
            return SRemarksDetail.model_validate(remarks)
    
    async def get_all_remarks(
        self, uow: UnitOfWork, object_id: uuid.UUID
    ) -> list[SRemarksList]:
        async with uow:
            check_object = await uow.objects.find_one_or_none(id=object_id)
            if not check_object:
                raise ObjectNotFoundExc

            remarks_rows = await uow.remarks.get_all_remarks(object_id)

            user_ids = [r.responsible_user_id for r in remarks_rows if r.responsible_user_id]
            users = {}
            if user_ids:
                rows = await uow.users.get_users_by_ids(user_ids)
                users = {u.id: u.fio for u in rows}

            return [
                SRemarksList(
                    id=row.id,
                    object_name=row.object_name,
                    responsible_user_name=users.get(row.responsible_user_id),
                    status=row.status,
                    date_remark=row.date_remark,
                    expiration_date=row.expiration_date
                )
                for row in remarks_rows
            ]
    
    async def create_remark(
        self,
        uow: UnitOfWork,
        data: list[SRemarkCreate],
        files: list[UploadFile],
        object_id: uuid.UUID,
        user: User,
        latitude: float,
        longitude: float
    ):
        async with uow:
            check_object: Objects | None = await uow.objects.find_one_or_none(id=object_id)
            if not check_object:
                raise ObjectNotFoundExc

            coords_valid = not (latitude == 0.00 and longitude == 0.00)

            validate_coords = False
            if coords_valid:
                validate_coords = await uow.users.validate_coords(
                    check_object.id, latitude, longitude
                )

            if not validate_coords:
                check_user_object: UserObjectAccess | None = await uow.user_object_access.find_one_or_none(
                    user_id=user.id,
                    object_id=object_id
                )
                if not check_user_object:
                    raise UserIsNotActivatedExc

                if check_user_object.is_active is False:
                    raise UserIsNotActivatedExc

                if (
                    check_user_object.access_expires_at
                    and check_user_object.access_expires_at < datetime.now(UTC)
                ):
                    await uow.user_object_access.delete_by_filter(
                        user_id=user.id,
                        object_id=object_id
                    )
                    raise UserIsNotActivatedExc

            created: list[RemarksItem] = []

            now = datetime.now(UTC)
            earliest_expiration = min((d.expiration_date for d in data), default=now)
            remarks_container = Remarks(
                responsible_user_id=check_object.responsible_user_id,
                date_remark=now,
                expiration_date=earliest_expiration,
                status=RemarkStatusEnum.NOT_FIXED
            )
            uow.session.add(remarks_container)
            await uow.session.flush()

            files_map = {file.filename: file for file in files} if files else {}

            for remark_data in data:
                remark_item = RemarksItem(
                    responsible_user_id=check_object.responsible_user_id,
                    object_id=object_id,
                    violations=remark_data.violations,
                    name_regulatory_docx=remark_data.name_regulatory_docx,
                    expiration_date=remark_data.expiration_date,
                    date_remark=datetime.now(UTC),
                    comment=remark_data.comment,
                    status=RemarkStatusEnum.NOT_FIXED,
                    remarks_id=remarks_container.id,
                )
                uow.session.add(remark_item)
                created.append(remark_item)

                for key in remark_data.photos_keys:
                    upload_file = files_map.get(key)
                    if upload_file:
                        path_folder = "images/remarks"
                        ext = upload_file.filename.split(".")[-1].lower()
                        object_name = f"{path_folder}/{uuid.uuid4()}.{ext}"

                        url: str = await uow.images.upload_any_file(upload_file, object_name)

                        photo = RemarkPhoto(file_path=url, remark_item=remark_item)
                        uow.session.add(photo)

            await uow.commit()

            return [SRemark.model_validate(r) for r in created]




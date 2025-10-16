import uuid
from collections import defaultdict
from datetime import UTC, datetime, timedelta

from app.config.main import settings
from app.dependencies.unitofwork import UnitOfWork
from app.exceptions.nfc import NFCLabelIsExistsExc, NFCNotFoundExc, ObjectNFCUidIsExistsExc
from app.exceptions.objects import ObjectNotFoundExc, UserObjectSessionNotFoundExc
from app.models.nfc import ObjectNFC
from app.models.objects import Objects
from app.models.users import User, UserObjectAccess
from app.schemas.nfc import (
    SNFCADD,
    NFCLabelScan,
    SNFCChange,
    SNFCCreate,
    SNFCDelete,
    SNFCHistoryDate,
    SNFCHistoryObject,
    SNFCHistoryObjectList,
    SNFCSessionTerminate,
    SNFCVerify,
)
from app.utils.nfc_label import number_to_label_nfc


class NFCService:
    
    async def change_nfc(
        self, 
        uow: UnitOfWork, 
        nfc_id: uuid.UUID, 
        object_id: uuid.UUID,
        user_data: SNFCChange
        ) -> SNFCChange:
        async with uow:
            check_nfc: ObjectNFC | None = await uow.object_nfc.find_one_or_none(
                id=nfc_id
            )
            if not check_nfc:
                raise NFCNotFoundExc
            
            check_label: ObjectNFC = await uow.object_nfc.find_one_or_none(
                label=user_data.label,
                object_id=object_id
                )
            if check_label:
                raise NFCLabelIsExistsExc
            
            updated_nfc: ObjectNFC = await uow.object_nfc.update_by_filter({
                "label": user_data.label
            }, id=nfc_id)
            
            await uow.commit()
            return SNFCChange.model_validate(updated_nfc)
    
    async def session_nfc(self, uow: UnitOfWork, object_id: uuid.UUID, user: User) -> SNFCSessionTerminate:
        async with uow:
            check_user_object: UserObjectAccess | None = await uow.user_object_access.find_one_or_none(
                user_id=user.id,
                object_id=object_id
            )
            if not check_user_object:
                raise UserObjectSessionNotFoundExc
            
            await uow.user_object_access.delete_by_filter(user_id=user.id, object_id=object_id)
            await uow.commit()
            return SNFCSessionTerminate.model_validate({"result": "success"})
    
    async def delete_nfc(
        self,
        uow: UnitOfWork,
        nfc_id: uuid.UUID
    ) -> SNFCDelete:
        async with uow:
            check_nfc: ObjectNFC | None = await uow.object_nfc.find_one_or_none(
                id=nfc_id
            )
            if not check_nfc:
                raise NFCNotFoundExc
            
            await uow.object_nfc.delete_by_filter(id=nfc_id)
            await uow.commit()
            
            return SNFCDelete.model_validate({"result": "success"})
    
    async def all_nfc(
        self, 
        uow: UnitOfWork,
        object_id: uuid.UUID
        ) -> list[SNFCHistoryObjectList]:
        async with uow:
            check_object: Objects | None = await uow.objects.find_one_or_none(id=object_id)
            if not check_object:
                raise ObjectNotFoundExc
                
            nfc = await uow.object_nfc.find_all_by_filter(object_id=object_id)
            return [SNFCHistoryObjectList.model_validate(n) for n in nfc]
        
    async def history_nfc_all(self, uow: UnitOfWork, user: User) -> list[SNFCHistoryObject]:
        async with uow:
            rows = await uow.object_nfc.history_all(user)

            grouped = defaultdict(lambda: {"title": "", "dates": defaultdict(list)})

            for row in rows:
                using_id = row["using_id"]
                scan_date = row["scan_date"]

                grouped[using_id]["title"] = row["title"]
                grouped[using_id]["dates"][scan_date].append(
                    NFCLabelScan(label=row["label"], scanned_at=row["scanned_at"])
                )

            history = [
                SNFCHistoryObject(
                    title=data["title"],
                    using_id=using_id,
                    data=[
                        SNFCHistoryDate(date=scan_date, scans=scans)
                        for scan_date, scans in sorted(dates.items(), reverse=True)
                    ]
                )
                for using_id, data in grouped.items()
                for dates in [data["dates"]]
            ]

            return history


    
    async def history_nfc(self, uow: UnitOfWork, object_id: uuid.UUID, user: User) -> list[SNFCHistoryObject]:
        async with uow:
            rows = await uow.object_nfc.history(user, object_id)

            grouped = defaultdict(lambda: {"title": "", "dates": defaultdict(list)})

            for row in rows:
                using_id = row["using_id"]
                scan_date = row["scan_date"]

                grouped[using_id]["title"] = row["title"]
                grouped[using_id]["dates"][scan_date].append(
                    NFCLabelScan(label=row["label"], scanned_at=row["scanned_at"])
                )

            history = [
                SNFCHistoryObject(
                    title=data["title"],
                    using_id=using_id,
                    data=[
                        SNFCHistoryDate(date=scan_date, scans=scans)
                        for scan_date, scans in sorted(dates.items(), reverse=True)
                    ]
                )
                for using_id, data in grouped.items()
                for dates in [data["dates"]]
            ]

            return history

    
    async def verify_nfc(
        self,
        uow: UnitOfWork,
        user_data: SNFCCreate,
        user: User,
        object_id: uuid.UUID
    ) -> SNFCVerify:
        async with uow:
            check_nfc: ObjectNFC | None = await uow.object_nfc.find_one_or_none(
                nfc_uid=user_data.nfc_uid,
                object_id=object_id
            )
            if not check_nfc:
                raise NFCNotFoundExc
            
            check_user_object: UserObjectAccess | None = await uow.user_object_access.find_one_or_none(
                user_id=user.id,
                object_id=object_id
            )
            
            access_expires_at = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_EXPIRES_AT_MIN)
            
            if check_user_object:
                await uow.user_object_access.update_by_filter({
                    "user_id": user.id,
                    "object_id": object_id,
                    "is_active": True,
                    "access_expires_at": access_expires_at
                }, user_id=user.id, object_id=object_id)
            else:
                await uow.user_object_access.insert_by_data({
                    "user_id": user.id,
                    "object_id": object_id,
                    "is_active": True,
                    "access_expires_at": access_expires_at
                })
            
            await uow.history_object_nfc.insert_by_data({
                "nfc_id": check_nfc.id,
                "user_id": user.id
            })
            await uow.commit()
            return SNFCVerify.model_validate({"access_expires_at": access_expires_at})
    
    async def create(
        self, 
        uow: UnitOfWork, 
        user_data: SNFCCreate,
        object_id: uuid.UUID,
        user: User
    ) -> SNFCADD:
        async with uow:
            check_object: Objects | None = await uow.objects.find_one_or_none(id=object_id)
            if not check_object:
                raise ObjectNotFoundExc
            
            check_nfc_uid: ObjectNFC | None = await uow.object_nfc.find_one_or_none(
                nfc_uid=user_data.nfc_uid
                )
            if check_nfc_uid:
                raise ObjectNFCUidIsExistsExc
            
            count = await uow.object_nfc.count_by_filter(object_id=object_id)
            label = number_to_label_nfc(count + 1)
    
            new_nfc: ObjectNFC = await uow.object_nfc.insert_by_data({
                "nfc_uid": user_data.nfc_uid,
                "object_id": object_id,
                "label": label
            })
            
            await uow.history_object_nfc.insert_by_data({
                "nfc_id": new_nfc.id,
                "user_id": user.id
            })
            
            await uow.commit()
            return SNFCADD.model_validate(new_nfc)
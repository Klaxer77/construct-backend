from typing import Annotated

from fastapi import Depends

from app.config.database import async_session_maker
from app.repositories.company import CompanyRepository
from app.repositories.control_materials import CategoriesMaterialsRepository, MaterialsRepository
from app.repositories.images import ImagesRepository
from app.repositories.nfc import HistoryObjectNFCRepository, ObjectNFCRepository
from app.repositories.objects import (
    ActDocumentRepository,
    ActsRepository,
    ObjectsCategoriesRepository,
    ObjectsRepository,
)
from app.repositories.remarks import (
    RemarkAnswerFileRepository,
    RemarkAnswerRepository,
    RemarkPhotoRepository,
    RemarksItemRepository,
    RemarksRepository,
)
from app.repositories.users import RefreshSessionRepository, UserObjectAccessRepository, UsersRepository
from app.repositories.violations import (
    ViolationAnswerFileRepository,
    ViolationAnswerRepository,
    ViolationPhotoRepository,
    ViolationsItemRepository,
    ViolationsRepository,
)


class UnitOfWork:
    def __init__(self):
        self.session_factory = async_session_maker

    async def __aenter__(self):
        self.session = self.session_factory()

        # Repositories
        self.images = ImagesRepository()
        self.users = UsersRepository(self.session)
        self.refresh_session = RefreshSessionRepository(self.session)
        self.company = CompanyRepository(self.session)
        self.objects = ObjectsRepository(self.session)
        self.objects_categories = ObjectsCategoriesRepository(self.session)
        self.acts = ActsRepository(self.session)
        self.act_document = ActDocumentRepository(self.session)
        self.object_nfc = ObjectNFCRepository(self.session)
        self.history_object_nfc = HistoryObjectNFCRepository(self.session)
        self.remark_photo = RemarkPhotoRepository(self.session)
        self.remarks_item = RemarksItemRepository(self.session)
        self.remarks = RemarksRepository(self.session)
        self.violation_photo = ViolationPhotoRepository(self.session)
        self.violations_item = ViolationsItemRepository(self.session)
        self.violations = ViolationsRepository(self.session)
        self.categories_materials = CategoriesMaterialsRepository(self.session)
        self.materials = MaterialsRepository(self.session)
        self.user_object_access = UserObjectAccessRepository(self.session)
        self.remark_answer = RemarkAnswerRepository(self.session)
        self.remark_answer_file = RemarkAnswerFileRepository(self.session)
        self.violation_answer = ViolationAnswerRepository(self.session)
        self.violation_answer_file = ViolationAnswerFileRepository(self.session)
        
    async def __aexit__(self, *args):
        await self.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()


UOWDep = Annotated[UnitOfWork, Depends(UnitOfWork)]



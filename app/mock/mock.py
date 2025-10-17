import json
import time

from sqlalchemy import insert

from app.config.database import async_session_maker
from app.config.main import settings
from app.models.company import Company
from app.models.objects import ObjectsCategories
from app.models.users import User
from app.repositories.company import CompanyRepository
from app.repositories.objects import ObjectsCategoriesRepository
from app.repositories.users import UsersRepository


def open_mock_json(model: str):
    with open(f"./app/mock/mock_{model}.json", encoding="utf-8") as file:
        return json.load(file)


async def init_app():
    time.sleep(1)
    
    companies = open_mock_json("companies")
    
    if settings.MODE == "PROD":
        users = open_mock_json("users")
    else:
        users = open_mock_json("users_dev")
        
    object_categories = open_mock_json("object_categories")

    async with async_session_maker() as session:
        for company in companies:
            find_company = await CompanyRepository(session).find_one_or_none(
                id=company["id"]
                )
            if not find_company:
                await session.execute(insert(Company).values(company))
                
        for user in users:
            find_user = await UsersRepository(session).find_one_or_none(
                id=user["id"]
                )
            if not find_user:
                await session.execute(insert(User).values(user))
                
        for object_category in object_categories:
            find_object_category = await ObjectsCategoriesRepository(session).find_one_or_none(
                id=object_category["id"]
                )
            if not find_object_category:
                await session.execute(insert(ObjectsCategories).values(object_category))
        
        await session.commit()
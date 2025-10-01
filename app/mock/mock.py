import json
import time
from datetime import datetime

from sqlalchemy import insert

from app.config.database import async_session_maker
from app.config.main import settings
from app.models.company import Company
from app.models.control_materials import CategoriesMaterials
from app.models.objects import ObjectsCategories
from app.models.users import User, UserObjectAccess
from app.repositories.company import CompanyRepository
from app.repositories.control_materials import CategoriesMaterialsRepository
from app.repositories.objects import ObjectsCategoriesRepository
from app.repositories.users import UserObjectAccessRepository, UsersRepository


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
    categories_materials = open_mock_json("categories_materials")
    
    if settings.MODE == "PROD":
        users_object_access = open_mock_json("users_object_access")
        
        for user_object_access in users_object_access:
            user_object_access["access_expires_at"] = datetime.strptime(user_object_access["access_expires_at"], "%Y-%m-%dT%H:%M:%S.%f%z") #noqa
    
    for category_material in categories_materials:
        category_material["date_from"] = datetime.strptime(category_material["date_from"], "%Y-%m-%dT%H:%M:%S.%f%z")
        category_material["date_to"] = datetime.strptime(category_material["date_to"], "%Y-%m-%dT%H:%M:%S.%f%z")

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
                
        for category_material in categories_materials:
            find_category_material = await CategoriesMaterialsRepository(session).find_one_or_none(
                id=category_material["id"]
                )
            if not find_category_material:
                await session.execute(insert(CategoriesMaterials).values(category_material))
        
        if settings.MODE == "PROD":        
            for user_object_access in users_object_access:
                find_user_object_access = await UserObjectAccessRepository(session).find_one_or_none(
                    id=user_object_access["id"]
                    )
                if not find_user_object_access:
                    await session.execute(insert(UserObjectAccess).values(user_object_access))
        
        await session.commit()
import httpx
from fastapi import UploadFile

from app.config.main import settings
from app.exceptions.api import LLMErrorExc
from app.schemas.control_materials import SLlmResponse


class ApiRepository:
    
    async def llm_query(self, upload_file: UploadFile) -> SLlmResponse:
        async with httpx.AsyncClient(timeout=90) as client:
            files = {
                "file": (upload_file.filename, upload_file.file, upload_file.content_type)
            }
            response = await client.post(settings.LLM_URL, files=files)
            result = response.json()
            print(result) #noqa

        if result.get("error"):
            raise LLMErrorExc

        response_model = SLlmResponse.model_validate(result)

        if response_model.llmResult:
            response_model.llmResult.replace_nulls()

            if all(v == "" for v in response_model.llmResult.__dict__.values()):
                raise LLMErrorExc

        return response_model

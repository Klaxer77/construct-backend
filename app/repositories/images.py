import io
import uuid

from fastapi import UploadFile
from PIL import Image, UnidentifiedImageError

from app.config.main import settings
from app.exceptions.bad_request import BadRequestException
from app.exceptions.files import FileLimitSizeExc
from app.exceptions.images import ImageLimitSizeExc
from app.utils.s3 import s3_client


class ImagesRepository:
    async def upload_image(self, file: UploadFile, object_name: str, width: int, height: int) -> str:
        """Загрузить файл в S3 и вернуть ссылку с расширением"""
        try:
            if file.size > 10485760:  # 10MB
                raise ImageLimitSizeExc

            image_data = await file.read()
            image = Image.open(io.BytesIO(image_data))

            img_buffer = io.BytesIO()

            if image.mode == "RGBA":
                image = image.resize((width, height), Image.Resampling.LANCZOS)
                image.save(img_buffer, format="PNG")
                ext = "png"
            else:
                image = image.convert("RGB")
                image = image.resize((width, height), Image.Resampling.LANCZOS)
                image.save(img_buffer, format="JPEG", quality=100)
                ext = "jpg"

            img_buffer.seek(0)

            if not object_name.endswith(f".{ext}"):
                object_name = f"{object_name}.{ext}"

            await s3_client.upload_file(img_buffer, object_name)

            return f"{settings.DOMAIN_S3}/{object_name}"

        except ImageLimitSizeExc:
            raise ImageLimitSizeExc

        except UnidentifiedImageError:
            raise BadRequestException("Unsupported image format")

        except Exception:
            raise BadRequestException("Unexpected error while uploading image")

            
    async def upload_images(
        self,
        files: list[UploadFile],
        folder_path: str,
        width: int,
        height: int
    ) -> list[str]:
        """Загрузка нескольких изображений"""
        urls = []
        for file in files:
            ext = file.filename.split(".")[-1].lower()
            object_name = f"{folder_path}/{uuid.uuid4()}.{ext}"
            url = await self.upload_image(file, object_name, width, height)
            urls.append(url)
        return urls
    
    async def upload_any_file(self, file: UploadFile, object_name: str) -> str:
        try:
            if file.size > 20485760:  # 20MB
                raise FileLimitSizeExc
            
            file_data = await file.read()
            file_buffer = io.BytesIO(file_data)

            await s3_client.upload_file(file_buffer, object_name)

            return f"{settings.DOMAIN_S3}/{object_name}"
        except Exception:
            raise BadRequestException("Unexpected error while uploading file")

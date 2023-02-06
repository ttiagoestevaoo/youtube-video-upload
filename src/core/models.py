from datetime import datetime
from pydantic import BaseModel
from fastapi import File


class VideoSnippet(BaseModel):
    title: str
    description: str


class VideoUpload(BaseModel):
    id: str
    snnipet: VideoSnippet
    media: bytes = File()

class VideoUploadResponse(BaseModel):
    id: str

from pydantic import BaseModel

from contracts.supported_langs import SupportedLangs


class UploadFunctionRequest(BaseModel):
    id: str
    lang: SupportedLangs
    version: str
    name: str
    dependencies: list[str]
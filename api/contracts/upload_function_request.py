from __future__ import annotations
from pydantic import BaseModel

from contracts.supported_langs import SupportedLangs

import uuid
import os
import json

class FunctionMetadata(BaseModel):
    id: str
    lang: SupportedLangs
    version: str
    name: str
    dependencies: list[str]
    folder_path: str
    str_dependencies: str
    tag: str

    @staticmethod
    def from_body(absolute_path: str , endpoint_inputs: str) -> FunctionMetadata:
        inputs = json.loads(endpoint_inputs)
        function_id = str(uuid.uuid4())[:8]
        folder_path = os.path.join(absolute_path, "functions", f"func-{function_id}")
        tag = f"{inputs["name"]}-{function_id}"

        return FunctionMetadata(
            id=function_id,
            **inputs,
            folder_path=folder_path,
            str_dependencies= " ".join(inputs["dependencies"]),
            tag=tag
        )

    @staticmethod
    def from_files(absolute_path: str ,function_id: str) -> FunctionMetadata:
        folder_path = os.path.join(absolute_path, "functions", f"func-{function_id}")
        metadata_file_path = os.path.join(folder_path, "metadata.json")
        with open(metadata_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    
        return FunctionMetadata(**data)


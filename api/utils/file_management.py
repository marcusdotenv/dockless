import os
import shutil

from fastapi import UploadFile

from contracts.upload_function_request import FunctionMetadata


async def __save_function_files(data: FunctionMetadata, file: UploadFile):
    os.makedirs(data.folder_path, exist_ok=True)

    function_file_name = f"function.{data.lang.value}"
    function_file_path = os.path.join(data.folder_path, function_file_name)
    
    with open(function_file_path, "wb") as f:
        f.write(await file.read())

    metadata_file_name = "metadata.json"
    metadata_file_path = os.path.join(data.folder_path, metadata_file_name)

    with open(metadata_file_path, "w") as f:
        f.write(data.model_dump_json(indent=4))


def __copy_base_management_files(absolute_path: str, destine_path: str):
    from_path = os.path.join(absolute_path, "functions", "base")

    for file in os.listdir(from_path):
        origin = os.path.join(from_path, file)
        destine = os.path.join(destine_path, file)

        if os.path.isfile(origin):
            shutil.copy(origin, destine)
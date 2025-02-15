from fastapi import FastAPI, Form, UploadFile

from contracts.upload_function_request import UploadFunctionRequest

import json
import os
import uuid
import shutil
import docker

app = FastAPI()
docker_client = docker.from_env()
absolute_path = os.path.dirname(os.path.abspath(__file__)) 

@app.post("/functions")
async def read_item(file: UploadFile, body: str = Form(...)):
    function_id = str(uuid.uuid4())[:8]
    data = UploadFunctionRequest(
        **{**json.loads(body), "id": function_id}
    )  
    
    new_function_folder_path = await __save_function_files(absolute_path=absolute_path, data=data, file=file )

    __copy_from_base(absolute_path=absolute_path, destine_path=new_function_folder_path)

    return {
        "id": function_id
    }

@app.post("/functions/{function_id}/start")
async def start(function_id: str):
    function_folder_path = os.path.join(absolute_path, "functions", f"func-{function_id}")
    metadata = __read_metadata_file(function_folder_path)

    function_dependencies = __build_function_dependencies(metadata.dependencies) if len(metadata.dependencies) > 0 else None

    docker_client.images.build(
        path=function_folder_path,
        buildargs={
            "FUNCTION_DEPENDENCIES": function_dependencies,
            "PY_VERSION": metadata.version
        },
        tag=metadata.name
    )
    
    docker_client.containers.run(metadata.name, detach=True, ports={'8001/tcp': 8001}) 



async def __save_function_files(absolute_path: str, data: UploadFunctionRequest, file: UploadFile) -> str:
    new_function_folder_path = os.path.join(absolute_path, "functions", f"func-{data.id}")
    os.makedirs(new_function_folder_path, exist_ok=True)

    function_file_name = f"function.{data.lang.value}"
    function_file_path = os.path.join(new_function_folder_path, function_file_name)
    
    with open(function_file_path, "wb") as f:
        f.write(await file.read())

    metadata_file_name = "metadata.json"
    metadata_file_path = os.path.join(new_function_folder_path, metadata_file_name)

    with open(metadata_file_path, "w") as f:
        f.write(data.model_dump_json(indent=4))

    return new_function_folder_path

def __read_metadata_file(file_path: str) -> UploadFunctionRequest:
    metadata_file_path = os.path.join(file_path, "metadata.json")
    with open(metadata_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    return UploadFunctionRequest(**data)

def __copy_from_base(absolute_path: str, destine_path: str):
    base_folder_path = os.path.join(absolute_path, "functions", "base")

    for file in os.listdir(base_folder_path):
        origin = os.path.join(base_folder_path, file)
        destine = os.path.join(destine_path, file)

        if os.path.isfile(origin):
            shutil.copy(origin, destine)

def __build_function_dependencies(dependencies: list[str]) -> str:
    return " ".join(dependencies)

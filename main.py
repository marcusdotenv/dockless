from fastapi import FastAPI, Form, UploadFile, BackgroundTasks

from contracts.upload_function_request import FunctionMetadata
from utils.docker_container_provider import DockerContainerProvider
from utils.file_management import __copy_base_management_files, __save_function_files
import os

app = FastAPI()
absolute_path = os.path.dirname(os.path.abspath(__file__)) 
docker = DockerContainerProvider()

@app.post("/functions")
async def read_item(file: UploadFile, body: str = Form(...)):
    data = FunctionMetadata.from_body(absolute_path=absolute_path, endpoint_inputs=body)
    
    await __save_function_files(data=data, file=file)
    __copy_base_management_files(absolute_path=absolute_path, destine_path=data.folder_path)

    return { "id": data.id }

@app.post("/functions/{function_id}/start")
def start(function_id: str, backgrounTask: BackgroundTasks):
    metadata = FunctionMetadata.from_files(absolute_path=absolute_path, function_id=function_id)
    
    backgrounTask.add_task(docker.build_and_run, metadata)

    return {}
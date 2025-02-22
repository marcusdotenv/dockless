from fastapi import FastAPI, Form, Response, UploadFile, BackgroundTasks

from utils.redis_container_manager import RedisContainerManager
from utils.nginx_conf_handler import NginxConfHandler
from contracts.upload_function_request import FunctionMetadata
from utils.docker_container_provider import DockerContainerProvider
from utils.file_management import __copy_base_management_files, __save_function_files
import os
import json

app = FastAPI()
absolute_path = os.path.dirname(os.path.abspath(__file__)) 
nginx_handler = NginxConfHandler()
docker = DockerContainerProvider()
container_manager = RedisContainerManager(on_container_expire=docker.pause)
running_servers = {}

@app.post("/functions")
async def new_function(file: UploadFile, backgrounTask: BackgroundTasks, body: str = Form(...)):
    data = FunctionMetadata.from_body(absolute_path=absolute_path, endpoint_inputs=body)
    
    await __save_function_files(data=data, file=file)
    __copy_base_management_files(absolute_path=absolute_path, destine_path=data.folder_path)
    
    backgrounTask.add_task(__monitore_building, data)

    return { "function": data }

@app.post("/functions/{function_id}/execute")
def execute(function_id: str):
    in_building = container_manager.in_building(function_id=function_id)

    if in_building: 
        return Response(status_code=403, content=json.dumps({"error": "Container in build"}))

    is_running = container_manager.is_running(function_id=function_id)


    if not is_running: 
        __handle_not_running_container(function_id=function_id)

    metadata = container_manager.get_data(function_id=function_id)

    #container_manager.registry_request(function_id=function_id)
    return nginx_handler.request(path=metadata.tag)

def __monitore_building(metadata: FunctionMetadata):
    container_manager.save(metadata=metadata)
    docker.build(metadata=metadata)
    container_manager.to_idle(function_id=metadata.id)

def __handle_not_running_container(function_id: str):
    metadata = FunctionMetadata.from_files(absolute_path=absolute_path, function_id=function_id)
    container_manager.to_running(function_id=function_id)
    docker.run(metadata=metadata)
    nginx_handler.add(metadata=metadata)
    nginx_container = docker.get_container("nginx-proxy")
    nginx_container.exec_run("nginx -s reload")

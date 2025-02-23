from fastapi import FastAPI, Form, Response, UploadFile, BackgroundTasks
import os
import json

from utils.redis_container_manager import RedisContainerManager
from utils.nginx_conf_handler import NginxConfHandler
from contracts.upload_function_request import FunctionMetadata
from utils.docker_container_provider import DockerContainerProvider
from utils.file_management import __copy_base_management_files, __save_function_files


app = FastAPI()
absolute_path = os.path.dirname(os.path.abspath(__file__))
nginx_handler = NginxConfHandler()
docker = DockerContainerProvider()

def on_expire_container(metadata: FunctionMetadata):
    nginx_handler.remove(metadata)
    docker.reload_nginx_container_conf()
    docker.pause(metadata)

container_manager = RedisContainerManager(on_container_expire=on_expire_container)

@app.post("/functions")
async def new_function(file: UploadFile, background_task: BackgroundTasks, body: str = Form(...)):
    data = FunctionMetadata.from_body(absolute_path=absolute_path, endpoint_inputs=body)
    
    await __save_function_files(data, file)
    __copy_base_management_files(absolute_path, data.folder_path)
    
    background_task.add_task(__handle_build, data)
    return {"function": data}

@app.post("/functions/{function_id}/execute")
def execute_function(function_id: str, body: dict):
    if container_manager.in_building(function_id):
        return Response(status_code=403, content=json.dumps({"error": "Container in build"}))
    
    if not container_manager.is_running(function_id):

        if container_manager.is_idle(function_id):
            __handle_idle(function_id)
        else:
            __handle_paused(function_id)
    
    metadata = container_manager.get_data(function_id)

    container_manager.registry_request(function_id=function_id)
    return nginx_handler.request(path=metadata.tag, data=body)
    container_manager.to_paused(function_id)
    metadata = container_manager.get_data(function_id)
    on_expire_container(metadata)

def __handle_build(metadata: FunctionMetadata):
    container_manager.save(metadata)
    docker.build(metadata)
    container_manager.to_idle(metadata.id)

def __handle_idle(function_id: str):
    metadata = container_manager.get_data(function_id)
    docker.run(metadata)
    __update_nginx_config(metadata)
    container_manager.to_running(function_id)

def __handle_paused(function_id: str):
    metadata = container_manager.get_data(function_id)
    docker.start(metadata)
    __update_nginx_config(metadata)
    container_manager.to_running(function_id)

def __update_nginx_config(metadata: FunctionMetadata):
    nginx_handler.add(metadata)
    docker.reload_nginx_container_conf()
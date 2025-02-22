import docker
import time
import threading
from contracts.upload_function_request import FunctionMetadata

class DockerContainerProvider:
    def __init__(self):
        self.client = docker.from_env()
        self.network_name = "dockless_dockless-network"
    
    def _build_image(self, metadata: FunctionMetadata):
        build_args = {
            "FUNCTION_DEPENDENCIES": metadata.str_dependencies,
            "PY_VERSION": metadata.version
        }
        
        self.client.images.build(
            path=metadata.folder_path,
            buildargs=build_args,
            tag=metadata.name
        )
    
    def __run_container(self, metadata: FunctionMetadata):
        container = self.client.containers.run(
            metadata.name, detach=True, network=self.network_name, name=metadata.tag
        )
        
        while True:
            container.reload()
            if container.status == "running" and container.attrs["State"].get("Health", {}).get("Status") == "healthy":
                break
            time.sleep(2)
    
    def __unpause_container(self, metadata: FunctionMetadata):
        container = self.client.containers.get(metadata.tag)
        container.unpause()
        
        while True:
            container.reload()
            if container.status == "running" and container.attrs["State"].get("Health", {}).get("Status") == "healthy":
                break
            time.sleep(2)
    
    def build(self, metadata: FunctionMetadata):
        self._build_image(metadata)
    
    def run(self, metadata: FunctionMetadata):
        thread = threading.Thread(target=self.__run_container, args=(metadata,))
        thread.start()
    
    def start(self, metadata: FunctionMetadata):
        thread = threading.Thread(target=self.__unpause_container, args=(metadata,))
        thread.start()
    
    def pause(self, metadata: FunctionMetadata):
        self.client.containers.get(metadata.tag).pause()
    
    def get_container(self, container_name: str):
        return self.client.containers.get(container_name)

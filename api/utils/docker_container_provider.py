import docker

from contracts.upload_function_request import FunctionMetadata
import time 
import threading
class DockerContainerProvider:
    def __init__(self):
        self.__client = docker.from_env()
        self.__network_name = "dockless_dockless-network"
    
    def __build_img(self, metadata: FunctionMetadata):
        args = {
            "FUNCTION_DEPENDENCIES": metadata.str_dependencies,
            "PY_VERSION": metadata.version
        }

        self.__client.images.build(
            path=metadata.folder_path,
            buildargs=args,
            tag=metadata.name
        )
    
    def __run_container_in_thread(self, metadata: FunctionMetadata):
        def run_container():
            container = self.__client.containers.run(
                metadata.name, detach=True, network=self.__network_name, name=metadata.tag
            ) 

            while True:
                container.reload()
                is_container_healthy = container.attrs["State"].get("Health", {}).get("Status") == "healthy"
                if container.status == "running" and is_container_healthy:
                    break
                time.sleep(2)

        thread = threading.Thread(target=run_container)
        thread.start()


    def build(self, metadata: FunctionMetadata):
        self.__build_img(metadata=metadata)
    
    def run(self, metadata: FunctionMetadata):
        self.__run_container_in_thread(metadata=metadata)  

    def pause(self, metadata: FunctionMetadata):
        self.__client.containers.get(metadata.tag).pause()

    def get_container(self, container_name: str):
        return self.__client.containers.get(container_name)

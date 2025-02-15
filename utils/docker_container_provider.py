import docker

from contracts.upload_function_request import FunctionMetadata
from utils.nginx_conf_handler import NginxConfHandler

class DockerContainerProvider:
    def __init__(self):
        self.__client = docker.from_env()
        self.__network_name = "dockless_dockless-network"
        self.__nginx_handler = NginxConfHandler()
    
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
    
    def __run(self, metadata: FunctionMetadata):
        tag = f"{metadata.name}-{metadata.id}"
        self.__client.containers.run(metadata.name, detach=True, network=self.__network_name, name=tag) 

    def build_and_run(self, metadata: FunctionMetadata):
        self.__build_img(metadata=metadata)
        self.__run(metadata=metadata)
        self.__registry_on_nginx(metadata=metadata)

    def __registry_on_nginx(self, metadata: FunctionMetadata):
        self.__nginx_handler.add(metadata=metadata)

        nginx = self.__client.containers.get("nginx-proxy")
        nginx.exec_run("nginx -s reload")
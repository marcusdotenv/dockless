import docker

from contracts.upload_function_request import FunctionMetadata

class DockerContainerProvider:
    def __init__(self):
        self.client = docker.from_env()

    
    def build_img(self, metadata: FunctionMetadata):
        args = {
            "FUNCTION_DEPENDENCIES": metadata.str_dependencies,
            "PY_VERSION": metadata.version
        }

        self.client.images.build(
            path=metadata.folder_path,
            buildargs=args,
            tag=metadata.name
        )
    
    def run(self, img_name: str):
        self.client.containers.run(img_name, detach=True, ports={'8001/tcp': 8001}) 

    def build_and_run(self, metadata: FunctionMetadata):
        self.build_img(metadata=metadata)
        self.run(img_name=metadata.name)

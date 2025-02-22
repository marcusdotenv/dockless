import redis
import json

from utils.container_status import ContainerStatus
from contracts.upload_function_request import FunctionMetadata

class RedisContainerManager:
    def __init__(self, on_container_expire: callable):
        self.__client = redis.Redis(host='redis', port=6379, decode_responses=True)
        self.__client.config_set("notify-keyspace-events", "KEA")
        self.__on_expire = on_container_expire
        self.__client_pubsub = self.__client.pubsub()
        self.__client_pubsub.psubscribe(**{'__keyevent@0__:expired': self.handle_expirations})
        self.__client_pubsub.run_in_thread(sleep_time=0.01, daemon=True)

    def __build_key_status(self, function_id: str):
        return f"function:{function_id}:status"
    
    def __build_key_data(self, function_id: str):
        return f"function:{function_id}:data"
    
    def __build_key_trigger(self, function_id: str):
        return f"function:{function_id}:trigger"
    
    def save(self, metadata: FunctionMetadata):
        key_status = self.__build_key_status(metadata.id)
        key_data = self.__build_key_data(metadata.id)

        self.__client.set(name=key_status, value=ContainerStatus.IN_BUILD.name)
        self.__client.set(name=key_data, value=metadata.model_dump_json())

    def to_idle(self, function_id: str):
        key = self.__build_key_status(function_id)
        self.__client.set(name=key, value=ContainerStatus.IDLE.name)

    def to_paused(self, function_id: str):
        key = self.__build_key_status(function_id)
        self.__client.set(name=key, value=ContainerStatus.PAUSED.name)

    def in_building(self, function_id: str):
        key = self.__build_key_status(function_id)
        return self.__client.get(key) == ContainerStatus.IN_BUILD.name

    def is_running(self, function_id: str):
        key = self.__build_key_status(function_id)
        return self.__client.get(key) == ContainerStatus.RUNNING.name
    
    def to_running(self, function_id: str):
        key = self.__build_key_status(function_id)
        self.__client.set(name=key, value=ContainerStatus.RUNNING.name)

        key_trigger = self.__build_key_trigger(function_id=function_id)
        self.__client.set(name=key_trigger, value="triggered", ex=120)
    
    def is_idle(self, function_id: str):
        key = self.__build_key_status(function_id)
        return self.__client.get(key) == ContainerStatus.IDLE.name
    
    def get_data(self, function_id: str) -> FunctionMetadata:
        key_data = self.__build_key_data(function_id=function_id)
        data = self.__client.get(key_data)
        return FunctionMetadata(**json.loads(data))

    def registry_request(self, function_id: str):
        key_trigger = self.__build_key_trigger(function_id=function_id)
        self.__client.set(name=key_trigger, value="trigger", ex=120)

    def handle_expirations(self, message):
        print("RECEIVED MESSAGE ", message)
        if not message or not message['type'] == 'pmessage':
            return
            
        expired_key = str(message["data"])
        if not expired_key.startswith("function"):
            return
            
        idle_container_id = expired_key.split(":")[1]
        self.to_paused(idle_container_id)
        data = self.get_data(idle_container_id)
        self.__on_expire(data)
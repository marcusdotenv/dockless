from dotenv import load_dotenv
import os

load_dotenv()

REDIS_HOST=os.getenv("REDIS_HOST")
REDIS_PORT=int(os.getenv("REDIS_PORT"))
TIME_PAUSE_IDLE_CONTAINERS_IN_SECONDS=int(os.getenv("TIME_PAUSE_IDLE_CONTAINERS_IN_SECONDS"))
NGINX_CONTAINER_NAME=os.getenv("NGINX_CONTAINER_NAME")

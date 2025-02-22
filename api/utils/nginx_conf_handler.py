import os
from textwrap import dedent
from utils.redis_container_manager import RedisContainerManager
from contracts.upload_function_request import FunctionMetadata
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, wait_fixed


class NginxConfHandler:
    def __init__(self):
        absolute_path = os.path.dirname(os.path.abspath(__file__)) 
        self.__file_path = os.path.join(absolute_path, "../", "nginx.conf")
        self.reset()

    def reset(self):
        content = '''events { }

http {

    server {
        listen 80;
    }
}
'''
        with open(self.__file_path, 'w') as f:
            f.write(content)

    def add(self, metadata: FunctionMetadata):

        new_upstream = self.__format_upstream(metadata.tag)
        new_location = self.__format_location(metadata.tag)

        with open(self.__file_path, "r+") as f:
            lines = f.readlines()

            if self.__block_exists(lines, f"upstream {metadata.tag} {{") or self.__block_exists(lines, f"location /{metadata.tag}/ {{"):
                # already exists
                return

            http_index = self.__find_index(lines, "http {")
            server_end_index = self.__find_last_index(lines, "}")

            lines.insert(http_index + 1, new_upstream)
            lines.insert(server_end_index, new_location)

            self.__write_lines(f, lines)  

    def remove(self, metadata: FunctionMetadata):

        with open(self.__file_path, "r+") as f:
            lines = f.readlines()

            upstream_range = self.__find_block(lines, f"upstream {metadata.tag} {{")
            location_range = self.__find_block(lines, f"location /{metadata.tag}/ {{")

            if not any(upstream_range) and not any(location_range):
                # not exists
                return

            self.__delete_ranges(lines, [upstream_range, location_range])
            self.__write_lines(f, lines)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(2), 
        retry=retry_if_exception_type(requests.RequestException), 
    )
    def request(self, path: str):
        response = requests.post(f"http://nginx-proxy:80/{path}/execute")
        response.raise_for_status() 
        return response.json()

    def __format_upstream(self, tag: str):
        return dedent(f"""
            upstream {tag} {{
                server {tag}:8001;
            }}
        """).strip() + "\n"

    def __format_location(self, tag: str):
        return dedent(f"""
            location /{tag}/ {{
                proxy_pass http://{tag}/;
                rewrite ^/{tag}(/.*)$ $1 break;
            }}
        """).strip() + "\n"

    def __block_exists(self, lines: list[str], start_marker: str):
        return any(start_marker in line for line in lines)

    def __find_index(self, lines: list[str], target: str):
        return next((i for i, line in enumerate(lines) if line.strip() == target), None)

    def __find_last_index(self, lines: list[str], target: str):
        return max((i for i, line in enumerate(lines) if line.strip() == target), default=None)

    def __find_block(self, lines: list[str], start_marker: str):
        start_index = self.__find_index(lines, start_marker)
        if start_index is None:
            return None, None
        end_index = self.__find_index(lines[start_index:], "}") 
        return (start_index, start_index + end_index + 1) if end_index is not None else (None, None)

    def __delete_ranges(self, lines: list[str], ranges: list[tuple[int, int]]):
        for start, end in sorted(filter(None, ranges), reverse=True):
            del lines[start:end]

    def __write_lines(self, file, lines: list[str]):
        file.seek(0)
        file.writelines(lines)
        file.truncate()
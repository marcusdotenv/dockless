from enum import Enum


class ContainerStatus(Enum):
    RUNNING="running"
    IDLE="idle"
    IN_BUILD="building"
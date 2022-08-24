from enum import Enum
from dataclasses import dataclass


@dataclass
class TaskState(Enum):
    QUEUED = 2
    ERRORED = -1
    STOPPED = 0
    SUCCESSFUL = 1
    RUNNING = 3


@dataclass
class PipelineState(Enum):
    QUEUED = 2
    ERRORED = -1
    STOPPED = 0
    SUCCESSFUL = 1
    RUNNING = 3


t = TaskState.STOPPED

print(t)
print(type(t))
print(t.value)

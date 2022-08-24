from dataclasses import dataclass, field
from typing import List, ClassVar


@dataclass
class Config:
    # Default options
    WATCHED_FOLDER: ClassVar[str] = "/dags"
    WATCHED_FILE_EXTENSIONS: ClassVar[List] = [".py"]

    # Recursive search when specifying an input folder to watch
    ORCHESTRATOR_RECURSIVENESS: ClassVar[bool] = True

    # Program specific
    ACCEPTED_PROGRAMS: ClassVar[List] = ["scheduler"]

    # Queue specific
    PIPELINE_BASE_QUEUE_MAX_LENGTH: ClassVar[int] = 20
    PIPELINE_QUEUE_MAX_LENGTH: ClassVar[int] = 20

    # Worker config
    DOCKER_SOURCE_CODE_PATH = "/app"

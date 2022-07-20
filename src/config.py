from dataclasses import dataclass, field
from typing import List, ClassVar


@dataclass
class Config:
    # Default options
    WATCHED_FOLDER: ClassVar[
        str
    ] = "/Users/iliono/My Drive/Homefiles/repos-mac/homemade-airflow-ivanliono/dags"
    WATCHED_FILE_EXTENSIONS: ClassVar[List] = [".py"]
    ORCHESTRATOR_RECURSIVENESS: ClassVar[
        bool
    ] = True  # Recursive search when specifying an input folder to watch
    ACCEPTED_PROGRAMS: ClassVar[List] = ["scheduler"]

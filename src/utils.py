from glob import glob
from croniter import croniter
from datetime import datetime as dt


# def check_if_substring_in_list(substring: str, input_list: list):
#     return any([True for string in input_list if substring in string])


def get_files_in_folder(input_path_string: str, recursive: bool = False):
    if recursive and input_path_string[-2:] != "**":
        raise ValueError(
            f"Expected '**' at end of input_path_string - {input_path_string}"
        )
    return glob(input_path_string, recursive=recursive)


def create_cron_iter(cron_str: str, base: dt = dt.utcnow()):
    if croniter.is_valid(cron_str):
        return croniter(cron_str, base)
    else:
        raise ValueError(f"Invalid input string - {cron_str}")

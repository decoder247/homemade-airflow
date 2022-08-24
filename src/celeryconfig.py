from distutils.command.config import config
from celery import Celery


class CeleryConfig:
    broker_url = "redis://localhost"
    # result_backend = "rpc://"

    task_serializer = "json"
    result_serializer = "json"
    accept_content = ["json"]
    timezone = "Europe/Amsterdam"
    enable_utc = True


# app = Celery(main="tasks", config_source=CeleryConfig)


# app.config_from_object("celeryconfig")
# app.send_task("tasks.tasks.beta_task", args=[2, 2], kwargs={})

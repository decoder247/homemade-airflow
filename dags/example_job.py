from models import Pipeline, PythonTask


def print_hello():
    print("hello")


def print_world():
    print("world")


# Create 2 pipelines
pipeline = Pipeline(name="test_example_job", schedule="* * * * * *")
second_pipeline = Pipeline(name="another_example_job", schedule="* * * * * *")

# Create 2 tasks
task_1 = PythonTask("print_hello", python_callable=print_hello, pipeline=pipeline)
task_2 = PythonTask("print_world", python_callable=print_world, pipeline=pipeline)
task_3 = PythonTask(
    "print_world", python_callable=print_world, pipeline=second_pipeline
)

# task_3 = HttpTask(
#     'http request',
#     endpoint='http://httpbin.org/get',
#     method='GET'
#     pipeline=pipeline

# )

task_1.set_downstream(task_2)
# task_2.set_downstream(task_3)

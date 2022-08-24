from models import Pipeline, PythonTask


def print_hello():
    print("hello")


def print_world():
    print("world")


def print_something(ip: str = None):
    print(f"Printing user input -> '{ip}'")


# Create 2 pipelines
pipeline_1 = Pipeline(pipeline_id="pipeline_1", schedule="* * * * * 0")
pipeline_2 = Pipeline(pipeline_id="pipeline_2", schedule="* * * * * */20")

# Create tasks for pipeline_1
# 1 -         - 4
#    | - 3 - |
# 2 -         - 5 - 6
task_1 = PythonTask("task_1", python_callable=print_hello, pipeline=pipeline_1)
task_2 = PythonTask("task_2", python_callable=print_world, pipeline=pipeline_1)
task_3 = PythonTask("task_3", python_callable=print_hello, pipeline=pipeline_1)
task_4 = PythonTask("task_4", python_callable=print_hello, pipeline=pipeline_1)
task_5 = PythonTask("task_5", python_callable=print_hello, pipeline=pipeline_1)
task_6 = PythonTask(
    "task_6",
    python_callable=print_something,
    pipeline=pipeline_1,
    op_args=["hello!"],
)

# Set order for tasks in pipeline_1
task_1.set_downstream(task_3)
task_2.set_downstream(task_3)
task_3.set_downstream(task_4)
task_3.set_downstream(task_5)
task_5.set_downstream(task_6)

# Create tasks for pipeline_2
# 1 -> 2 -> 3
task_x1 = PythonTask("print_world", python_callable=print_world, pipeline=pipeline_2)
task_x2 = PythonTask("print_hello", python_callable=print_hello, pipeline=pipeline_2)
task_x3 = PythonTask(
    "print_something",
    python_callable=print_something,
    pipeline=pipeline_2,
    op_args=["hello! I am printing something from pipeline 2"],
)

# Set order
task_x1.set_downstream(task_x2)
task_x2.set_downstream(task_x3)

# task_3 = HttpTask(
#     'http request',
#     endpoint='http://httpbin.org/get',
#     method='GET'
#     pipeline=pipeline

# )

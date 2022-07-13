from modules import Pipeline

pipeline = Pipeline(name="test_example_job", schedule="* * * * * *")

# def print_hello():
#     print('hello')


# def print_world():
#     print('world')


# task_1 = PythonTask(
#     'print_hello',
#     python_callable=print_hello
#     pipeline=pipeline
# )

# task_2 = PythonTask(
#     'print_world',
#     python_callable=print_world
#     pipeline=pipeline
# )

# task_3 = HttpTask(
#     'http request',
#     endpoint='http://httpbin.org/get',
#     method='GET'
#     pipeline=pipeline

# )

# task_1.set_downstream(task_2)
# task_2.set_downstream(task_3)

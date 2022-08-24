# homemade-airflow-ivanliono

## Table of contents

- [Table of contents](#table-of-contents)
- [todo](#todo)
- [running](#running)

## todo

Find the remaining todo's by looking for `#TODO:` and `#NOTE:`

**GREAT Refresh cycle (When a DAG is updated)**  

1. task flows (i.e. DAGs) are updated
2. new DAG, if detected, is added to the list and the pipeline queue refreshed

ASYNC to this -:

- There should be an executor / worker that executes based on info from the scheduling class
- xx

**Main**

-----> RESOLVE queue based on priority as well!

- Use scheduler to execute at specific time! -> print pipeline_running for now, but use celery to chain execution of tasks
Also then get pipeline to execute tasks (i.e. using celery!!)
  - Execute pipeline on schedule first
  - Then, use celery to execute tasks in the correct DAG sequence (The topoligical order / sorting might need to be updated)

- Pipeline should have an end_date parameter, and the executor should check
- Scheduler checks if end date if reached, if it is then quit and don't put in scheduler, and state is set to done!!!

Get scheduler to resolve the pipeline queues!!! And print the max 20 -> something should refresh, and check if max_queue is reached or not reached

- [x] Generate UID's for each task + pipeline
- [x] Investigate whether we can append objects to 'nodes' in the graph, instead of just strings
- [x] Give visual represenation of connected tasks

- [ ] Implement flow of executing tasks in the pipeline + the schedule for said pipeline / sequence execution, i.e. after showing dag what is the actual sequence
- [ ] Populate and display the list of pipelines queued, and execute tasks in pipeline, i.e. use celery for grouping!
  - [ ] Cron string parsing + scheduling logic
- [ ] Investigate how to visualise dependencies for grouping (parallel processing)

- [ ] Need a runner, that monitors every (i.e. minute) and executes when schedule is met
- [ ] Try extending the example_job script and see if it works with other imports etc.
- [ ] PICKLE functions for backup!! // to send to workers?

**NOTE: REFRESH dag cycle**

```
    - Create dag for each (changed) pipeline
    - Check each node is connected
    - Get the sequence
    - Show graph
```

## running

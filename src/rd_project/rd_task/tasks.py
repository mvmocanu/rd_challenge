from rd_project.celery import app

from .models import Task


class TaskException(Exception):
    pass


@app.task(bind=True)
def add(self, task_id, a, b):
    task = Task.objects.get(id=task_id)
    task.set_celery_task_id(self.request.id, commit=False)

    try:
        result = a + b
        task.mark_as_successfull(result=result)
        return result
    except Exception as error:
        task.mark_as_failed(failed_message=error)
        raise TaskException(error) from error

import pytest
from django.utils import timezone
from django_celery_beat.models import IntervalSchedule
from django_celery_beat.models import PeriodicTask

from rd_project.rd_task.models import Task
from rd_project.rd_task.models import TaskSchedule


@pytest.mark.django_db
class TestTaskModel:
    def test_create_task(self):
        task = Task.objects.create(a=1, b=2)
        assert task.a == 1
        assert task.b == 2
        assert task.status == Task.PENDING

    def test_set_celery_task_id(self):
        task = Task.objects.create(a=1, b=2)
        task.set_celery_task_id("test_task_id")
        assert task.celery_task_id == "test_task_id"

    def test_mark_as_successful(self):
        task = Task.objects.create(a=1, b=2)
        task.mark_as_successfull(result=42)
        assert task.status == Task.SUCCESS
        assert task.results.count() == 1
        assert task.results.first().result == 42

    def test_mark_as_failed(self):
        task = Task.objects.create(a=1, b=2)
        task.mark_as_failed("Some error occurred")
        assert task.status == Task.FAILED
        assert task.failed_message == "Some error occurred"


@pytest.mark.django_db
class TestTaskScheduleModel:
    def test_create_task_schedule(self):
        task = Task.objects.create(a=1, b=2)
        schedule = TaskSchedule.objects.create(
            task=task, scheduled_at=timezone.now(), interval=10
        )
        assert schedule.task == task
        assert schedule.interval == 10

    def test_schedule_celery_beat_task(self):
        task = Task.objects.create(a=1, b=2)
        schedule = TaskSchedule.objects.create(
            task=task, scheduled_at=timezone.now(), interval=10
        )
        schedule.schedule_celery_beat_task()
        assert PeriodicTask.objects.count() == 1
        assert (
            PeriodicTask.objects.first().name
            == f"task-{schedule.task_id}-scheduled"
        )
        assert IntervalSchedule.objects.count() == 1
        assert IntervalSchedule.objects.first().every == 10

    def test_update_celery_beat_task(self):
        task = Task.objects.create(a=1, b=2)
        schedule = TaskSchedule.objects.create(
            task=task, scheduled_at=timezone.now(), interval=10
        )
        schedule.schedule_celery_beat_task()
        schedule.interval = 20
        schedule.update_celery_beat_task()
        assert schedule.interval_schedule.every == 20

    def test_delete_celery_beat_task(self):
        task = Task.objects.create(a=1, b=2)
        schedule = TaskSchedule.objects.create(
            task=task, scheduled_at=timezone.now(), interval=10
        )
        schedule.schedule_celery_beat_task()
        assert PeriodicTask.objects.count() == 1
        schedule.delete_celery_beat_task()
        assert PeriodicTask.objects.count() == 0

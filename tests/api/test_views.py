import pytest
from django_celery_beat.models import IntervalSchedule
from django_celery_beat.models import PeriodicTask
from rest_framework import status
from rest_framework.test import APIClient

from rd_project.rd_task.models import Task
from rd_project.rd_task.models import TaskSchedule


@pytest.mark.django_db
class TestTaskScheduleViewSet:
    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def task_schedule(self):
        task = Task.objects.create(a=5, b=2)
        return TaskSchedule.objects.create(
            task=task, scheduled_at="2022-02-20T14:24:34", interval=30
        )

    def test_create_task_schedule(self, api_client):
        data = {
            "a": 5,
            "b": 4,
            "scheduled_at": "2022-02-22T14:14:14",
            "interval": 50,
        }
        response = api_client.post("/api/task-schedules/", data)
        assert response.status_code == status.HTTP_201_CREATED
        assert TaskSchedule.objects.count() == 1
        assert Task.objects.count() == 1
        assert Task.objects.first().a == 5
        assert Task.objects.first().b == 4
        assert IntervalSchedule.objects.count() == 1
        assert PeriodicTask.objects.count() == 1

    def test_update_task_schedule(self, api_client, task_schedule):
        task_schedule.schedule_celery_beat_task()
        data = {
            "a": 6,
            "b": 6,
            "scheduled_at": "2022-02-22T14:14:14",
            "interval": 10,
        }
        response = api_client.put(
            f"/api/task-schedules/{task_schedule.pk}/", data
        )
        assert response.status_code == status.HTTP_200_OK
        assert TaskSchedule.objects.count() == 1
        assert Task.objects.count() == 1
        assert Task.objects.first().a == 6
        assert Task.objects.first().b == 6
        assert IntervalSchedule.objects.count() == 1
        assert PeriodicTask.objects.count() == 1

    def test_delete_task_schedule(self, api_client, task_schedule):
        task_schedule.schedule_celery_beat_task()
        response = api_client.delete(
            f"/api/task-schedules/{task_schedule.pk}/"
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert TaskSchedule.objects.count() == 0
        assert Task.objects.count() == 0
        assert IntervalSchedule.objects.count() == 0
        assert PeriodicTask.objects.count() == 0

    def test_retrieve_task_schedule(self, api_client, task_schedule):
        response = api_client.get(f"/api/task-schedules/{task_schedule.pk}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["task"]["a"] == task_schedule.task.a


@pytest.mark.django_db
class TestTaskViewSet:
    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def task(self):
        return Task.objects.create(a=5, b=6)

    def test_create_task(self, api_client):
        data = {"a": 5, "b": 6}
        response = api_client.post("/api/tasks/", data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Task.objects.count() == 1
        assert Task.objects.get().a == 5
        assert Task.objects.get().b == 6

    def test_retrieve_task(self, api_client, task):
        response = api_client.get(f"/api/tasks/{task.pk}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["a"] == task.a
        assert response.data["b"] == task.b

    def test_list_tasks(self, api_client, task):
        response = api_client.get("/api/tasks/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

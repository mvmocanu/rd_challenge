import json
import logging
import uuid

from django.db import models
from django_celery_beat.models import IntervalSchedule
from django_celery_beat.models import PeriodicTask

logger = logging.getLogger(__name__)


class BaseModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True


class TaskSchedule(BaseModel, models.Model):
    TASK_ADD = "rd_project.rd_task.tasks.add"
    # task = models.ForeignKey(
    #     Task, on_delete=models.CASCADE, related_name="schedule"
    # )
    interval_schedule = models.ForeignKey(
        "django_celery_beat.IntervalSchedule",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    periodic_task = models.ForeignKey(
        "django_celery_beat.PeriodicTask",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    scheduled_at = models.DateTimeField()
    interval = models.IntegerField(
        help_text=("The interval in seconds for periodic tasks")
    )

    def schedule_celery_beat_task(self):
        interval_schedule, _ = IntervalSchedule.objects.get_or_create(
            every=self.interval, period=IntervalSchedule.SECONDS
        )

        periodic_task = PeriodicTask.objects.create(
            interval=interval_schedule,
            name=f"task-{self.task.id}-scheduled",
            task=self.TASK_ADD,
            args=json.dumps([str(self.task.id), self.task.a, self.task.b]),
            start_time=self.scheduled_at,
            enabled=True,
        )
        self.interval_schedule = interval_schedule
        self.periodic_task = periodic_task
        self.save()
        return periodic_task

    def update_celery_beat_task(self):
        self.interval_schedule.every = self.interval
        self.interval_schedule.save()
        self.periodic_task.scheduled_at = self.scheduled_at
        self.periodic_task.args = json.dumps(
            [str(self.task.id), self.task.a, self.task.b]
        )
        self.periodic_task.save()

    def delete_celery_beat_task(self):
        # self.task.delete()
        self.periodic_task.delete()
        self.interval_schedule.delete()


class Task(BaseModel, models.Model):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (SUCCESS, "Success"),
        (FAILED, "Failed"),
    ]

    schedule = models.OneToOneField(
        "rd_task.TaskSchedule",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="task",
    )
    a = models.IntegerField()
    b = models.IntegerField()
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=PENDING
    )
    failed_message = models.CharField(max_length=255, blank=True)
    celery_task_id = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Task {self.id} - {self.status}"

    def set_celery_task_id(self, _id, commit=True):
        self.celery_task_id = _id
        commit and self.save()

    def mark_as_successfull(self, result, commit=True):
        self.status = self.SUCCESS
        TaskResult.objects.create(task=self, result=result)
        commit and self.save()

    def mark_as_failed(self, failed_message, commit=True):
        self.failed_message = failed_message
        self.status = self.FAILED
        commit and self.save()


class TaskResult(BaseModel, models.Model):
    task = models.ForeignKey(
        "Task", on_delete=models.CASCADE, related_name="results"
    )
    result = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.task_id} - {self.result}"

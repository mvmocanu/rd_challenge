import logging

from rest_framework import serializers

from rd_project.rd_task.models import Task
from rd_project.rd_task.models import TaskResult
from rd_project.rd_task.models import TaskSchedule

logger = logging.getLogger(__name__)


class TaskResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskResult
        fields = ["result", "created_at"]


class TaskSerializer(serializers.HyperlinkedModelSerializer):
    status = serializers.ChoiceField(
        choices=Task.STATUS_CHOICES, read_only=True
    )
    is_scheduled = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = (
            "url",
            "id",
            "a",
            "b",
            "is_scheduled",
            "status",
            "failed_message",
            "celery_task_id",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "result",
            "status",
            "failed_message",
            "celery_task_id",
            "results",
            "created_at",
            "updated_at",
        )
        extra_kwargs = {
            "url": {"view_name": "api:tasks-detail", "lookup_field": "pk"}
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get("context", {}).get("show_results"):
            self.fields["results"] = TaskResultSerializer(many=True)

    def get_is_scheduled(self, obj):
        return obj.schedule_id is not None


class CreateUpdateTaskScheduleSerializer(
    serializers.HyperlinkedModelSerializer
):
    a = serializers.IntegerField()
    b = serializers.IntegerField()

    class Meta:
        model = TaskSchedule
        fields = [
            "a",
            "b",
            "scheduled_at",
            "interval",
        ]

    def create(self, validated_data):
        schedule = TaskSchedule.objects.create(
            scheduled_at=validated_data["scheduled_at"],
            interval=validated_data["interval"],
        )
        Task.objects.create(
            schedule=schedule, a=validated_data["a"], b=validated_data["b"]
        )
        schedule.schedule_celery_beat_task()
        return schedule

    def update(self, instance, validated_data):
        instance.scheduled_at = validated_data["scheduled_at"]
        instance.interval = validated_data["interval"]
        instance.save()
        instance.task.a = validated_data["a"]
        instance.task.b = validated_data["b"]
        instance.task.save()
        instance.update_celery_beat_task()
        return instance


class TaskScheduleSerializer(serializers.HyperlinkedModelSerializer):
    task = TaskSerializer()

    class Meta:
        model = TaskSchedule
        fields = [
            "url",
            "task",
            "scheduled_at",
            "interval",
            "created_at",
            "updated_at",
        ]
        read_only = ["task", "created_at", "updated_at"]
        extra_kwargs = {
            "url": {
                "view_name": "api:taskschedules-detail",
                "lookup_field": "pk",
            }
        }

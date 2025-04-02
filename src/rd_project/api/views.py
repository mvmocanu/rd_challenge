import logging

from rest_framework import serializers
from rest_framework import status
from rest_framework.mixins import CreateModelMixin
from rest_framework.mixins import DestroyModelMixin
from rest_framework.mixins import ListModelMixin
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.mixins import UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from rd_project.rd_task.models import Task
from rd_project.rd_task.models import TaskSchedule
from rd_project.rd_task.tasks import add

logger = logging.getLogger(__name__)


class TaskSerializer(serializers.HyperlinkedModelSerializer):
    status = serializers.ChoiceField(
        choices=Task.STATUS_CHOICES, read_only=True
    )
    result = serializers.SerializerMethodField()
    is_scheduled = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = (
            "url",
            "id",
            "a",
            "b",
            "is_scheduled",
            "result",
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
            "created_at",
            "updated_at",
        )
        extra_kwargs = {
            "url": {"view_name": "api:tasks-detail", "lookup_field": "pk"}
        }

    def get_result(self, obj):
        result = obj.get_result()
        return result.result if result else None

    def get_is_scheduled(self, obj):
        return obj.schedule.exists()


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
        task = Task.objects.create(
            a=validated_data["a"], b=validated_data["b"]
        )
        instance = TaskSchedule.objects.create(
            task=task,
            scheduled_at=validated_data["scheduled_at"],
            interval=validated_data["interval"],
        )
        instance.schedule_celery_beat_task()
        return instance

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


class TaskScheduleViewSet(
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
    UpdateModelMixin,
    GenericViewSet,
):
    lookup_field = "pk"
    queryset = TaskSchedule.objects.all().order_by("-created_at")
    serializer_class = TaskScheduleSerializer

    def perform_destroy(self, instance):
        instance.delete_celery_beat_task()
        instance.delete()

    def create(self, request, *args, **kwargs):
        serializer = CreateUpdateTaskScheduleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(
            TaskScheduleSerializer(
                instance, context={"request": request}
            ).data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = CreateUpdateTaskScheduleSerializer(
            instance, data=request.data, partial=False
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(
            TaskScheduleSerializer(
                serializer.instance, context={"request": request}
            ).data,
        )


class TaskViewSet(
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    GenericViewSet,
):
    lookup_field = "pk"
    queryset = Task.objects.all().order_by("-created_at")
    serializer_class = TaskSerializer

    def perform_create(self, serializer):
        task = serializer.save()
        add.delay(str(task.id), task.a, task.b)

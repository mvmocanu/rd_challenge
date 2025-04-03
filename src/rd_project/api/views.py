import logging

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

from .serializers import CreateUpdateTaskScheduleSerializer
from .serializers import TaskScheduleSerializer
from .serializers import TaskSerializer

logger = logging.getLogger(__name__)


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

    def get_serializer_class(self):
        logger.debug("action: %s", self.action)
        # if self.action in ["retrieve", "update", "list"]:
        #     return TaskScheduleSerializer
        if self.action in [
            "create",
        ]:
            return CreateUpdateTaskScheduleSerializer
        return TaskScheduleSerializer

    # def get_serializer(self, *args, **kwargs):
    #     logger.debug("args %s", args)
    #     logger.debug("kargs %s", kwargs)
    #     serializer_class = self.get_serializer_class()
    #     kwargs.setdefault("context", self.get_serializer_context())
    #     if self.action == "update":
    #         object = self.get_object()
    #         kwargs["data"]["a"] = object.task.a
    #         wargs["data"]["b"] = object.task.b
    #     return serializer_class(*args, **kwargs)

    def perform_destroy(self, instance):
        instance.delete_celery_beat_task()
        instance.delete()

    def create(self, request, *args, **kwargs):
        serializer = CreateUpdateTaskScheduleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            TaskScheduleSerializer(
                serializer.instance, context={"request": request}
            ).data,
            status=status.HTTP_201_CREATED,
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
    queryset = (
        Task.objects.all()
        .prefetch_related("results")
        .prefetch_related("schedule")
        .order_by("-created_at")
    )
    serializer_class = TaskSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.action == "retrieve":
            context["show_results"] = True
        logger.debug("context %s", context)
        return context

    def perform_create(self, serializer):
        task = serializer.save()
        add.delay(str(task.id), task.a, task.b)

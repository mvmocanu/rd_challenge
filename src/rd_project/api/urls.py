from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import TaskScheduleViewSet
from .views import TaskViewSet

app_name = "api"

router = DefaultRouter()
router.register(r"task", TaskViewSet, basename="tasks")
router.register(
    r"task-schedule", TaskScheduleViewSet, basename="taskschedules"
)

urlpatterns = [
    path("api/", include(router.urls)),
]


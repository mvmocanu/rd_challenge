from django.contrib import admin

from .models import Task
from .models import TaskResult
from .models import TaskSchedule


class TaskResultAdmin(admin.TabularInline):
    model = TaskResult
    extra = 0
    fields = ["pk", "result", "created_at"]
    readonly_fields = ["pk", "result", "created_at"]

    def has_add_permission(self, request, obj):
        return False


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    search_fields = ["id"]
    list_filter = ["status"]
    inlines = [TaskResultAdmin]
    list_display = [
        "id",
        "a",
        "b",
        "status",
        "updated_at",
    ]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "id",
                    "a",
                    "b",
                    "status",
                    "failed_message",
                )
            },
        ),
        (
            "Miscellaneous",
            {"fields": ("celery_task_id", "created_at", "updated_at")},
        ),
    )

    ordering = ("-updated_at",)
    readonly_fields = [field.name for field in Task._meta.fields]

    def has_add_permission(self, request):
        return False


@admin.register(TaskSchedule)
class TaskScheduleAdmin(admin.ModelAdmin):
    list_display = ["id", "task", "scheduled_at", "interval", "updated_at"]

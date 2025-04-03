# The challenge

## Objective

Build a task scheduling system for a simulated computer cluster using Django, Celery, and Docker. The system will schedule, distribute, and monitor simple addition operations (A+B) across worker nodes through a REST API. Users should be able to create, monitor, and manage these computation tasks.

The point here is to see how Django, Celery, Redis, and PostgreSQL play together. This is the reason for choosing a very simple operation such as `A+B` .

## Business Context

You're building a task scheduler for a distributed computing system that processes addition operations. While the operations themselves are simple (A+B), the system needs to handle scheduling, resource allocation, task queuing, and results storage efficiently.

## Developement

### Installing the project

Having docker on the local machine is a requirement.

1. In the root of the project, run the following command:

```
docker compose up --build
```

2. After the build is finished, run the following commands

```
docker compose exec web bash
python manage.py collectstatic
python manage.py migrate
```

### Running the project

1. In the root of the porject, run the following command:

```
docker compose up
```

2. Go to http://localhost:8000/

### Running the tests

In the root of the project, the following command can be run:

```
docker compose run django-web pytest
```

## Architecture

## 🔍 1. Overview

This Django-based project is structured around a clean separation of concerns using the Django REST Framework (DRF) for API communication and Celery for background task processing. The system is modular, scalable, and built to handle asynchronous operations efficiently.

### Key Components:

- **Models** define data structures and business rules.
- **Serializers** validate and convert data for API interaction.
- **Views** orchestrate logic, handle requests, and manage workflow.
- **URLs** map API endpoints to logic handlers.
- **Tasks** define background jobs for asynchronous processing.

#### Models documentation

This module defines the core data models used in the application for managing and scheduling arithmetic tasks. It supports one-off and periodic task execution using Celery and Django-Celery-Beat.

---

## 🔹 BaseModel

An **abstract base model** that provides two standard fields:

- `id`: A UUID primary key (automatically generated).
- `created_at`: Timestamp of record creation (auto-populated).
- `updated_at`: Timestamp of last modification (auto-updated).

**Usage**: Inherited by all other models to ensure consistency and auditability.

---

## 🧮 Task

Represents a unit of work to perform an addition operation between two integers (`a + b`). Each task tracks its execution status and is optionally tied to a Celery task.

### Fields:

- `a`- The first operand.
- `b`- The second operand.
- `status` - Tracks task status: `PENDING`, `SUCCESS`, or `FAILED`.
- `failed_message` - Stores error messages when tasks fail.
- `celery_task_id` - Stores the ID of the associated Celery task.

### Methods:

- `set_celery_task_id(_id, commit=True)`: Sets and optionally saves the Celery task ID.
- `mark_as_successfull(result, commit=True)`: Updates task as successful and stores result.
- `mark_as_failed(message, commit=True)`: Updates task as failed with an error message.

---

## ⏰ TaskSchedule

Handles **scheduling of periodic tasks** using Django-Celery-Beat. It ties a `Task` to a schedule using an `IntervalSchedule` and a `PeriodicTask`.

### Fields:

- `task` - Links to the `Task` to be scheduled using a ForeignKey.
- `interval_schedule` - Links to the Celery Beat `IntervalSchedule` using a ForeignKey.
- `periodic_task` - Links to the Celery Beat `PeriodicTask` usign a ForeignKey.
- `scheduled_at` - When the task should start.
- `interval` - Interval in seconds for the periodic task.

### Methods:

- `schedule_celery_beat_task()`: Creates and associates a new periodic task with Celery Beat.
- `update_celery_beat_task()`: Updates the existing interval and task configuration.
- `delete_celery_beat_task()`: Cleans up associated Celery Beat records.

---

## ✅ TaskResult

Stores the **result of a completed task**. Each task can have multiple results, ordered from newest to oldest.

### Fields:

- `task` - The `Task` to which this result belongs (ForeignKey).
- `result` - The numeric result of `a + b`.

---

# The challenge

## Objective

Build a task scheduling system for a simulated computer cluster using Django, Celery, and Docker. The system will schedule, distribute, and monitor simple addition operations (A+B) across worker nodes through a REST API. Users should be able to create, monitor, and manage these computation tasks.

The point here is to see how Django, Celery, Redis, and PostgreSQL play together. This is the reason for choosing a very simple operation such as `A+B` .

## Business Context

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

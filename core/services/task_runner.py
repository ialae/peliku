"""Background task runner using Python threading.

Spawns daemon threads for long-running operations (AI generation, etc.)
and tracks their status via the Task model.
"""

import logging
import threading

from core.models import Task

logger = logging.getLogger(__name__)


def run_in_background(task_type, target_func, *args, **kwargs):
    """Create a Task record and execute *target_func* in a background thread.

    Args:
        task_type: A short label for the operation (e.g. "video_generation").
        target_func: The callable to run in the background.
        *args: Positional arguments forwarded to *target_func*.
        **kwargs: Keyword arguments forwarded to *target_func*.

    Returns:
        int: The primary key of the newly created Task.
    """
    related_object_id = kwargs.pop("related_object_id", None)
    related_object_type = kwargs.pop("related_object_type", "")

    task = Task.objects.create(
        task_type=task_type,
        status="pending",
        related_object_id=related_object_id,
        related_object_type=related_object_type,
    )

    thread = threading.Thread(
        target=_execute_task,
        args=(task.pk, target_func, args, kwargs),
        daemon=True,
    )
    thread.start()

    return task.pk


def _execute_task(task_pk, target_func, args, kwargs):
    """Run *target_func* and persist the outcome on the Task record.

    This function is intended to be called inside a daemon thread.
    It transitions the task through pending → running → completed/failed.
    """
    import django

    django.setup()

    from core.models import Task as TaskModel

    try:
        task = TaskModel.objects.get(pk=task_pk)
    except TaskModel.DoesNotExist:
        logger.error("Task %s disappeared before execution started.", task_pk)
        return

    task.status = "running"
    task.save(update_fields=["status", "updated_at"])

    try:
        result = target_func(*args, **kwargs)
        task.status = "completed"
        task.progress = 100
        task.result_data = result if isinstance(result, (dict, list)) else None
        task.save(update_fields=["status", "progress", "result_data", "updated_at"])
    except Exception as exc:
        logger.exception("Background task %s (%s) failed.", task_pk, task.task_type)
        task.status = "failed"
        task.error_message = str(exc)
        task.save(update_fields=["status", "error_message", "updated_at"])

"""Tests for the background task runner and status polling API."""

import json
import threading
import time

import pytest

from django.test import Client

from core.models import Task
from core.services.task_runner import run_in_background


@pytest.fixture()
def client():
    """Return a Django test client."""
    return Client()


def _wait_for_status(task_pk, target_status, max_iterations=50):
    """Poll the Task table until the expected status or timeout."""
    for _ in range(max_iterations):
        task = Task.objects.get(pk=task_pk)
        if task.status == target_status:
            return task
        time.sleep(0.1)
    return Task.objects.get(pk=task_pk)


@pytest.mark.django_db(transaction=True)
class TestRunInBackground:
    """Tests for the run_in_background service function."""

    def test_creates_task_with_pending_status(self):
        """run_in_background should create a Task record immediately."""
        event = threading.Event()

        def blocking_func():
            event.wait(timeout=5)

        task_pk = run_in_background("test_task", blocking_func)
        task = Task.objects.get(pk=task_pk)

        assert task.task_type == "test_task"
        assert task.status in ("pending", "running")
        event.set()

    def test_task_transitions_to_completed(self):
        """A successful target function should set status to completed."""

        def simple_func():
            return {"result": "ok"}

        task_pk = run_in_background("test_complete", simple_func)
        task = _wait_for_status(task_pk, "completed")

        assert task.status == "completed"
        assert task.progress == 100
        assert task.result_data == {"result": "ok"}

    def test_task_transitions_to_failed_on_exception(self):
        """An exception in the target function should set status to failed."""

        def failing_func():
            raise ValueError("Something went wrong")

        task_pk = run_in_background("test_fail", failing_func)
        task = _wait_for_status(task_pk, "failed")

        assert task.status == "failed"
        assert "Something went wrong" in task.error_message

    def test_stores_related_object_metadata(self):
        """run_in_background should store related_object_id and type."""
        event = threading.Event()

        def blocking_func():
            event.wait(timeout=5)

        task_pk = run_in_background(
            "test_related",
            blocking_func,
            related_object_id=42,
            related_object_type="Clip",
        )
        task = Task.objects.get(pk=task_pk)

        assert task.related_object_id == 42
        assert task.related_object_type == "Clip"
        event.set()

    def test_passes_args_to_target_func(self):
        """Positional and keyword args should be forwarded to target_func."""
        received = {}

        def capture_args(a, b, key=None):
            received["a"] = a
            received["b"] = b
            received["key"] = key

        task_pk = run_in_background("test_args", capture_args, 1, 2, key="value")
        _wait_for_status(task_pk, "completed")

        assert received == {"a": 1, "b": 2, "key": "value"}

    def test_non_dict_result_stores_none(self):
        """When target_func returns a non-dict/list, result_data is None."""

        def returns_string():
            return "just a string"

        task_pk = run_in_background("test_string_result", returns_string)
        task = _wait_for_status(task_pk, "completed")

        assert task.status == "completed"
        assert task.result_data is None


class TestTaskStatusEndpoint:
    """Tests for the GET /api/tasks/<id>/status/ endpoint."""

    def test_returns_task_json(self, db, client):
        """Should return task fields as JSON for an existing task."""
        task = Task.objects.create(
            task_type="test_poll",
            status="running",
            progress=45,
        )

        response = client.get(f"/api/tasks/{task.pk}/status/")

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data["id"] == task.pk
        assert data["task_type"] == "test_poll"
        assert data["status"] == "running"
        assert data["progress"] == 45
        assert data["result_data"] is None
        assert data["error_message"] == ""

    def test_returns_404_for_missing_task(self, db, client):
        """Should return 404 for a non-existent task ID."""
        response = client.get("/api/tasks/99999/status/")
        assert response.status_code == 404

    def test_returns_completed_task_with_result(self, db, client):
        """Should include result_data when task has completed."""
        task = Task.objects.create(
            task_type="test_done",
            status="completed",
            progress=100,
            result_data={"video_path": "/media/videos/test.mp4"},
        )

        response = client.get(f"/api/tasks/{task.pk}/status/")

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data["status"] == "completed"
        assert data["result_data"] == {"video_path": "/media/videos/test.mp4"}

    def test_returns_failed_task_with_error(self, db, client):
        """Should include error_message when task has failed."""
        task = Task.objects.create(
            task_type="test_error",
            status="failed",
            error_message="API rate limit exceeded",
        )

        response = client.get(f"/api/tasks/{task.pk}/status/")

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data["status"] == "failed"
        assert data["error_message"] == "API rate limit exceeded"

    def test_pending_task_returns_zero_progress(self, db, client):
        """A pending task should have progress=0."""
        task = Task.objects.create(
            task_type="test_pending",
            status="pending",
        )

        response = client.get(f"/api/tasks/{task.pk}/status/")

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data["status"] == "pending"
        assert data["progress"] == 0


@pytest.mark.django_db(transaction=True)
class TestTaskStatusEndpointIntegration:
    """Integration test: run_in_background → poll status endpoint."""

    def test_full_lifecycle_via_api(self, client):
        """Create a task, let it complete, then verify status via API."""

        def quick_task():
            return {"done": True}

        task_pk = run_in_background("integration_test", quick_task)

        # Wait for completion via API polling
        data = None
        for _ in range(50):
            response = client.get(f"/api/tasks/{task_pk}/status/")
            data = json.loads(response.content)
            if data["status"] == "completed":
                break
            time.sleep(0.1)

        assert data["status"] == "completed"
        assert data["progress"] == 100
        assert data["result_data"] == {"done": True}

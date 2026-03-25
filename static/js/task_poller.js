/**
 * Task Poller — Peliku
 * jQuery-based polling mechanism for tracking background task status.
 * Polls the /api/tasks/<id>/status/ endpoint at a fixed interval
 * and invokes callbacks based on status transitions.
 */

const TaskPoller = (function ($) {
  "use strict";

  /* ── Constants ── */
  var POLL_INTERVAL_MS = 2000;

  /**
   * Start polling a background task for status updates.
   *
   * @param {number} taskId       - The ID of the Task to poll.
   * @param {Object} callbacks    - Callback functions for status events.
   * @param {Function} [callbacks.onProgress]  - Called with task data while running.
   * @param {Function} [callbacks.onComplete]  - Called with task data on completion.
   * @param {Function} [callbacks.onError]     - Called with task data on failure.
   * @returns {Object} A handle with a `stop()` method to cancel polling.
   */
  function pollTask(taskId, callbacks) {
    var onProgress = callbacks.onProgress || $.noop;
    var onComplete = callbacks.onComplete || $.noop;
    var onError = callbacks.onError || $.noop;

    var intervalId = null;
    var startTime = Date.now();
    var stopped = false;

    function getElapsedSeconds() {
      return Math.floor((Date.now() - startTime) / 1000);
    }

    function poll() {
      if (stopped) {
        return;
      }

      $.ajax({
        url: "/api/tasks/" + taskId + "/status/",
        method: "GET",
        dataType: "json",
        success: function (data) {
          if (stopped) {
            return;
          }

          data.elapsed_seconds = getElapsedSeconds();

          if (data.status === "completed") {
            stop();
            onComplete(data);
          } else if (data.status === "failed") {
            stop();
            onError(data);
          } else {
            onProgress(data);
          }
        },
        error: function () {
          if (stopped) {
            return;
          }
          stop();
          onError({
            id: taskId,
            status: "failed",
            error_message: "Lost connection while checking task status.",
            elapsed_seconds: getElapsedSeconds(),
          });
        },
      });
    }

    function stop() {
      stopped = true;
      if (intervalId !== null) {
        clearInterval(intervalId);
        intervalId = null;
      }
    }

    /* Kick off the first poll immediately, then repeat on interval */
    poll();
    intervalId = setInterval(poll, POLL_INTERVAL_MS);

    return { stop: stop };
  }

  /**
   * Format elapsed seconds into a human-readable string.
   *
   * @param {number} seconds - Total seconds elapsed.
   * @returns {string} Formatted time string (e.g. "1m 23s" or "45s").
   */
  function formatElapsed(seconds) {
    if (seconds < 60) {
      return seconds + "s";
    }
    var minutes = Math.floor(seconds / 60);
    var remaining = seconds % 60;
    return minutes + "m " + remaining + "s";
  }

  return {
    pollTask: pollTask,
    formatElapsed: formatElapsed,
  };
})(jQuery);

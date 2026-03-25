/**
 * Workspace JS — Peliku
 * jQuery handlers for the Project Workspace page.
 * Handles Reference Images Panel toggle, inline script editing,
 * auto-save via AJAX, live character counts, and video generation.
 */

const Workspace = (function ($) {
  "use strict";

  /* ── Constants ── */
  const DEBOUNCE_DELAY_MS = 5000;
  const SAVED_INDICATOR_DURATION_MS = 3000;

  /* ── Debounce timers keyed by clip ID ── */
  var debounceTimers = {};

  /* ── Generation timers keyed by clip ID ── */
  var genTimers = {};

  /**
   * Retrieve the CSRF token from the hidden csrf_token input in the page.
   * @returns {string} The CSRF token value.
   */
  function getCsrfToken() {
    return $("[name=csrfmiddlewaretoken]").val();
  }

  /**
   * Bind the Reference Images Panel expand/collapse toggle.
   * Toggles the hidden attribute on the body and aria-expanded on the button.
   */
  function bindRefPanelToggle() {
    $(".js-ref-toggle").on("click", function () {
      const $btn = $(this);
      const $body = $(".js-ref-body");
      const isExpanded = $btn.attr("aria-expanded") === "true";

      if (isExpanded) {
        $body.attr("hidden", "");
        $btn.attr("aria-expanded", "false");
      } else {
        $body.removeAttr("hidden");
        $btn.attr("aria-expanded", "true");
      }
    });
  }

  /**
   * Bind live character count updates on clip script textareas.
   */
  function bindScriptCharCount() {
    $(".clip-card__script").on("input", function () {
      var $textarea = $(this);
      var $group = $textarea.closest(".form-group");
      var $current = $group.find(".js-char-current");
      $current.text($textarea.val().length);
    });
  }

  /**
   * Save a clip's script via AJAX POST.
   * @param {jQuery} $textarea - The textarea element.
   */
  function saveClipScript($textarea) {
    var $card = $textarea.closest(".clip-card");
    var clipId = $card.data("clip-id");
    var $status = $card.find(".js-save-status");

    if (!clipId) {
      return;
    }

    var scriptText = $textarea.val();

    $status.text("Saving\u2026").removeClass("save-status--saved save-status--error");

    $.ajax({
      url: "/api/clips/" + clipId + "/update-script/",
      method: "POST",
      contentType: "application/json",
      headers: { "X-CSRFToken": getCsrfToken() },
      data: JSON.stringify({ script_text: scriptText }),
      success: function () {
        $status
          .text("Saved")
          .removeClass("save-status--error")
          .addClass("save-status--saved");
        clearSavedIndicator($status);
      },
      error: function () {
        $status
          .text("Save failed")
          .removeClass("save-status--saved")
          .addClass("save-status--error");
      },
    });
  }

  /**
   * Clear the "Saved" indicator after a delay.
   * @param {jQuery} $status - The status element.
   */
  function clearSavedIndicator($status) {
    setTimeout(function () {
      if ($status.text() === "Saved") {
        $status.text("").removeClass("save-status--saved");
      }
    }, SAVED_INDICATOR_DURATION_MS);
  }

  /**
   * Bind auto-save: save on blur and debounced save while typing.
   */
  function bindAutoSave() {
    $(".clip-card__script").on("blur", function () {
      var $textarea = $(this);
      var clipId = $textarea.closest(".clip-card").data("clip-id");
      if (clipId && debounceTimers[clipId]) {
        clearTimeout(debounceTimers[clipId]);
        delete debounceTimers[clipId];
      }
      saveClipScript($textarea);
    });

    $(".clip-card__script").on("input", function () {
      var $textarea = $(this);
      var clipId = $textarea.closest(".clip-card").data("clip-id");

      if (!clipId) {
        return;
      }

      if (debounceTimers[clipId]) {
        clearTimeout(debounceTimers[clipId]);
      }

      debounceTimers[clipId] = setTimeout(function () {
        saveClipScript($textarea);
        delete debounceTimers[clipId];
      }, DEBOUNCE_DELAY_MS);
    });
  }

  /* ── Video Generation ── */

  /**
   * Switch the visible state panel within a clip card's right column.
   * @param {jQuery} $right - The .clip-card__right element.
   * @param {string} state - One of "idle", "generating", "completed", "failed".
   */
  function showState($right, state) {
    $right.find(".clip-card__state").addClass("hidden");
    $right.find(".clip-card__state--" + state).removeClass("hidden");
    $right.attr("data-status", state);
  }

  /**
   * Start the elapsed-time counter for a generating clip.
   * @param {jQuery} $right - The .clip-card__right element.
   * @param {number} clipId - The clip primary key.
   */
  function startGenTimer($right, clipId) {
    stopGenTimer(clipId);
    var startTime = Date.now();
    var $timer = $right.find(".js-gen-timer");

    genTimers[clipId] = setInterval(function () {
      var elapsed = Math.floor((Date.now() - startTime) / 1000);
      var minutes = Math.floor(elapsed / 60);
      var seconds = elapsed % 60;
      $timer.text(minutes + ":" + (seconds < 10 ? "0" : "") + seconds);
    }, 1000);
  }

  /**
   * Stop the elapsed-time counter for a clip.
   * @param {number} clipId - The clip primary key.
   */
  function stopGenTimer(clipId) {
    if (genTimers[clipId]) {
      clearInterval(genTimers[clipId]);
      delete genTimers[clipId];
    }
  }

  /**
   * Trigger video generation for a clip.
   * @param {jQuery} $card - The .clip-card article element.
   */
  function generateVideo($card) {
    var clipId = $card.data("clip-id");
    var clipNum = $card.data("clip");
    var $right = $card.find(".clip-card__right");

    showState($right, "generating");
    startGenTimer($right, clipId);

    $.ajax({
      url: "/api/clips/" + clipId + "/generate-video/",
      method: "POST",
      contentType: "application/json",
      headers: { "X-CSRFToken": getCsrfToken() },
      data: JSON.stringify({}),
      success: function (data) {
        TaskPoller.pollTask(data.task_id, {
          onProgress: function () {
            /* Timer is already running — nothing extra needed */
          },
          onComplete: function (taskData) {
            stopGenTimer(clipId);
            handleGenerationComplete($card, $right, clipNum, taskData);
          },
          onError: function (taskData) {
            stopGenTimer(clipId);
            handleGenerationFailed($right, taskData);
          },
        });
      },
      error: function (xhr) {
        stopGenTimer(clipId);
        var msg = "Could not start video generation.";
        try {
          var body = JSON.parse(xhr.responseText);
          if (body.error) {
            msg = body.error;
          }
        } catch (e) {
          /* use default message */
        }
        $right.find(".js-error-text").text(msg);
        showState($right, "failed");
      },
    });
  }

  /**
   * Handle successful video generation: update UI with video player.
   * @param {jQuery} $card - The clip card element.
   * @param {jQuery} $right - The right panel element.
   * @param {number} clipNum - The clip sequence number.
   * @param {Object} taskData - Task result data from the poller.
   */
  function handleGenerationComplete($card, $right, clipNum, taskData) {
    var videoUrl = "";
    if (taskData.result_data && taskData.result_data.video_url) {
      videoUrl = taskData.result_data.video_url;
    }

    var $completed = $right.find(".clip-card__state--completed");
    $completed.find(".js-clip-video, .clip-card__video-placeholder").remove();

    if (videoUrl) {
      var $video = $(
        '<video class="clip-card__video js-clip-video" muted autoplay loop playsinline></video>'
      );
      $video.attr("src", videoUrl);
      $video.attr(
        "aria-label",
        "Generated video for clip " + clipNum
      );
      $completed
        .find(".btn")
        .first()
        .before($video);
    }

    showState($right, "completed");

    if (typeof Peliku !== "undefined" && Peliku.Toast) {
      Peliku.Toast.show(
        "Clip " + clipNum + " generated successfully",
        "success"
      );
    }
  }

  /**
   * Handle failed video generation: show error message.
   * @param {jQuery} $right - The right panel element.
   * @param {Object} taskData - Task data from the poller.
   */
  function handleGenerationFailed($right, taskData) {
    var errorMsg =
      "We couldn\u2019t generate this video. Try adjusting the script and click Retry.";
    if (taskData.error_message) {
      errorMsg = taskData.error_message;
    }
    $right.find(".js-error-text").text(errorMsg);
    showState($right, "failed");

    if (typeof Peliku !== "undefined" && Peliku.Toast) {
      Peliku.Toast.show("Video generation failed", "error");
    }
  }

  /**
   * Bind click handlers for all Generate Video / Regenerate / Retry buttons.
   */
  function bindGenerateVideo() {
    $(document).on("click", ".js-generate-video", function () {
      var $card = $(this).closest(".clip-card");
      generateVideo($card);
    });
  }

  return {
    init: function () {
      bindRefPanelToggle();
      bindScriptCharCount();
      bindAutoSave();
      bindGenerateVideo();
    },
  };
})(jQuery);

$(document).ready(function () {
  Workspace.init();
});

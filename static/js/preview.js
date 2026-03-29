/**
 * Preview JS — Peliku
 * Full-screen reel preview with sequential clip playback and timeline scrubber.
 * Loads clip video URLs from the preview-data API end plays them in order.
 */

var ReelPreview = (function ($) {
  "use strict";

  /* ── State ── */
  var projectId = null;
  var segments = [];
  var currentIndex = 0;
  var isPlaying = false;
  var progressTimer = null;

  /* ── DOM references (set once on init) ── */
  var $overlay = null;
  var $video = null;
  var $placeholder = null;
  var $playBtn = null;
  var $pauseBtn = null;
  var $restartBtn = null;
  var $currentTime = null;
  var $totalTime = null;
  var $scrubberTrack = null;
  var $progress = null;

  /**
   * Format seconds into M:SS display string.
   * @param {number} seconds - Total seconds to format.
   * @returns {string} Formatted time string.
   */
  function formatTime(seconds) {
    var secs = Math.max(0, Math.floor(seconds));
    var m = Math.floor(secs / 60);
    var s = secs % 60;
    return m + ":" + (s < 10 ? "0" : "") + s;
  }

  /**
   * Calculate total duration of all playable segments.
   * @returns {number} Total seconds.
   */
  function getTotalDuration() {
    var total = 0;
    for (var i = 0; i < segments.length; i++) {
      total += segments[i].duration;
    }
    return total;
  }

  /**
   * Calculate the elapsed time up to the start of a given segment index.
   * @param {number} index - The segment index.
   * @returns {number} Seconds elapsed before this segment.
   */
  function getElapsedBefore(index) {
    var elapsed = 0;
    for (var i = 0; i < index && i < segments.length; i++) {
      elapsed += segments[i].duration;
    }
    return elapsed;
  }

  /**
   * Build the scrubber bar with segment markers.
   * Each segment is a clickable section proportional to its duration.
   */
  function buildScrubber() {
    $scrubberTrack.empty();
    $progress = $(
      '<div class="preview-overlay__scrubber-progress js-preview-progress"></div>'
    );
    $scrubberTrack.append($progress);

    var total = getTotalDuration();
    if (total <= 0) {
      return;
    }

    var cumulative = 0;
    for (var i = 0; i < segments.length; i++) {
      var seg = segments[i];
      var leftPct = (cumulative / total) * 100;
      var widthPct = (seg.duration / total) * 100;
      cumulative += seg.duration;

      var $segment = $(
        '<div class="preview-overlay__scrubber-segment" ' +
          'data-index="' + i + '" ' +
          'title="' + seg.label + '">' +
          "</div>"
      );
      $segment.css({
        position: "absolute",
        left: leftPct + "%",
        width: widthPct + "%",
        height: "100%",
        cursor: "pointer",
      });

      if (!seg.video_url) {
        $segment.addClass("preview-overlay__scrubber-segment--empty");
      }

      $scrubberTrack.append($segment);

      if (i < segments.length - 1) {
        var $marker = $(
          '<div class="preview-overlay__scrubber-marker" aria-hidden="true"></div>'
        );
        $marker.css({ left: (cumulative / total) * 100 + "%" });
        $scrubberTrack.append($marker);
      }
    }
  }

  /**
   * Update the progress bar position and time display.
   */
  function updateProgress() {
    var videoEl = $video[0];
    if (!videoEl || segments.length === 0) {
      return;
    }

    var elapsed = getElapsedBefore(currentIndex);
    if (segments[currentIndex] && segments[currentIndex].video_url && !videoEl.paused) {
      elapsed += videoEl.currentTime || 0;
    }

    var total = getTotalDuration();
    var pct = total > 0 ? (elapsed / total) * 100 : 0;
    $progress.css("width", Math.min(pct, 100) + "%");
    $currentTime.text(formatTime(elapsed));
    $totalTime.text(formatTime(total));
  }

  /**
   * Start the progress update timer.
   */
  function startProgressTimer() {
    stopProgressTimer();
    progressTimer = setInterval(updateProgress, 250);
  }

  /**
   * Stop the progress update timer.
   */
  function stopProgressTimer() {
    if (progressTimer) {
      clearInterval(progressTimer);
      progressTimer = null;
    }
  }

  /**
   * Play the segment at the given index.
   * Skips segments without video and advances to the next.
   * @param {number} index - The segment index to play.
   */
  function playSegment(index) {
    if (index >= segments.length) {
      handlePlaybackEnd();
      return;
    }

    currentIndex = index;
    var seg = segments[index];

    highlightSegment(index);

    if (!seg.video_url) {
      playSegment(index + 1);
      return;
    }

    var videoEl = $video[0];
    $placeholder.addClass("hidden");
    $video.removeClass("hidden");

    videoEl.src = seg.video_url;
    videoEl.load();

    var playPromise = videoEl.play();
    if (playPromise && typeof playPromise.then === "function") {
      playPromise.catch(function () {
        /* Autoplay may be blocked — user can click play manually */
      });
    }

    isPlaying = true;
    showPauseBtn();
    startProgressTimer();
  }

  /**
   * Highlight the active segment in the scrubber.
   * @param {number} index - The segment index to highlight.
   */
  function highlightSegment(index) {
    $scrubberTrack
      .find(".preview-overlay__scrubber-segment")
      .removeClass("is-active");
    $scrubberTrack
      .find('.preview-overlay__scrubber-segment[data-index="' + index + '"]')
      .addClass("is-active");
  }

  /**
   * Handle the end of a single clip — advance to next segment.
   */
  function handleClipEnd() {
    playSegment(currentIndex + 1);
  }

  /**
   * Handle the end of full reel playback.
   */
  function handlePlaybackEnd() {
    isPlaying = false;
    stopProgressTimer();
    showPlayBtn();
    updateProgress();
  }

  /**
   * Show the play button, hide the pause button.
   */
  function showPlayBtn() {
    $playBtn.removeClass("hidden");
    $pauseBtn.addClass("hidden");
  }

  /**
   * Show the pause button, hide the play button.
   */
  function showPauseBtn() {
    $pauseBtn.removeClass("hidden");
    $playBtn.addClass("hidden");
  }

  /**
   * Open the preview overlay and load clip data.
   * @param {number} projId - The project primary key.
   */
  function open(projId) {
    projectId = projId;
    $overlay.addClass("is-active").attr("aria-hidden", "false");

    $("body").css("overflow", "hidden");

    $.ajax({
      url: "/api/projects/" + projectId + "/preview-data/",
      method: "GET",
      success: function (data) {
        loadPreviewData(data);
      },
      error: function () {
        if (typeof Peliku !== "undefined" && Peliku.Toast) {
          Peliku.Toast.show("Could not load preview data", "error");
        }
      },
    });
  }

  /**
   * Load the preview data and set up the player.
   * @param {Object} data - Response from the preview-data endpoint.
   */
  function loadPreviewData(data) {
    segments = [];

    if (data.hook && data.hook.is_enabled && data.hook.video_url) {
      segments.push({
        video_url: data.hook.video_url,
        duration: data.hook.duration || 4,
        label: "Hook",
      });
    }

    var clips = data.clips || [];
    for (var i = 0; i < clips.length; i++) {
      segments.push({
        video_url: clips[i].video_url,
        duration: clips[i].duration,
        label: "Clip " + clips[i].sequence_number,
      });
    }

    var aspectRatio = data.aspect_ratio || "9:16";
    if (aspectRatio === "16:9") {
      $video.css({ "max-width": "100%", "aspect-ratio": "16 / 9" });
      $placeholder.css("aspect-ratio", "16 / 9").css("max-width", "100%");
    } else {
      $video.css({ "max-width": "270px", "aspect-ratio": "9 / 16" });
      $placeholder.css("aspect-ratio", "9 / 16").css("max-width", "270px");
    }

    $totalTime.text(formatTime(getTotalDuration()));
    $currentTime.text(formatTime(0));

    buildScrubber();

    var hasVideo = false;
    for (var j = 0; j < segments.length; j++) {
      if (segments[j].video_url) {
        hasVideo = true;
        break;
      }
    }

    if (!hasVideo) {
      $video.addClass("hidden");
      $placeholder.removeClass("hidden");
      $placeholder
        .find(".preview-overlay__hint")
        .text("No clips have been generated yet. Generate at least one clip to preview.");
    } else {
      $placeholder.addClass("hidden");
      $video.addClass("hidden");
      showPlayBtn();
    }
  }

  /**
   * Close the preview overlay and reset state.
   */
  function close() {
    var videoEl = $video[0];
    if (videoEl) {
      videoEl.pause();
      videoEl.removeAttribute("src");
      videoEl.load();
    }

    isPlaying = false;
    currentIndex = 0;
    segments = [];
    stopProgressTimer();

    $overlay.removeClass("is-active").attr("aria-hidden", "true");
    $("body").css("overflow", "");

    $video.addClass("hidden");
    $placeholder.removeClass("hidden");
    $progress.css("width", "0%");
    showPlayBtn();
  }

  /**
   * Bind all preview-related event handlers.
   */
  function bindEvents() {
    $(document).on("click", ".js-preview-close, .js-preview-close-btn", function () {
      close();
    });

    $(document).on("keydown", function (e) {
      if (e.key === "Escape" && $overlay.hasClass("is-active")) {
        close();
      }
    });

    $(document).on("click", ".js-preview-play", function () {
      if (segments.length === 0) {
        return;
      }
      if (currentIndex >= segments.length) {
        currentIndex = 0;
      }
      playSegment(currentIndex);
    });

    $(document).on("click", ".js-preview-pause", function () {
      var videoEl = $video[0];
      if (videoEl) {
        videoEl.pause();
      }
      isPlaying = false;
      stopProgressTimer();
      showPlayBtn();
    });

    $(document).on("click", ".js-preview-restart", function () {
      currentIndex = 0;
      $progress.css("width", "0%");
      $currentTime.text(formatTime(0));
      playSegment(0);
    });

    $(document).on("click", ".preview-overlay__scrubber-segment", function () {
      var index = parseInt($(this).data("index"), 10);
      if (isNaN(index) || index < 0 || index >= segments.length) {
        return;
      }
      currentIndex = index;
      playSegment(index);
    });
  }

  /**
   * Bind the video "ended" event for sequential playback.
   */
  function bindVideoEvents() {
    $video.on("ended", function () {
      handleClipEnd();
    });
  }

  /**
   * Bind the Preview Reel button in the workspace header.
   */
  function bindPreviewButton() {
    $(document).on("click", ".js-preview-toggle", function () {
      var $btn = $(this);
      if ($btn.prop("disabled")) {
        return;
      }
      var projId =
        $(".js-clip-list").data("project-id") ||
        $(".ref-panel").data("project-id");
      if (projId) {
        open(projId);
      }
    });
  }

  return {
    init: function () {
      $overlay = $(".js-preview-overlay");
      $video = $overlay.find(".js-preview-video");
      $placeholder = $overlay.find(".js-preview-placeholder");
      $playBtn = $overlay.find(".js-preview-play");
      $pauseBtn = $overlay.find(".js-preview-pause");
      $restartBtn = $overlay.find(".js-preview-restart");
      $currentTime = $overlay.find(".js-preview-current-time");
      $totalTime = $overlay.find(".js-preview-total-time");
      $scrubberTrack = $overlay.find(".js-preview-scrubber-track");
      $progress = $overlay.find(".js-preview-progress");

      bindEvents();
      bindVideoEvents();
      bindPreviewButton();
    },
  };
})(jQuery);

$(document).ready(function () {
  ReelPreview.init();
});

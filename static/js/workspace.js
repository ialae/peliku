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
      data: JSON.stringify({ method: getClipMethod($card) }),
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

  /* ── Reference Images Panel ── */

  /**
   * Get the project ID from the reference panel data attribute.
   * @returns {number} The project primary key.
   */
  function getProjectId() {
    return $(".ref-panel").data("project-id");
  }

  /**
   * Update the reference count badge in the panel toggle.
   */
  function updateRefCount() {
    var filled = $(".ref-slot__preview--filled").length;
    $(".js-ref-count").text(filled + " / 3");
  }

  /**
   * Render a filled reference slot after generate or upload.
   * @param {jQuery} $slot - The .js-ref-slot element.
   * @param {Object} data - The response data with id, label, image_url.
   */
  function renderFilledSlot($slot, data) {
    $slot.find(".ref-slot__empty").addClass("hidden");
    $slot.find(".ref-slot__preview--filled, .ref-slot__label-input").remove();

    var $preview = $(
      '<div class="ref-slot__preview ref-slot__preview--filled" data-ref-id="' +
        data.id +
        '">' +
        '<img src="' +
        data.image_url +
        '" alt="' +
        $("<span>").text(data.label).html() +
        '" class="ref-slot__img">' +
        '<button type="button" class="ref-slot__remove js-ref-remove" aria-label="Remove reference image">' +
        '<i class="ph ph-x" aria-hidden="true"></i>' +
        "</button>" +
        "</div>"
    );
    var $label = $(
      '<input type="text" class="form-input form-input--sm ref-slot__label-input" ' +
        'value="' +
        $("<span>").text(data.label).html() +
        '" maxlength="100" readonly>'
    );

    $slot.prepend($label).prepend($preview);
    updateRefCount();
    updateAllClipRefCheckboxes(data.id, data.label, data.image_url);
  }

  /**
   * Reset a slot to its empty state.
   * @param {jQuery} $slot - The .js-ref-slot element.
   */
  function clearSlot($slot) {
    var $filled = $slot.find(".ref-slot__preview--filled");
    var refId = $filled.data("ref-id");
    $filled.remove();
    $slot.find(".ref-slot__label-input").remove();
    $slot.find(".ref-slot__empty").removeClass("hidden");
    updateRefCount();
    if (refId) {
      removeRefFromAllClips(refId);
    }
  }

  /**
   * Add a new reference checkbox to all clip sections.
   * @param {number} refId - The reference image PK.
   * @param {string} label - The reference label.
   * @param {string} imageUrl - The image URL for the thumbnail.
   */
  function updateAllClipRefCheckboxes(refId, label, imageUrl) {
    $(".js-clip-refs").each(function () {
      var $list = $(this).find(".clip-refs__list");
      $list.find(".clip-refs__empty").remove();

      if ($list.find('.js-ref-checkbox[value="' + refId + '"]').length > 0) {
        return;
      }

      var escapedLabel = $("<span>").text(label).html();
      var $item = $(
        '<label class="clip-refs__item">' +
          '<input type="checkbox" class="clip-refs__checkbox js-ref-checkbox" value="' +
          refId +
          '" aria-label="Include ' +
          escapedLabel +
          '">' +
          '<img src="' +
          imageUrl +
          '" alt="' +
          escapedLabel +
          '" class="clip-refs__thumb">' +
          '<span class="clip-refs__name">' +
          escapedLabel +
          "</span>" +
          "</label>"
      );
      $list.append($item);
    });
  }

  /**
   * Remove a reference checkbox from all clip sections.
   * @param {number} refId - The reference image PK to remove.
   */
  function removeRefFromAllClips(refId) {
    $(".js-clip-refs").each(function () {
      var $list = $(this).find(".clip-refs__list");
      $list
        .find('.js-ref-checkbox[value="' + refId + '"]')
        .closest(".clip-refs__item")
        .remove();

      if ($list.find(".clip-refs__item").length === 0) {
        $list.append(
          '<p class="body-small clip-refs__empty">No references defined yet.</p>'
        );
      }
    });
  }

  /**
   * Bind the "Generate" button on empty reference slots.
   * Shows a prompt input inline, then POSTs to generate endpoint.
   */
  function bindRefGenerate() {
    $(document).on("click", ".js-ref-generate", function () {
      var $slot = $(this).closest(".js-ref-slot");
      var slotNum = parseInt($slot.data("slot"), 10);

      var promptText = window.prompt("Describe the reference image:");
      if (!promptText || !promptText.trim()) {
        return;
      }

      var label = window.prompt("Label for this reference (e.g., Main character):");
      if (!label || !label.trim()) {
        return;
      }

      var $btn = $slot.find(".js-ref-generate");
      $btn.prop("disabled", true).text("Generating\u2026");

      $.ajax({
        url:
          "/api/projects/" + getProjectId() + "/references/generate/",
        method: "POST",
        contentType: "application/json",
        headers: { "X-CSRFToken": getCsrfToken() },
        data: JSON.stringify({
          slot_number: slotNum,
          prompt: promptText.trim(),
          label: label.trim(),
        }),
        success: function (data) {
          if (data.task_id) {
            TaskPoller.pollTask(data.task_id, {
              onComplete: function (taskData) {
                renderFilledSlot($slot, taskData.result_data);
                $btn.prop("disabled", false).html(
                  '<i class="ph ph-sparkle" aria-hidden="true"></i> Generate'
                );
              },
              onError: function () {
                $btn.prop("disabled", false).html(
                  '<i class="ph ph-sparkle" aria-hidden="true"></i> Generate'
                );
                window.alert("Image generation failed. Please try again.");
              },
            });
          }
        },
        error: function () {
          $btn.prop("disabled", false).html(
            '<i class="ph ph-sparkle" aria-hidden="true"></i> Generate'
          );
          window.alert("Could not start image generation.");
        },
      });
    });
  }

  /**
   * Bind the file upload input on empty reference slots.
   */
  function bindRefUpload() {
    $(document).on("change", ".js-ref-upload-input", function () {
      var $input = $(this);
      var file = $input[0].files[0];
      if (!file) {
        return;
      }

      var $slot = $input.closest(".js-ref-slot");
      var slotNum = parseInt($slot.data("slot"), 10);

      var label = window.prompt("Label for this reference (e.g., Main character):");
      if (!label || !label.trim()) {
        $input.val("");
        return;
      }

      var formData = new FormData();
      formData.append("slot_number", slotNum);
      formData.append("label", label.trim());
      formData.append("image", file);

      $.ajax({
        url:
          "/api/projects/" + getProjectId() + "/references/upload/",
        method: "POST",
        headers: { "X-CSRFToken": getCsrfToken() },
        data: formData,
        processData: false,
        contentType: false,
        success: function (data) {
          renderFilledSlot($slot, data);
        },
        error: function (xhr) {
          var msg = "Upload failed.";
          try {
            var body = JSON.parse(xhr.responseText);
            if (body.error) {
              msg = body.error;
            }
          } catch (e) {
            /* use default */
          }
          window.alert(msg);
        },
      });

      $input.val("");
    });
  }

  /**
   * Bind the remove button on filled reference slots.
   */
  function bindRefRemove() {
    $(document).on("click", ".js-ref-remove", function (e) {
      e.stopPropagation();
      var $slot = $(this).closest(".js-ref-slot");
      var slotNum = parseInt($slot.data("slot"), 10);

      $.ajax({
        url:
          "/api/projects/" +
          getProjectId() +
          "/references/" +
          slotNum +
          "/delete/",
        method: "POST",
        headers: { "X-CSRFToken": getCsrfToken() },
        success: function () {
          clearSlot($slot);
        },
        error: function () {
          window.alert("Could not remove reference image.");
        },
      });
    });
  }

  /**
   * Bind per-clip reference checkbox changes.
   */
  function bindClipRefCheckboxes() {
    $(document).on("change", ".js-ref-checkbox", function () {
      var $refs = $(this).closest(".js-clip-refs");
      saveClipReferences($refs);
    });
  }

  /**
   * Bind the "Select All" button for per-clip references.
   */
  function bindRefSelectAll() {
    $(document).on("click", ".js-ref-select-all", function () {
      var $refs = $(this).closest(".js-clip-refs");
      $refs.find(".js-ref-checkbox").prop("checked", true);
      saveClipReferences($refs);
    });
  }

  /**
   * Save the selected reference IDs for a clip via AJAX.
   * @param {jQuery} $refs - The .js-clip-refs container.
   */
  function saveClipReferences($refs) {
    var clipId = $refs.data("clip-id");
    var ids = [];
    $refs.find(".js-ref-checkbox:checked").each(function () {
      ids.push(parseInt($(this).val(), 10));
    });

    $.ajax({
      url: "/api/clips/" + clipId + "/update-references/",
      method: "POST",
      contentType: "application/json",
      headers: { "X-CSRFToken": getCsrfToken() },
      data: JSON.stringify({ reference_ids: ids }),
    });
  }

  /* ── Generation Method Switching ── */

  /**
   * Get the selected generation method for a clip card.
   * @param {jQuery} $card - The .clip-card article element.
   * @returns {string} The selected generation method value.
   */
  function getClipMethod($card) {
    return $card.find(".js-gen-method").val() || "text_to_video";
  }

  /**
   * Bind generation method dropdown change handler.
   * Toggles the first-frame panel visibility and saves the selection.
   */
  function bindGenMethodChange() {
    $(document).on("change", ".js-gen-method", function () {
      var $select = $(this);
      var $card = $select.closest(".clip-card");
      var clipId = $card.data("clip-id");
      var method = $select.val();

      var $firstFramePanel = $card.find(".js-first-frame-panel");
      var $lastFramePanel = $card.find(".js-last-frame-panel");

      if (method === "image_to_video") {
        $firstFramePanel.removeClass("hidden");
        $lastFramePanel.addClass("hidden");
      } else if (method === "frame_interpolation") {
        $firstFramePanel.removeClass("hidden");
        $lastFramePanel.removeClass("hidden");
      } else {
        $firstFramePanel.addClass("hidden");
        $lastFramePanel.addClass("hidden");
      }

      $.ajax({
        url: "/api/clips/" + clipId + "/update-method/",
        method: "POST",
        contentType: "application/json",
        headers: { "X-CSRFToken": getCsrfToken() },
        data: JSON.stringify({ method: method }),
      });
    });
  }

  /* ── First Frame Management ── */

  /**
   * Render a first-frame image into the preview area.
   * @param {jQuery} $panel - The .js-first-frame-panel element.
   * @param {string} imageUrl - The URL of the first-frame image.
   */
  function renderFirstFrame($panel, imageUrl) {
    var $preview = $panel.find(".js-first-frame-preview");
    $preview.html(
      '<img src="' +
        imageUrl +
        '" alt="First frame" class="first-frame-panel__img">'
    );
  }

  /**
   * Bind the "Generate Image" button in the first-frame panel.
   */
  function bindFirstFrameGenerate() {
    $(document).on("click", ".js-first-frame-generate", function () {
      var $btn = $(this);
      var $panel = $btn.closest(".js-first-frame-panel");
      var clipId = $panel.data("clip-id");

      $btn.prop("disabled", true).text("Generating\u2026");

      $.ajax({
        url: "/api/clips/" + clipId + "/set-first-frame/",
        method: "POST",
        contentType: "application/json",
        headers: { "X-CSRFToken": getCsrfToken() },
        data: JSON.stringify({ source: "generate" }),
        success: function (data) {
          if (data.task_id) {
            TaskPoller.pollTask(data.task_id, {
              onComplete: function (taskData) {
                var imageUrl =
                  taskData.result_data && taskData.result_data.image_url
                    ? taskData.result_data.image_url
                    : "";
                if (imageUrl) {
                  renderFirstFrame($panel, imageUrl);
                }
                $btn.prop("disabled", false).html(
                  '<i class="ph ph-sparkle" aria-hidden="true"></i> Generate Image'
                );
                if (typeof Peliku !== "undefined" && Peliku.Toast) {
                  Peliku.Toast.show("First frame generated", "success");
                }
              },
              onError: function () {
                $btn.prop("disabled", false).html(
                  '<i class="ph ph-sparkle" aria-hidden="true"></i> Generate Image'
                );
                if (typeof Peliku !== "undefined" && Peliku.Toast) {
                  Peliku.Toast.show("First frame generation failed", "error");
                }
              },
            });
          }
        },
        error: function (xhr) {
          $btn.prop("disabled", false).html(
            '<i class="ph ph-sparkle" aria-hidden="true"></i> Generate Image'
          );
          var msg = "Could not generate first frame.";
          try {
            var body = JSON.parse(xhr.responseText);
            if (body.error) {
              msg = body.error;
            }
          } catch (e) {
            /* use default */
          }
          if (typeof Peliku !== "undefined" && Peliku.Toast) {
            Peliku.Toast.show(msg, "error");
          }
        },
      });
    });
  }

  /**
   * Bind the file upload input in the first-frame panel.
   */
  function bindFirstFrameUpload() {
    $(document).on("change", ".js-first-frame-upload-input", function () {
      var $input = $(this);
      var file = $input[0].files[0];
      if (!file) {
        return;
      }

      var $panel = $input.closest(".js-first-frame-panel");
      var clipId = $panel.data("clip-id");

      var formData = new FormData();
      formData.append("source", "upload");
      formData.append("image", file);

      $.ajax({
        url: "/api/clips/" + clipId + "/set-first-frame/",
        method: "POST",
        headers: { "X-CSRFToken": getCsrfToken() },
        data: formData,
        processData: false,
        contentType: false,
        success: function (data) {
          if (data.image_url) {
            renderFirstFrame($panel, data.image_url);
          }
          if (typeof Peliku !== "undefined" && Peliku.Toast) {
            Peliku.Toast.show("First frame uploaded", "success");
          }
        },
        error: function (xhr) {
          var msg = "Upload failed.";
          try {
            var body = JSON.parse(xhr.responseText);
            if (body.error) {
              msg = body.error;
            }
          } catch (e) {
            /* use default */
          }
          if (typeof Peliku !== "undefined" && Peliku.Toast) {
            Peliku.Toast.show(msg, "error");
          }
        },
      });

      $input.val("");
    });
  }

  /**
   * Bind the "Use Previous Clip's Last Frame" button.
   */
  function bindFirstFrameFromPrev() {
    $(document).on("click", ".js-first-frame-from-prev", function () {
      var $btn = $(this);
      var $panel = $btn.closest(".js-first-frame-panel");
      var clipId = $panel.data("clip-id");

      $btn.prop("disabled", true);

      $.ajax({
        url: "/api/clips/" + clipId + "/set-first-frame/",
        method: "POST",
        contentType: "application/json",
        headers: { "X-CSRFToken": getCsrfToken() },
        data: JSON.stringify({ source: "previous_clip" }),
        success: function (data) {
          if (data.image_url) {
            renderFirstFrame($panel, data.image_url);
          }
          $btn.prop("disabled", false);
          if (typeof Peliku !== "undefined" && Peliku.Toast) {
            Peliku.Toast.show("First frame set from previous clip", "success");
          }
        },
        error: function (xhr) {
          $btn.prop("disabled", false);
          var msg = "Could not set first frame from previous clip.";
          try {
            var body = JSON.parse(xhr.responseText);
            if (body.error) {
              msg = body.error;
            }
          } catch (e) {
            /* use default */
          }
          if (typeof Peliku !== "undefined" && Peliku.Toast) {
            Peliku.Toast.show(msg, "error");
          }
        },
      });
    });
  }

  /* ── Last Frame Management ── */

  /**
   * Render a last-frame image into the preview area.
   * @param {jQuery} $panel - The .js-last-frame-panel element.
   * @param {string} imageUrl - The URL of the last-frame image.
   */
  function renderLastFrame($panel, imageUrl) {
    var $preview = $panel.find(".js-last-frame-preview");
    $preview.html(
      '<img src="' +
        imageUrl +
        '" alt="Last frame" class="last-frame-panel__img">'
    );
  }

  /**
   * Bind the "Generate Image" button in the last-frame panel.
   */
  function bindLastFrameGenerate() {
    $(document).on("click", ".js-last-frame-generate", function () {
      var $btn = $(this);
      var $panel = $btn.closest(".js-last-frame-panel");
      var clipId = $panel.data("clip-id");

      $btn.prop("disabled", true).text("Generating\u2026");

      $.ajax({
        url: "/api/clips/" + clipId + "/set-last-frame/",
        method: "POST",
        contentType: "application/json",
        headers: { "X-CSRFToken": getCsrfToken() },
        data: JSON.stringify({ source: "generate" }),
        success: function (data) {
          if (data.task_id) {
            TaskPoller.pollTask(data.task_id, {
              onComplete: function (taskData) {
                var imageUrl =
                  taskData.result_data && taskData.result_data.image_url
                    ? taskData.result_data.image_url
                    : "";
                if (imageUrl) {
                  renderLastFrame($panel, imageUrl);
                }
                $btn.prop("disabled", false).html(
                  '<i class="ph ph-sparkle" aria-hidden="true"></i> Generate Image'
                );
                if (typeof Peliku !== "undefined" && Peliku.Toast) {
                  Peliku.Toast.show("Last frame generated", "success");
                }
              },
              onError: function () {
                $btn.prop("disabled", false).html(
                  '<i class="ph ph-sparkle" aria-hidden="true"></i> Generate Image'
                );
                if (typeof Peliku !== "undefined" && Peliku.Toast) {
                  Peliku.Toast.show("Last frame generation failed", "error");
                }
              },
            });
          }
        },
        error: function (xhr) {
          $btn.prop("disabled", false).html(
            '<i class="ph ph-sparkle" aria-hidden="true"></i> Generate Image'
          );
          var msg = "Could not generate last frame.";
          try {
            var body = JSON.parse(xhr.responseText);
            if (body.error) {
              msg = body.error;
            }
          } catch (e) {
            /* use default */
          }
          if (typeof Peliku !== "undefined" && Peliku.Toast) {
            Peliku.Toast.show(msg, "error");
          }
        },
      });
    });
  }

  /**
   * Bind the file upload input in the last-frame panel.
   */
  function bindLastFrameUpload() {
    $(document).on("change", ".js-last-frame-upload-input", function () {
      var $input = $(this);
      var file = $input[0].files[0];
      if (!file) {
        return;
      }

      var $panel = $input.closest(".js-last-frame-panel");
      var clipId = $panel.data("clip-id");

      var formData = new FormData();
      formData.append("source", "upload");
      formData.append("image", file);

      $.ajax({
        url: "/api/clips/" + clipId + "/set-last-frame/",
        method: "POST",
        headers: { "X-CSRFToken": getCsrfToken() },
        data: formData,
        processData: false,
        contentType: false,
        success: function (data) {
          if (data.image_url) {
            renderLastFrame($panel, data.image_url);
          }
          if (typeof Peliku !== "undefined" && Peliku.Toast) {
            Peliku.Toast.show("Last frame uploaded", "success");
          }
        },
        error: function (xhr) {
          var msg = "Upload failed.";
          try {
            var body = JSON.parse(xhr.responseText);
            if (body.error) {
              msg = body.error;
            }
          } catch (e) {
            /* use default */
          }
          if (typeof Peliku !== "undefined" && Peliku.Toast) {
            Peliku.Toast.show(msg, "error");
          }
        },
      });

      $input.val("");
    });
  }

  /**
   * Bind the "Use Next Clip's First Frame" button.
   */
  function bindLastFrameFromNext() {
    $(document).on("click", ".js-last-frame-from-next", function () {
      var $btn = $(this);
      var $panel = $btn.closest(".js-last-frame-panel");
      var clipId = $panel.data("clip-id");

      $btn.prop("disabled", true);

      $.ajax({
        url: "/api/clips/" + clipId + "/set-last-frame/",
        method: "POST",
        contentType: "application/json",
        headers: { "X-CSRFToken": getCsrfToken() },
        data: JSON.stringify({ source: "next_clip" }),
        success: function (data) {
          if (data.image_url) {
            renderLastFrame($panel, data.image_url);
          }
          $btn.prop("disabled", false);
          if (typeof Peliku !== "undefined" && Peliku.Toast) {
            Peliku.Toast.show("Last frame set from next clip", "success");
          }
        },
        error: function (xhr) {
          $btn.prop("disabled", false);
          var msg = "Could not set last frame from next clip.";
          try {
            var body = JSON.parse(xhr.responseText);
            if (body.error) {
              msg = body.error;
            }
          } catch (e) {
            /* use default */
          }
          if (typeof Peliku !== "undefined" && Peliku.Toast) {
            Peliku.Toast.show(msg, "error");
          }
        },
      });
    });
  }

  return {
    init: function () {
      bindRefPanelToggle();
      bindScriptCharCount();
      bindAutoSave();
      bindGenerateVideo();
      bindGenMethodChange();
      bindFirstFrameGenerate();
      bindFirstFrameUpload();
      bindFirstFrameFromPrev();
      bindLastFrameGenerate();
      bindLastFrameUpload();
      bindLastFrameFromNext();
      bindRefGenerate();
      bindRefUpload();
      bindRefRemove();
      bindClipRefCheckboxes();
      bindRefSelectAll();
    },
  };
})(jQuery);

$(document).ready(function () {
  Workspace.init();
});

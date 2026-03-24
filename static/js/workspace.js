/**
 * Workspace JS — Peliku
 * jQuery handlers for the Project Workspace page.
 * Handles Reference Images Panel toggle, inline script editing,
 * auto-save via AJAX, and live character counts.
 */

const Workspace = (function ($) {
  "use strict";

  /* ── Constants ── */
  const DEBOUNCE_DELAY_MS = 5000;
  const SAVED_INDICATOR_DURATION_MS = 3000;

  /* ── Debounce timers keyed by clip ID ── */
  var debounceTimers = {};

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

  return {
    init: function () {
      bindRefPanelToggle();
      bindScriptCharCount();
      bindAutoSave();
    },
  };
})(jQuery);

$(document).ready(function () {
  Workspace.init();
});

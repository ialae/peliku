/**
 * Main JS — Peliku
 * jQuery-powered toast notification system, settings panel,
 * preview overlay, and global interactions.
 */

const Peliku = (function ($) {
  "use strict";

  /* ── Constants ── */
  const TOAST_DURATION_MS = 5000;
  const MAX_VISIBLE_TOASTS = 3;
  const SLIDE_DURATION_MS = 300;

  /* ── Toast system ── */
  const Toast = {
    /**
     * Show a toast notification.
     * @param {string} message - The message to display.
     * @param {"success"|"error"|"warning"|"info"} variant - Toast type.
     */
    show(message, variant) {
      const $container = $("#toast-container");
      const iconMap = {
        success: "ph ph-check-circle",
        error: "ph ph-warning-circle",
        warning: "ph ph-warning",
        info: "ph ph-info",
      };

      const $toast = $(
        '<div class="toast toast--' +
          variant +
          '" role="alert">' +
          '<i class="' +
          (iconMap[variant] || iconMap.info) +
          '" aria-hidden="true"></i>' +
          '<span class="toast__message"></span>' +
          '<button type="button" class="toast__dismiss" aria-label="Dismiss">' +
          '<i class="ph ph-x" aria-hidden="true"></i>' +
          "</button>" +
          "</div>"
      );

      $toast.find(".toast__message").text(message);
      $container.append($toast);

      /* Enforce max stack */
      const $toasts = $container.children(".toast");
      if ($toasts.length > MAX_VISIBLE_TOASTS) {
        $toasts.first().remove();
      }

      /* Animate in */
      requestAnimationFrame(function () {
        $toast.addClass("is-visible");
      });

      /* Auto-dismiss */
      const dismissTimer = setTimeout(function () {
        Toast.dismiss($toast);
      }, TOAST_DURATION_MS);

      /* Manual dismiss */
      $toast.find(".toast__dismiss").on("click", function () {
        clearTimeout(dismissTimer);
        Toast.dismiss($toast);
      });
    },

    /**
     * Dismiss a toast element.
     * @param {jQuery} $toast - The toast element to remove.
     */
    dismiss($toast) {
      $toast.removeClass("is-visible");
      setTimeout(function () {
        $toast.remove();
      }, SLIDE_DURATION_MS);
    },
  };

  /* ── Settings panel ── */
  const SettingsPanel = {
    /**
     * Open the settings slide-over panel.
     */
    open() {
      const $panel = $(".js-settings-panel");
      const $backdrop = $(".js-settings-backdrop");
      $panel.addClass("is-open");
      $panel.attr("aria-hidden", "false");
      $backdrop.addClass("is-visible");
      $backdrop.attr("aria-hidden", "false");
      $panel.find(".js-settings-close").trigger("focus");
    },

    /**
     * Close the settings slide-over panel.
     */
    close() {
      const $panel = $(".js-settings-panel");
      const $backdrop = $(".js-settings-backdrop");
      $panel.removeClass("is-open");
      $panel.attr("aria-hidden", "true");
      $backdrop.removeClass("is-visible");
      $backdrop.attr("aria-hidden", "true");
      $(".js-settings-toggle").trigger("focus");
    },

    /**
     * Check whether the settings panel is currently open.
     * @returns {boolean}
     */
    isOpen() {
      return $(".js-settings-panel").hasClass("is-open");
    },
  };

  /* ── Preview overlay ── */
  const PreviewOverlay = {
    /**
     * Open the full-screen preview overlay.
     */
    open() {
      const $overlay = $(".js-preview-overlay");
      $overlay.addClass("is-active");
      $overlay.attr("aria-hidden", "false");
      $overlay.find(".js-preview-close-btn").trigger("focus");
    },

    /**
     * Close the preview overlay.
     */
    close() {
      const $overlay = $(".js-preview-overlay");
      $overlay.removeClass("is-active");
      $overlay.attr("aria-hidden", "true");
      $(".js-preview-toggle").trigger("focus");
    },

    /**
     * Check whether the preview overlay is currently open.
     * @returns {boolean}
     */
    isOpen() {
      return $(".js-preview-overlay").hasClass("is-active");
    },
  };

  /* ── Event bindings ── */

  /**
   * Bind settings panel open/close handlers.
   */
  function bindSettingsToggle() {
    $(".js-settings-toggle").on("click", function () {
      if (SettingsPanel.isOpen()) {
        SettingsPanel.close();
      } else {
        SettingsPanel.open();
      }
    });

    $(".js-settings-close").on("click", function () {
      SettingsPanel.close();
    });

    $(".js-settings-backdrop").on("click", function () {
      SettingsPanel.close();
    });
  }

  /**
   * Bind preview overlay open/close handlers.
   */
  function bindPreviewToggle() {
    $(".js-preview-toggle").on("click", function () {
      PreviewOverlay.open();
    });

    $(".js-preview-close-btn").on("click", function () {
      PreviewOverlay.close();
    });

    $(".js-preview-overlay > .preview-overlay__backdrop").on(
      "click",
      function () {
        PreviewOverlay.close();
      }
    );
  }

  /**
   * Bind Escape key to close settings panel and preview overlay.
   */
  function bindEscapeKey() {
    $(document).on("keydown", function (event) {
      if (event.key !== "Escape") {
        return;
      }
      if (SettingsPanel.isOpen()) {
        SettingsPanel.close();
      } else if (PreviewOverlay.isOpen()) {
        PreviewOverlay.close();
      }
    });
  }

  /* ── Public API ── */
  return {
    Toast: Toast,
    SettingsPanel: SettingsPanel,
    PreviewOverlay: PreviewOverlay,

    init() {
      bindSettingsToggle();
      bindPreviewToggle();
      bindEscapeKey();
    },
  };
})(jQuery);

$(document).ready(function () {
  Peliku.init();
});

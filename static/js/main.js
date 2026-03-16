/**
 * Main JS — ReelForge
 * jQuery-powered toast notification system and global interactions.
 */

const ReelForge = (function ($) {
  "use strict";

  /* ── Constants ── */
  const TOAST_DURATION_MS = 5000;
  const MAX_VISIBLE_TOASTS = 3;

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
      }, 300);
    },
  };

  /* ── Settings gear placeholder ── */
  function bindSettingsToggle() {
    $(".js-settings-toggle").on("click", function () {
      Toast.show("Settings panel coming soon.", "info");
    });
  }

  /* ── Public API ── */
  return {
    Toast: Toast,

    init() {
      bindSettingsToggle();
    },
  };
})(jQuery);

$(document).ready(function () {
  ReelForge.init();
});

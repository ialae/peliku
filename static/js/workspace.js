/**
 * Workspace JS — Peliku
 * jQuery handlers for the Project Workspace page.
 * Handles Reference Images Panel expand/collapse toggle.
 */

const Workspace = (function ($) {
  "use strict";

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

  return {
    init: function () {
      bindRefPanelToggle();
      bindScriptCharCount();
    },
  };
})(jQuery);

$(document).ready(function () {
  Workspace.init();
});

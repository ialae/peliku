/**
 * Project Form JS — Peliku
 * Character count indicators for Description and Visual Style fields.
 */

const ProjectForm = (function ($) {
  "use strict";

  /* ── Constants ── */
  const CHAR_WARNING_THRESHOLD = 0.9;

  /**
   * Update the character count display for a textarea.
   * @param {HTMLTextAreaElement} field - The textarea element.
   */
  function updateCharCount(field) {
    const $field = $(field);
    const $group = $field.closest(".form-group");
    const $counter = $group.find(".js-char-count");
    const $current = $counter.find(".js-char-current");
    const maxChars = parseInt($field.attr("data-max"), 10);
    const currentChars = $field.val().length;

    $current.text(currentChars);

    $counter
      .removeClass("char-count--warning char-count--limit");

    if (currentChars >= maxChars) {
      $counter.addClass("char-count--limit");
    } else if (currentChars >= maxChars * CHAR_WARNING_THRESHOLD) {
      $counter.addClass("char-count--warning");
    }
  }

  /**
   * Bind input events on all character-counted fields.
   */
  function bindCharCountFields() {
    $(".js-charcount-field").on("input", function () {
      updateCharCount(this);
    });
  }

  return {
    init() {
      bindCharCountFields();
    },
  };
})(jQuery);

$(document).ready(function () {
  ProjectForm.init();
});

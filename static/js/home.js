/**
 * Home Page — Peliku
 * jQuery handlers: three-dot menu, delete (confirmation modal),
 * inline rename, duplicate via AJAX, search filtering.
 */

const HomePage = (function ($) {
  "use strict";

  /* ── Constants ── */
  const CSRF_TOKEN = $("[name=csrfmiddlewaretoken]").val() || getCookie("csrftoken");

  /* ── State ── */
  let activeDropdown = null;
  let pendingDeleteId = null;

  /* ── Helpers ── */

  /**
   * Read a cookie value by name.
   * @param {string} name - Cookie name.
   * @returns {string|null}
   */
  function getCookie(name) {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.startsWith(name + "=")) {
        return decodeURIComponent(cookie.substring(name.length + 1));
      }
    }
    return null;
  }

  /**
   * Close all open card dropdowns.
   */
  function closeAllDropdowns() {
    $(".js-card-dropdown").removeClass("is-open");
    activeDropdown = null;
  }

  /* ── Three-dot menu ── */

  /**
   * Toggle the dropdown menu for a project card.
   * @param {Event} event - Click event from the menu button.
   */
  function handleMenuToggle(event) {
    event.preventDefault();
    event.stopPropagation();

    const $dropdown = $(event.currentTarget)
      .closest(".project-card__actions")
      .find(".js-card-dropdown");

    if ($dropdown.hasClass("is-open")) {
      closeAllDropdowns();
      return;
    }

    closeAllDropdowns();
    $dropdown.addClass("is-open");
    activeDropdown = $dropdown;
  }

  /* ── Delete ── */

  /**
   * Show the confirmation modal before deleting a project.
   * @param {Event} event - Click event from the delete button.
   */
  function handleDeleteClick(event) {
    event.preventDefault();
    event.stopPropagation();
    closeAllDropdowns();

    const $card = $(event.currentTarget).closest(".js-project-card");
    pendingDeleteId = $card.data("project-id");
    const title = $card.find(".js-card-title").text();

    $(".js-confirm-title").text("Delete project");
    $(".js-confirm-message").text(
      'Are you sure you want to delete "' + title + '"? This cannot be undone.'
    );
    $(".js-confirm-overlay").addClass("is-active");
    $(".js-confirm-ok").trigger("focus");
  }

  /**
   * Execute the confirmed delete via AJAX.
   */
  function confirmDelete() {
    if (!pendingDeleteId) {
      return;
    }

    const projectId = pendingDeleteId;
    closeConfirmModal();

    $.ajax({
      url: "/api/projects/" + projectId + "/delete/",
      method: "POST",
      headers: { "X-CSRFToken": CSRF_TOKEN },
      contentType: "application/json",
      success: function () {
        const $card = $('[data-project-id="' + projectId + '"]');
        $card.fadeOut(300, function () {
          $card.remove();
          if ($(".js-project-card").length === 0) {
            window.location.reload();
          }
        });
        if (typeof Peliku !== "undefined" && Peliku.Toast) {
          Peliku.Toast.show("Project deleted.", "success");
        }
      },
      error: function () {
        if (typeof Peliku !== "undefined" && Peliku.Toast) {
          Peliku.Toast.show("Failed to delete project.", "error");
        }
      },
    });
  }

  /**
   * Close the confirmation modal and reset state.
   */
  function closeConfirmModal() {
    $(".js-confirm-overlay").removeClass("is-active");
    pendingDeleteId = null;
  }

  /* ── Rename ── */

  /**
   * Show the inline rename input for a project card.
   * @param {Event} event - Click event from the rename button.
   */
  function handleRenameClick(event) {
    event.preventDefault();
    event.stopPropagation();
    closeAllDropdowns();

    const $card = $(event.currentTarget).closest(".js-project-card");
    const $title = $card.find(".js-card-title");
    const currentTitle = $title.text();
    const projectId = $card.data("project-id");

    const $overlay = $(".js-rename-overlay");
    const $input = $overlay.find(".js-rename-input");

    $input.val(currentTitle);
    $overlay.data("project-id", projectId);

    /* Position overlay near the card title */
    const titleOffset = $title.offset();
    $overlay.css({
      display: "flex",
      position: "absolute",
      top: titleOffset.top - 4 + "px",
      left: titleOffset.left + "px",
      zIndex: 100,
    });

    $input.trigger("focus").trigger("select");
  }

  /**
   * Save the renamed title via AJAX.
   */
  function saveRename() {
    const $overlay = $(".js-rename-overlay");
    const $input = $overlay.find(".js-rename-input");
    const projectId = $overlay.data("project-id");
    const newTitle = $input.val().trim();

    if (!newTitle) {
      cancelRename();
      return;
    }

    $.ajax({
      url: "/api/projects/" + projectId + "/rename/",
      method: "POST",
      headers: { "X-CSRFToken": CSRF_TOKEN },
      contentType: "application/json",
      data: JSON.stringify({ title: newTitle }),
      success: function (data) {
        const $card = $('[data-project-id="' + projectId + '"]');
        $card.find(".js-card-title").text(data.title);
        $card.attr("data-title", data.title);
        cancelRename();
        if (typeof Peliku !== "undefined" && Peliku.Toast) {
          Peliku.Toast.show("Project renamed.", "success");
        }
      },
      error: function () {
        cancelRename();
        if (typeof Peliku !== "undefined" && Peliku.Toast) {
          Peliku.Toast.show("Failed to rename project.", "error");
        }
      },
    });
  }

  /**
   * Hide the rename overlay without saving.
   */
  function cancelRename() {
    $(".js-rename-overlay").hide().removeData("project-id");
  }

  /* ── Duplicate ── */

  /**
   * Duplicate a project via AJAX and reload the page.
   * @param {Event} event - Click event from the duplicate button.
   */
  function handleDuplicateClick(event) {
    event.preventDefault();
    event.stopPropagation();
    closeAllDropdowns();

    const $card = $(event.currentTarget).closest(".js-project-card");
    const projectId = $card.data("project-id");

    $.ajax({
      url: "/api/projects/" + projectId + "/duplicate/",
      method: "POST",
      headers: { "X-CSRFToken": CSRF_TOKEN },
      contentType: "application/json",
      success: function () {
        window.location.reload();
      },
      error: function () {
        if (typeof Peliku !== "undefined" && Peliku.Toast) {
          Peliku.Toast.show("Failed to duplicate project.", "error");
        }
      },
    });
  }

  /* ── Search ── */

  /**
   * Filter project cards by title based on the search input.
   */
  function handleSearchInput() {
    const query = $(".js-search-input").val().toLowerCase().trim();
    let visibleCount = 0;

    $(".js-project-card").each(function () {
      const title = $(this).data("title").toString().toLowerCase();
      const isMatch = query === "" || title.indexOf(query) !== -1;
      $(this).toggle(isMatch);
      if (isMatch) {
        visibleCount++;
      }
    });

    $(".js-search-empty").toggle(visibleCount === 0 && query !== "");
  }

  /* ── Initialization ── */

  /**
   * Bind all event handlers for the home page.
   */
  function init() {
    /* Three-dot menu */
    $(document).on("click", ".js-card-menu-btn", handleMenuToggle);

    /* Close dropdown on outside click */
    $(document).on("click", function (event) {
      if (!$(event.target).closest(".project-card__actions").length) {
        closeAllDropdowns();
      }
    });

    /* CRUD actions */
    $(document).on("click", ".js-delete-btn", handleDeleteClick);
    $(document).on("click", ".js-rename-btn", handleRenameClick);
    $(document).on("click", ".js-duplicate-btn", handleDuplicateClick);

    /* Confirm modal */
    $(document).on("click", ".js-confirm-ok", confirmDelete);
    $(document).on("click", ".js-confirm-cancel", closeConfirmModal);
    $(document).on("click", ".js-confirm-close", closeConfirmModal);

    /* Rename overlay */
    $(document).on("click", ".js-rename-save", saveRename);
    $(document).on("click", ".js-rename-cancel", cancelRename);
    $(document).on("keydown", ".js-rename-input", function (event) {
      if (event.key === "Enter") {
        event.preventDefault();
        saveRename();
      } else if (event.key === "Escape") {
        cancelRename();
      }
    });

    /* Search */
    $(document).on("input", ".js-search-input", handleSearchInput);

    /* Escape key closes modals */
    $(document).on("keydown", function (event) {
      if (event.key === "Escape") {
        if ($(".js-confirm-overlay").hasClass("is-active")) {
          closeConfirmModal();
        }
        if ($(".js-rename-overlay").is(":visible")) {
          cancelRename();
        }
      }
    });
  }

  /* ── Boot ── */
  $(document).ready(init);

  return { init: init };
})(jQuery);

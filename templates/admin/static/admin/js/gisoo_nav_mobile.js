/* Mobile nav helpers: default closed, backdrop + close wire to Django toggle */
(function () {
  function ready(fn) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn);
    } else {
      fn();
    }
  }

  function isMobile() {
    return window.matchMedia("(max-width: 900px)").matches;
  }

  ready(function () {
    var main = document.getElementById("main");
    var toggle = document.getElementById("toggle-nav-sidebar");
    var nav = document.getElementById("nav-sidebar");
    var backdrop = document.getElementById("gisoo-nav-backdrop");
    var sideClose = document.getElementById("gisoo-side-close");
    if (!main || !toggle || !nav) return;

    function syncToggleUi() {
      var open = main.classList.contains("shifted");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      toggle.setAttribute("aria-label", open ? "بستن منو" : "باز کردن منو");
      document.body.classList.toggle("gisoo-nav-open", open && isMobile());
    }

    // Mobile should start closed (override Django default open=true)
    if (isMobile()) {
      var stored = localStorage.getItem("django.admin.navSidebarIsOpen");
      if (stored === null || stored === "true") {
        main.classList.remove("shifted");
        localStorage.setItem("django.admin.navSidebarIsOpen", "false");
        nav.setAttribute("aria-expanded", "false");
      }
    }

    syncToggleUi();

    toggle.addEventListener("click", function () {
      // Django handler runs first in same tick after ours if we register later —
      // use microtask to read post-toggle state.
      queueMicrotask(syncToggleUi);
    });

    function closeIfOpen() {
      if (main.classList.contains("shifted")) {
        toggle.click();
      }
    }

    if (backdrop) {
      backdrop.addEventListener("click", closeIfOpen);
    }
    if (sideClose) {
      sideClose.addEventListener("click", closeIfOpen);
    }

    window.addEventListener("resize", function () {
      if (!isMobile() && document.body.classList.contains("gisoo-nav-open")) {
        document.body.classList.remove("gisoo-nav-open");
      }
      syncToggleUi();
    });
  });
})();

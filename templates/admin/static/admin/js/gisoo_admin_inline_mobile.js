/* Label tabular/nested inline cells for mobile card layout + Persianize a few admin strings */
(function () {
  var LABEL_MAP = {
    "Delete?": "حذف؟",
    Delete: "حذف",
    Remove: "حذف",
    Change: "ویرایش",
    View: "مشاهده",
    "View on site": "مشاهده در سایت",
  };

  var scheduled = false;

  function faLabel(text) {
    var t = (text || "").replace(/\s+/g, " ").trim();
    if (!t) return "";
    if (LABEL_MAP[t]) return LABEL_MAP[t];
    var m = t.match(/^Add another\s+(.+)$/i);
    if (m) return "افزودن " + m[1] + " دیگر";
    return t;
  }

  function headerLabels(table) {
    var ths = table.querySelectorAll(":scope > thead > tr > th");
    var labels = [];
    ths.forEach(function (th) {
      var clone = th.cloneNode(true);
      clone.querySelectorAll("img, svg, .help").forEach(function (n) {
        n.remove();
      });
      labels.push(faLabel(clone.textContent));
    });
    return labels;
  }

  function labelRow(tr, labels) {
    var cells = tr.querySelectorAll(":scope > td");
    cells.forEach(function (td, index) {
      if (td.hasAttribute("colspan")) {
        td.removeAttribute("data-label");
        return;
      }
      var label = labels[index] || "";
      if (td.classList.contains("original") && !label) label = "مورد";
      if (td.classList.contains("delete") && !label) label = "حذف؟";
      if (label) td.setAttribute("data-label", label);
    });
  }

  function processTable(table) {
    if (!table) return;
    var labels = headerLabels(table);
    if (!labels.length) return;

    table.querySelectorAll(":scope > tbody").forEach(function (tbody) {
      tbody.querySelectorAll(":scope > tr").forEach(function (tr) {
        labelRow(tr, labels);
      });
    });
  }

  function persianizeAddLinks(root) {
    root.querySelectorAll(".djn-add-item a, .add-row a, .inline-deletelink").forEach(function (a) {
      var next = faLabel(a.textContent);
      if (next && next !== a.textContent.trim()) a.textContent = next;
    });
  }

  function run(root) {
    root = root || document;
    root.querySelectorAll("table.djn-items, .inline-group .tabular > table").forEach(processTable);
    persianizeAddLinks(root);
  }

  function scheduleRun() {
    if (scheduled) return;
    scheduled = true;
    window.requestAnimationFrame(function () {
      scheduled = false;
      run(document);
    });
  }

  function boot() {
    run(document);
    document.addEventListener("formset:added", scheduleRun);
    if (window.MutationObserver) {
      new MutationObserver(scheduleRun).observe(document.body, {
        childList: true,
        subtree: true,
      });
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();

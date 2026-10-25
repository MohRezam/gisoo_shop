(function () {
  function csrfToken() {
    var match = document.cookie.match(/(?:^|; )csrftoken=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : "";
  }

  function escapeHtml(value) {
    return value
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  function looksLikeHtml(value) {
    return /<\/?[a-z][\s\S]*>/i.test(value);
  }

  function plainToHtml(value) {
    var lines = value.replace(/\r\n/g, "\n").split("\n");
    return lines
      .map(function (line) {
        return "<p>" + (escapeHtml(line) || "<br>") + "</p>";
      })
      .join("");
  }

  function button(label, title) {
    var el = document.createElement("button");
    el.type = "button";
    el.textContent = label;
    if (title) el.title = title;
    el.addEventListener("mousedown", function (event) {
      event.preventDefault();
    });
    return el;
  }

  function currentBlock(root) {
    var sel = window.getSelection();
    if (!sel || !sel.anchorNode || !root.contains(sel.anchorNode)) return null;
    var node = sel.anchorNode.nodeType === 1 ? sel.anchorNode : sel.anchorNode.parentElement;
    while (node && node.parentElement !== root) node = node.parentElement;
    return node;
  }

  function sync(textarea, surface) {
    var text = surface.innerText.replace(/\u00a0/g, " ").trim();
    textarea.value = text ? surface.innerHTML : "";
  }

  function format(tag) {
    document.execCommand("formatBlock", false, tag);
    var current = "";
    try {
      current = String(document.queryCommandValue("formatBlock") || "").toLowerCase();
    } catch (err) {
      current = "";
    }
    if (current.indexOf(tag) === -1) {
      document.execCommand("formatBlock", false, "<" + tag + ">");
    }
  }

  function selectionElement(root) {
    var sel = window.getSelection();
    if (!sel || !sel.anchorNode || !root.contains(sel.anchorNode)) return null;
    return sel.anchorNode.nodeType === 1 ? sel.anchorNode : sel.anchorNode.parentElement;
  }

  function mount(textarea) {
    if (textarea.dataset.gisooMounted === "1") return;
    textarea.dataset.gisooMounted = "1";

    var wrap = document.createElement("div");
    wrap.className = "gisoo-editor";
    textarea.parentNode.insertBefore(wrap, textarea);
    wrap.appendChild(textarea);

    var toolbar = document.createElement("div");
    toolbar.className = "gisoo-editor-toolbar";
    wrap.insertBefore(toolbar, textarea);

    var panel = document.createElement("div");
    panel.className = "gisoo-editor-panel";
    wrap.insertBefore(panel, textarea);

    var surface = document.createElement("div");
    surface.className = "gisoo-editor-surface";
    surface.contentEditable = "true";
    surface.dir = "rtl";
    surface.lang = "fa";
    surface.setAttribute("role", "textbox");
    surface.setAttribute("aria-multiline", "true");
    wrap.insertBefore(surface, textarea);

    var initial = textarea.value || "";
    surface.innerHTML = looksLikeHtml(initial) ? initial : initial ? plainToHtml(initial) : "<p><br></p>";
    textarea.hidden = true;

    var stateButtons = [];
    var hint = document.createElement("div");
    hint.className = "gisoo-editor-hint";

    function track(el, kind, value) {
      el.dataset.gisooKind = kind;
      el.dataset.gisooValue = value;
      stateButtons.push(el);
    }

    function refreshState() {
      var node = selectionElement(surface);
      var block = "";
      var list = "";
      var bold = false;
      var italic = false;
      var el = node;
      while (el && el !== surface) {
        var tag = el.tagName;
        if (tag === "B" || tag === "STRONG") bold = true;
        if (tag === "I" || tag === "EM") italic = true;
        if (tag === "OL") list = "ol";
        if (tag === "UL" && !list) list = "ul";
        if (!block && (tag === "P" || /^H[1-6]$/.test(tag))) block = tag.toLowerCase();
        el = el.parentElement;
      }
      if (node) {
        try {
          if (document.queryCommandState("bold")) bold = true;
          if (document.queryCommandState("italic")) italic = true;
        } catch (err) {
          /* queryCommandState is unavailable in some browsers */
        }
      }
      stateButtons.forEach(function (item) {
        var on = false;
        if (item.dataset.gisooKind === "block") on = block === item.dataset.gisooValue;
        if (item.dataset.gisooKind === "inline") {
          on = item.dataset.gisooValue === "bold" ? bold : italic;
        }
        if (item.dataset.gisooKind === "list") on = list === item.dataset.gisooValue;
        item.classList.toggle("is-active", on);
        item.setAttribute("aria-pressed", on ? "true" : "false");
      });
    }

    function run(label, title, action, state) {
      var el = button(label, title);
      if (state) track(el, state.kind, state.value);
      el.addEventListener("click", function () {
        surface.focus();
        action();
        sync(textarea, surface);
        refreshState();
      });
      toolbar.appendChild(el);
      return el;
    }

    run("متن", "متن معمولی", function () { format("p"); }, { kind: "block", value: "p" });
    ["۱", "۲", "۳", "۴", "۵", "۶"].forEach(function (n, index) {
      var level = index + 1;
      run("تیتر " + n, "تیتر سطح " + n, function () { format("h" + level); }, {
        kind: "block",
        value: "h" + level,
      });
    });
    run("ضخیم", "ضخیم", function () { document.execCommand("bold"); }, { kind: "inline", value: "bold" });
    run("کج", "کج", function () { document.execCommand("italic"); }, { kind: "inline", value: "italic" });
    run("لینک", "لینک", function () {
      var url = window.prompt("نشانی لینک را وارد کنید", "https://");
      if (!url) return;
      url = url.trim();
      if (!/^https?:\/\//i.test(url) && url.charAt(0) !== "/") return;
      document.execCommand("createLink", false, url);
    });
    run("فهرست", "فهرست نشانه‌دار", function () { document.execCommand("insertUnorderedList"); }, {
      kind: "list",
      value: "ul",
    });
    run("شماره‌دار", "فهرست شماره‌دار", function () { document.execCommand("insertOrderedList"); }, {
      kind: "list",
      value: "ol",
    });

    var imageButton = button("تصویر", "درج تصویر");
    imageButton.addEventListener("click", function () {
      panel.classList.toggle("is-open");
    });
    toolbar.appendChild(imageButton);

    function insertAside(className, placeholder) {
      document.execCommand(
        "insertHTML",
        false,
        '<aside class="' + className + '"><p>' + placeholder + "</p></aside><p><br></p>"
      );
    }
    run("نکته", "باکس نکته", function () { insertAside("gisoo-note", "متن نکته"); });
    run("هشدار", "باکس هشدار", function () { insertAside("gisoo-warn", "متن هشدار"); });
    function tableContext() {
      var node = selectionElement(surface);
      if (!node || !node.closest) return null;
      var cell = node.closest("td, th");
      if (!cell || !surface.contains(cell)) return null;
      return { cell: cell, row: cell.parentElement, table: cell.closest("table") };
    }

    function note(message) {
      hint.textContent = message || "";
    }

    run("جدول", "جدول ساده", function () {
      var html = "<div class=\"gisoo-table-wrap\"><table><tbody>";
      for (var r = 0; r < 2; r += 1) {
        html += "<tr>";
        for (var c = 0; c < 2; c += 1) html += "<td><br></td>";
        html += "</tr>";
      }
      html += "</tbody></table></div><p><br></p>";
      document.execCommand("insertHTML", false, html);
      note("");
    });
    run("سطر جدید", "افزودن سطر زیر خانهٔ فعلی", function () {
      var ctx = tableContext();
      if (!ctx) {
        note("برای افزودن سطر، نشانگر را داخل جدول بگذارید.");
        return;
      }
      var tr = document.createElement("tr");
      for (var i = 0; i < ctx.row.cells.length; i += 1) {
        var td = document.createElement("td");
        td.appendChild(document.createElement("br"));
        tr.appendChild(td);
      }
      ctx.row.parentNode.insertBefore(tr, ctx.row.nextSibling);
      note("");
    });
    run("ستون جدید", "افزودن ستون کنار خانهٔ فعلی", function () {
      var ctx = tableContext();
      if (!ctx) {
        note("برای افزودن ستون، نشانگر را داخل جدول بگذارید.");
        return;
      }
      var index = ctx.cell.cellIndex;
      Array.prototype.forEach.call(ctx.table.rows, function (row) {
        var ref = row.cells[index];
        var cell = document.createElement(ref && ref.tagName === "TH" ? "th" : "td");
        cell.appendChild(document.createElement("br"));
        if (ref && ref.nextSibling) row.insertBefore(cell, ref.nextSibling);
        else row.appendChild(cell);
      });
      note("");
    });
    run("حذف سطر", "حذف سطر فعلی", function () {
      var ctx = tableContext();
      if (!ctx) {
        note("نشانگر داخل جدول نیست.");
        return;
      }
      if (ctx.table.rows.length <= 1) {
        var wrap = ctx.table.closest(".gisoo-table-wrap");
        (wrap || ctx.table).remove();
      } else {
        ctx.row.remove();
      }
      note("");
    });
    run("حذف ستون", "حذف ستون فعلی", function () {
      var ctx = tableContext();
      if (!ctx) {
        note("نشانگر داخل جدول نیست.");
        return;
      }
      var index = ctx.cell.cellIndex;
      var columns = ctx.row.cells.length;
      if (columns <= 1) {
        var wrap = ctx.table.closest(".gisoo-table-wrap");
        (wrap || ctx.table).remove();
        note("");
        return;
      }
      Array.prototype.forEach.call(ctx.table.rows, function (row) {
        if (row.cells[index]) row.deleteCell(index);
      });
      note("");
    });
    run("بالا", "انتقال بلوک به بالا", function () {
      var block = currentBlock(surface);
      if (block && block.previousElementSibling) {
        surface.insertBefore(block, block.previousElementSibling);
      }
    });
    run("پایین", "انتقال بلوک به پایین", function () {
      var block = currentBlock(surface);
      if (block && block.nextElementSibling) {
        surface.insertBefore(block.nextElementSibling, block);
      }
    });

    function resize(className) {
      var sel = window.getSelection();
      if (!sel || !sel.anchorNode) return;
      var node = sel.anchorNode.nodeType === 1 ? sel.anchorNode : sel.anchorNode.parentElement;
      var figure = node && node.closest ? node.closest("figure") : null;
      if (!figure || !surface.contains(figure)) return;
      figure.classList.remove("gisoo-img-sm", "gisoo-img-md", "gisoo-img-lg");
      figure.classList.add(className);
    }
    run("کوچک", "اندازه کوچک تصویر", function () { resize("gisoo-img-sm"); });
    run("متوسط", "اندازه متوسط تصویر", function () { resize("gisoo-img-md"); });
    run("بزرگ", "اندازه بزرگ تصویر", function () { resize("gisoo-img-lg"); });

    var file = document.createElement("input");
    file.type = "file";
    file.accept = "image/jpeg,image/png,image/webp,image/gif";
    var alt = document.createElement("input");
    alt.type = "text";
    alt.placeholder = "متن جایگزین تصویر";
    var caption = document.createElement("input");
    caption.type = "text";
    caption.placeholder = "توضیح زیر عکس (اختیاری)";
    var size = document.createElement("select");
    [["gisoo-img-lg", "بزرگ"], ["gisoo-img-md", "متوسط"], ["gisoo-img-sm", "کوچک"]].forEach(function (item) {
      var option = document.createElement("option");
      option.value = item[0];
      option.textContent = item[1];
      size.appendChild(option);
    });
    var error = document.createElement("div");
    error.className = "gisoo-editor-error";
    var insert = button("گذاشتن تصویر");
    function field(label, control) {
      var box = document.createElement("label");
      box.appendChild(document.createTextNode(label));
      box.appendChild(control);
      panel.appendChild(box);
    }
    field("فایل تصویر", file);
    field("متن جایگزین", alt);
    field("توضیح زیر عکس", caption);
    field("اندازه", size);
    panel.appendChild(insert);
    panel.appendChild(error);

    insert.addEventListener("click", function () {
      error.textContent = "";
      if (!file.files || !file.files[0]) {
        error.textContent = "یک تصویر انتخاب کنید.";
        return;
      }
      var uploadUrl = textarea.getAttribute("data-upload-url");
      if (!uploadUrl) {
        error.textContent = "بارگذاری تصویر در این صفحه فعال نیست.";
        return;
      }
      var body = new FormData();
      body.append("file", file.files[0]);
      insert.disabled = true;
      fetch(uploadUrl, {
        method: "POST",
        body: body,
        credentials: "same-origin",
        headers: { "X-CSRFToken": csrfToken() },
      })
        .then(function (response) {
          return response.json().then(function (data) {
            if (!response.ok) throw new Error(data.error || "بارگذاری تصویر ناموفق بود.");
            return data;
          });
        })
        .then(function (data) {
          var altText = escapeHtml(alt.value.trim() || "تصویر");
          var captionText = caption.value.trim();
          var html = '<figure class="gisoo-figure ' + size.value + '"><img src="' +
            escapeHtml(data.url) + '" alt="' + altText + '">';
          if (captionText) html += "<figcaption>" + escapeHtml(captionText) + "</figcaption>";
          html += "</figure><p><br></p>";
          surface.focus();
          document.execCommand("insertHTML", false, html);
          file.value = "";
          alt.value = "";
          caption.value = "";
          panel.classList.remove("is-open");
          sync(textarea, surface);
        })
        .catch(function (err) {
          error.textContent = err.message || "بارگذاری تصویر ناموفق بود.";
        })
        .finally(function () {
          insert.disabled = false;
        });
    });

    toolbar.after(hint);
    surface.addEventListener("input", function () { sync(textarea, surface); });
    surface.addEventListener("keyup", refreshState);
    surface.addEventListener("mouseup", refreshState);
    document.addEventListener("selectionchange", refreshState);
    var form = textarea.closest("form");
    if (form) form.addEventListener("submit", function () { sync(textarea, surface); });
  }

  function boot() {
    document.querySelectorAll("textarea[data-gisoo-editor]").forEach(mount);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();

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

  function selectionElement(root) {
    var sel = window.getSelection();
    if (!sel || !sel.anchorNode || !root.contains(sel.anchorNode)) return null;
    return sel.anchorNode.nodeType === 1 ? sel.anchorNode : sel.anchorNode.parentElement;
  }

  function closestIn(node, selector, root) {
    if (!node || !node.closest) return null;
    var found = node.closest(selector);
    if (!found || !root.contains(found)) return null;
    return found;
  }

  function mount(textarea) {
    if (textarea.dataset.gisooMounted === "1") return;
    textarea.dataset.gisooMounted = "1";

    var wrap = document.createElement("div");
    wrap.className = "gisoo-editor";
    textarea.parentNode.insertBefore(wrap, textarea);
    wrap.appendChild(textarea);

    var dock = document.createElement("div");
    dock.className = "gisoo-editor-dock";
    var toolbar = document.createElement("div");
    toolbar.className = "gisoo-editor-toolbar";
    var tableBar = document.createElement("div");
    tableBar.className = "gisoo-editor-context";
    tableBar.hidden = true;
    var imageBar = document.createElement("div");
    imageBar.className = "gisoo-editor-context";
    imageBar.hidden = true;
    var boxBar = document.createElement("div");
    boxBar.className = "gisoo-editor-context";
    boxBar.hidden = true;
    var linkPanel = document.createElement("div");
    linkPanel.className = "gisoo-editor-panel";
    var imagePanel = document.createElement("div");
    imagePanel.className = "gisoo-editor-panel";
    var surface = document.createElement("div");
    surface.className = "gisoo-editor-surface";
    surface.contentEditable = "true";
    surface.dir = "rtl";
    surface.lang = "fa";
    surface.setAttribute("role", "textbox");
    surface.setAttribute("aria-multiline", "true");

    dock.appendChild(toolbar);
    dock.appendChild(tableBar);
    dock.appendChild(imageBar);
    dock.appendChild(boxBar);
    dock.appendChild(linkPanel);
    dock.appendChild(imagePanel);
    wrap.insertBefore(dock, textarea);
    wrap.insertBefore(surface, textarea);

    var initial = textarea.value || "";
    surface.innerHTML = looksLikeHtml(initial) ? initial : initial ? plainToHtml(initial) : "<p><br></p>";
    textarea.hidden = true;

    var savedRange = null;
    var stateButtons = [];
    var styleSelect = document.createElement("select");
    styleSelect.className = "gisoo-editor-style";
    styleSelect.setAttribute("aria-label", "سبک متن");
    [
      ["p", "متن معمولی"],
      ["h1", "تیتر ۱"],
      ["h2", "تیتر ۲"],
      ["h3", "تیتر ۳"],
      ["h4", "تیتر ۴"],
      ["h5", "تیتر ۵"],
      ["h6", "تیتر ۶"],
    ].forEach(function (item) {
      var option = document.createElement("option");
      option.value = item[0];
      option.textContent = item[1];
      styleSelect.appendChild(option);
    });

    function saveRange() {
      var sel = window.getSelection();
      if (!sel || !sel.rangeCount || !surface.contains(sel.anchorNode)) return;
      savedRange = sel.getRangeAt(0).cloneRange();
    }

    function restoreRange() {
      surface.focus();
      if (!savedRange) return;
      var sel = window.getSelection();
      sel.removeAllRanges();
      sel.addRange(savedRange);
    }

    function markedNodes() {
      return Array.prototype.slice.call(surface.querySelectorAll(".is-current"));
    }

    function sync() {
      var marked = markedNodes();
      marked.forEach(function (el) { el.classList.remove("is-current"); });
      var text = surface.innerText.replace(/\u00a0/g, " ").trim();
      textarea.value = text ? surface.innerHTML : "";
      marked.forEach(function (el) { el.classList.add("is-current"); });
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

    function placeCaret(node) {
      var range = document.createRange();
      range.selectNodeContents(node);
      range.collapse(true);
      var sel = window.getSelection();
      sel.removeAllRanges();
      sel.addRange(range);
    }

    function currentBlock() {
      var node = selectionElement(surface);
      if (!node) return null;
      while (node && node.parentElement !== surface) node = node.parentElement;
      return node;
    }

    function moveBlock(direction) {
      var block = currentBlock();
      if (!block) return;
      if (direction < 0 && block.previousElementSibling) {
        surface.insertBefore(block, block.previousElementSibling);
      }
      if (direction > 0 && block.nextElementSibling) {
        surface.insertBefore(block.nextElementSibling, block);
      }
    }

    function tableContext() {
      var cell = closestIn(selectionElement(surface), "td, th", surface);
      if (!cell) return null;
      return { cell: cell, row: cell.parentElement, table: cell.closest("table") };
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
          /* older browsers */
        }
      }
      if (document.activeElement !== styleSelect) {
        styleSelect.value = block || "p";
      }
      stateButtons.forEach(function (item) {
        var on = false;
        if (item.dataset.gisooKind === "inline") {
          on = item.dataset.gisooValue === "bold" ? bold : italic;
        }
        if (item.dataset.gisooKind === "list") on = list === item.dataset.gisooValue;
        item.classList.toggle("is-active", on);
        item.setAttribute("aria-pressed", on ? "true" : "false");
      });

      markedNodes().forEach(function (item) { item.classList.remove("is-current"); });
      var figure = closestIn(node, "figure", surface);
      var aside = closestIn(node, "aside", surface);
      var inTable = Boolean(tableContext());
      tableBar.hidden = !inTable;
      imageBar.hidden = !figure;
      boxBar.hidden = !aside;
      if (figure) {
        figure.classList.add("is-current");
        imageBar.querySelectorAll("[data-size]").forEach(function (item) {
          item.classList.toggle("is-active", figure.classList.contains(item.dataset.size));
        });
      }
      if (aside) aside.classList.add("is-current");
      var tableWrap = inTable ? closestIn(node, ".gisoo-table-wrap, table", surface) : null;
      if (tableWrap) tableWrap.classList.add("is-current");
    }

    function group() {
      var el = document.createElement("div");
      el.className = "gisoo-editor-group";
      toolbar.appendChild(el);
      return el;
    }

    function addButton(parent, label, title, action, state) {
      var el = button(label, title);
      if (state) {
        el.dataset.gisooKind = state.kind;
        el.dataset.gisooValue = state.value;
        stateButtons.push(el);
      }
      el.addEventListener("click", function () {
        surface.focus();
        action();
        sync();
        refreshState();
      });
      parent.appendChild(el);
      return el;
    }

    function contextLabel(bar, text) {
      var label = document.createElement("span");
      label.className = "gisoo-editor-context-label";
      label.textContent = text;
      bar.appendChild(label);
    }

    var styleGroup = group();
    styleGroup.appendChild(styleSelect);
    styleSelect.addEventListener("mousedown", saveRange);
    styleSelect.addEventListener("change", function () {
      restoreRange();
      format(styleSelect.value);
      sync();
      refreshState();
    });

    var typeGroup = group();
    addButton(typeGroup, "ضخیم", "ضخیم", function () {
      document.execCommand("bold");
    }, { kind: "inline", value: "bold" });
    addButton(typeGroup, "کج", "کج", function () {
      document.execCommand("italic");
    }, { kind: "inline", value: "italic" });

    var linkGroup = group();
    var linkButton = button("لینک", "گذاشتن یا ویرایش لینک");
    linkButton.addEventListener("click", openLinkPanel);
    linkGroup.appendChild(linkButton);

    var listGroup = group();
    addButton(listGroup, "فهرست", "فهرست نشانه‌دار", function () {
      document.execCommand("insertUnorderedList");
    }, { kind: "list", value: "ul" });
    addButton(listGroup, "شماره‌دار", "فهرست شماره‌دار", function () {
      document.execCommand("insertOrderedList");
    }, { kind: "list", value: "ol" });

    var insertGroup = group();
    var imageButton = button("تصویر", "افزودن تصویر");
    imageButton.addEventListener("click", openImagePanel);
    insertGroup.appendChild(imageButton);
    addButton(insertGroup, "نکته", "باکس نکته", function () {
      document.execCommand("insertHTML", false, '<aside class="gisoo-note"><p>متن نکته</p></aside><p><br></p>');
    });
    addButton(insertGroup, "هشدار", "باکس هشدار", function () {
      document.execCommand("insertHTML", false, '<aside class="gisoo-warn"><p>متن هشدار</p></aside><p><br></p>');
    });
    addButton(insertGroup, "جدول", "جدول ۲ در ۲", function () {
      var html = '<div class="gisoo-table-wrap"><table><tbody>';
      for (var r = 0; r < 2; r += 1) {
        html += "<tr><td><br></td><td><br></td></tr>";
      }
      html += "</tbody></table></div><p><br></p>";
      document.execCommand("insertHTML", false, html);
    });

    var historyGroup = group();
    addButton(historyGroup, "واگرد", "برگرداندن آخرین تغییر", function () {
      document.execCommand("undo");
    });
    addButton(historyGroup, "ازنو", "انجام دوباره", function () {
      document.execCommand("redo");
    });

    contextLabel(tableBar, "جدول");
    addButton(tableBar, "سطر", "سطر زیر این خانه", function () {
      var ctx = tableContext();
      if (!ctx) return;
      var tr = document.createElement("tr");
      for (var i = 0; i < ctx.row.cells.length; i += 1) {
        var td = document.createElement("td");
        td.appendChild(document.createElement("br"));
        tr.appendChild(td);
      }
      ctx.row.parentNode.insertBefore(tr, ctx.row.nextSibling);
      placeCaret(tr.cells[0]);
    });
    addButton(tableBar, "ستون", "ستون کنار این خانه", function () {
      var ctx = tableContext();
      if (!ctx) return;
      var index = ctx.cell.cellIndex;
      Array.prototype.forEach.call(ctx.table.rows, function (row) {
        var ref = row.cells[index];
        var cell = document.createElement(ref && ref.tagName === "TH" ? "th" : "td");
        cell.appendChild(document.createElement("br"));
        if (ref && ref.nextSibling) row.insertBefore(cell, ref.nextSibling);
        else row.appendChild(cell);
      });
    });
    addButton(tableBar, "حذف سطر", "حذف همین سطر", function () {
      var ctx = tableContext();
      if (!ctx) return;
      if (ctx.table.rows.length <= 1) {
        var holder = ctx.table.closest(".gisoo-table-wrap") || ctx.table;
        holder.remove();
      } else {
        ctx.row.remove();
      }
    });
    addButton(tableBar, "حذف ستون", "حذف همین ستون", function () {
      var ctx = tableContext();
      if (!ctx) return;
      var index = ctx.cell.cellIndex;
      if (ctx.row.cells.length <= 1) {
        var holder = ctx.table.closest(".gisoo-table-wrap") || ctx.table;
        holder.remove();
        return;
      }
      Array.prototype.forEach.call(ctx.table.rows, function (row) {
        if (row.cells[index]) row.deleteCell(index);
      });
    });
    addButton(tableBar, "بالا", "انتقال جدول به بالا", function () { moveBlock(-1); });
    addButton(tableBar, "پایین", "انتقال جدول به پایین", function () { moveBlock(1); });

    contextLabel(imageBar, "این تصویر");
    ["gisoo-img-sm", "gisoo-img-md", "gisoo-img-lg"].forEach(function (className, index) {
      var label = ["کوچک", "متوسط", "بزرگ"][index];
      var el = addButton(imageBar, label, "اندازه " + label, function () {
        var figure = closestIn(selectionElement(surface), "figure", surface);
        if (!figure) return;
        figure.classList.remove("gisoo-img-sm", "gisoo-img-md", "gisoo-img-lg");
        figure.classList.add(className);
      });
      el.dataset.size = className;
    });
    addButton(imageBar, "بالا", "انتقال تصویر به بالا", function () { moveBlock(-1); });
    addButton(imageBar, "پایین", "انتقال تصویر به پایین", function () { moveBlock(1); });

    contextLabel(boxBar, "این باکس");
    addButton(boxBar, "بالا", "انتقال باکس به بالا", function () { moveBlock(-1); });
    addButton(boxBar, "پایین", "انتقال باکس به پایین", function () { moveBlock(1); });

    var linkUrl = document.createElement("input");
    linkUrl.type = "url";
    linkUrl.placeholder = "https://";
    var linkText = document.createElement("input");
    linkText.type = "text";
    linkText.placeholder = "اگر متنی انتخاب نکرده‌اید، اینجا بنویسید";
    var linkError = document.createElement("div");
    linkError.className = "gisoo-editor-error";
    var linkApply = button("گذاشتن لینک");
    var linkRemove = button("برداشتن لینک");
    var linkCancel = button("انصراف");
    fillPanel(linkPanel, "لینک", [
      labeled("نشانی", linkUrl),
      labeled("متن لینک", linkText),
    ], [linkApply, linkRemove, linkCancel], linkError);

    var file = document.createElement("input");
    file.type = "file";
    file.accept = "image/jpeg,image/png,image/webp,image/gif";
    var alt = document.createElement("input");
    alt.type = "text";
    alt.placeholder = "مثلاً شامپو تقویت‌کننده";
    var caption = document.createElement("input");
    caption.type = "text";
    caption.placeholder = "اختیاری";
    var size = document.createElement("select");
    [["gisoo-img-lg", "بزرگ"], ["gisoo-img-md", "متوسط"], ["gisoo-img-sm", "کوچک"]].forEach(function (item) {
      var option = document.createElement("option");
      option.value = item[0];
      option.textContent = item[1];
      size.appendChild(option);
    });
    var imageError = document.createElement("div");
    imageError.className = "gisoo-editor-error";
    var imageApply = button("گذاشتن تصویر");
    var imageCancel = button("انصراف");
    fillPanel(imagePanel, "افزودن تصویر", [
      labeled("فایل تصویر", file),
      labeled("متن جایگزین", alt),
      labeled("توضیح زیر عکس", caption),
      labeled("اندازه", size),
    ], [imageApply, imageCancel], imageError);

    function labeled(text, control) {
      var box = document.createElement("label");
      box.appendChild(document.createTextNode(text));
      box.appendChild(control);
      return box;
    }

    function fillPanel(panel, title, fields, actions, error) {
      var heading = document.createElement("p");
      heading.className = "gisoo-editor-panel-title";
      heading.textContent = title;
      panel.appendChild(heading);
      fields.forEach(function (field) { panel.appendChild(field); });
      var row = document.createElement("div");
      row.className = "gisoo-editor-panel-actions";
      actions.forEach(function (action) { row.appendChild(action); });
      panel.appendChild(row);
      panel.appendChild(error);
    }

    function closePanels() {
      linkPanel.classList.remove("is-open");
      imagePanel.classList.remove("is-open");
    }

    function anchorFromRange(range) {
      if (!range) return null;
      var node = range.startContainer;
      var el = node.nodeType === 1 ? node : node.parentElement;
      return closestIn(el, "a", surface);
    }

    function openLinkPanel() {
      saveRange();
      imagePanel.classList.remove("is-open");
      linkError.textContent = "";
      var anchor = anchorFromRange(savedRange);
      linkUrl.value = anchor ? anchor.getAttribute("href") || "" : "https://";
      linkText.value = "";
      linkRemove.hidden = !anchor;
      linkPanel.classList.add("is-open");
      linkUrl.focus();
    }

    function openImagePanel() {
      saveRange();
      linkPanel.classList.remove("is-open");
      imageError.textContent = "";
      imagePanel.classList.add("is-open");
    }

    linkCancel.addEventListener("click", function () {
      closePanels();
      restoreRange();
    });
    imageCancel.addEventListener("click", function () {
      closePanels();
      restoreRange();
    });

    linkApply.addEventListener("click", function () {
      linkError.textContent = "";
      var url = linkUrl.value.trim();
      if (!/^https?:\/\//i.test(url) && url.charAt(0) !== "/") {
        linkError.textContent = "نشانی باید با https:// شروع شود.";
        return;
      }
      restoreRange();
      var range = savedRange;
      var anchor = anchorFromRange(range);
      if (anchor && (!range || range.collapsed)) {
        anchor.setAttribute("href", url);
        if (linkText.value.trim()) anchor.textContent = linkText.value.trim();
      } else if (range && !range.collapsed) {
        document.execCommand("createLink", false, url);
      } else if (linkText.value.trim()) {
        var link = document.createElement("a");
        link.href = url;
        link.textContent = linkText.value.trim();
        if (range) {
          range.insertNode(link);
          placeCaret(link);
        }
      } else {
        linkError.textContent = "متن لینک را بنویسید یا بخشی از متن را انتخاب کنید.";
        return;
      }
      closePanels();
      sync();
      refreshState();
    });

    linkRemove.addEventListener("click", function () {
      var anchor = anchorFromRange(savedRange);
      if (!anchor) return;
      var parent = anchor.parentNode;
      while (anchor.firstChild) parent.insertBefore(anchor.firstChild, anchor);
      anchor.remove();
      closePanels();
      sync();
      refreshState();
    });

    imageApply.addEventListener("click", function () {
      imageError.textContent = "";
      if (!file.files || !file.files[0]) {
        imageError.textContent = "یک تصویر انتخاب کنید.";
        return;
      }
      var uploadUrl = textarea.getAttribute("data-upload-url");
      if (!uploadUrl) {
        imageError.textContent = "بارگذاری تصویر در این صفحه فعال نیست.";
        return;
      }
      var body = new FormData();
      body.append("file", file.files[0]);
      imageApply.disabled = true;
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
          restoreRange();
          document.execCommand("insertHTML", false, html);
          file.value = "";
          alt.value = "";
          caption.value = "";
          closePanels();
          sync();
          refreshState();
        })
        .catch(function (err) {
          imageError.textContent = err.message || "بارگذاری تصویر ناموفق بود.";
        })
        .finally(function () {
          imageApply.disabled = false;
        });
    });

    surface.addEventListener("input", function () {
      sync();
      refreshState();
    });
    surface.addEventListener("keyup", refreshState);
    surface.addEventListener("mouseup", refreshState);
    document.addEventListener("selectionchange", refreshState);

    function placeDock() {
      var header = document.getElementById("header");
      var limit = (header ? header.getBoundingClientRect().bottom : 0) + 8;
      var dockHeight = dock.offsetHeight;
      var box = wrap.getBoundingClientRect();
      var surfaceBox = surface.getBoundingClientRect();
      var stick = box.top < limit && surfaceBox.bottom > limit + dockHeight + 16;
      if (!stick) {
        if (dock.classList.contains("is-fixed")) {
          dock.classList.remove("is-fixed");
          dock.style.top = "";
          dock.style.left = "";
          dock.style.width = "";
          wrap.style.paddingTop = "";
        }
        return;
      }
      dock.classList.add("is-fixed");
      dock.style.top = limit + "px";
      dock.style.left = box.left + "px";
      dock.style.width = box.width + "px";
      var pad = dockHeight + "px";
      if (wrap.style.paddingTop !== pad) wrap.style.paddingTop = pad;
    }
    document.addEventListener("scroll", placeDock, true);
    window.addEventListener("resize", placeDock);
    if (window.ResizeObserver) new ResizeObserver(placeDock).observe(dock);
    placeDock();
    var form = textarea.closest("form");
    if (form) {
      form.addEventListener("submit", function () {
        markedNodes().forEach(function (el) { el.classList.remove("is-current"); });
        sync();
      });
    }
    refreshState();
  }

  function boot() {
    document.querySelectorAll("textarea[data-gisoo-editor]").forEach(mount);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();

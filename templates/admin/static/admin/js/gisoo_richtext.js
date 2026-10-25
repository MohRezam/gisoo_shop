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

    function run(label, title, action) {
      var el = button(label, title);
      el.addEventListener("click", function () {
        surface.focus();
        action();
        sync(textarea, surface);
      });
      toolbar.appendChild(el);
      return el;
    }

    run("متن", "متن معمولی", function () { format("p"); });
    ["۱", "۲", "۳", "۴", "۵", "۶"].forEach(function (n, index) {
      var level = index + 1;
      run("تیتر " + n, "تیتر سطح " + n, function () { format("h" + level); });
    });
    run("ضخیم", "ضخیم", function () { document.execCommand("bold"); });
    run("کج", "کج", function () { document.execCommand("italic"); });
    run("لینک", "لینک", function () {
      var url = window.prompt("نشانی لینک را وارد کنید", "https://");
      if (!url) return;
      url = url.trim();
      if (!/^https?:\/\//i.test(url) && url.charAt(0) !== "/") return;
      document.execCommand("createLink", false, url);
    });
    run("فهرست", "فهرست نشانه‌دار", function () { document.execCommand("insertUnorderedList"); });
    run("شماره‌دار", "فهرست شماره‌دار", function () { document.execCommand("insertOrderedList"); });

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
    run("جدول", "جدول ساده", function () {
      var html = "<div class=\"gisoo-table-wrap\"><table><tbody>";
      for (var r = 0; r < 2; r += 1) {
        html += "<tr>";
        for (var c = 0; c < 2; c += 1) html += "<td>متن</td>";
        html += "</tr>";
      }
      html += "</tbody></table></div><p><br></p>";
      document.execCommand("insertHTML", false, html);
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

    surface.addEventListener("input", function () { sync(textarea, surface); });
    var form = textarea.closest("form");
    if (form) form.addEventListener("submit", function () { sync(textarea, surface); });
  }

  function boot() {
    document.querySelectorAll("textarea[data-gisoo-editor]").forEach(mount);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();

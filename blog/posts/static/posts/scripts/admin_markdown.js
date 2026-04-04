(function () {
  "use strict";

  /* ── Wait for marked.js to load ────────────────────────── */
  function waitForMarked(cb) {
    if (window.marked) return cb();
    const interval = setInterval(() => {
      if (window.marked) {
        clearInterval(interval);
        cb();
      }
    }, 50);
  }

  /* ── Bootstrap ─────────────────────────────────────────── */
  function init() {
    const textarea = document.querySelector("#id_body");
    if (!textarea) return;

    // Configure marked
    marked.setOptions({
      breaks: true,
      gfm: true,
    });

    // ── Build toolbar ─────────────────────────────────────
    const toolbar = document.createElement("div");
    toolbar.className = "md-toolbar";

    const btnWrite = makeBtn("✏️ Write", true);
    const btnPreview = makeBtn("👁️ Preview", false);
    toolbar.append(btnWrite, btnPreview);

    // ── Build preview pane ────────────────────────────────
    const preview = document.createElement("div");
    preview.className = "md-preview";

    // Insert toolbar + preview right before the textarea
    textarea.parentNode.insertBefore(toolbar, textarea);
    textarea.parentNode.insertBefore(preview, textarea.nextSibling);

    // ── Toggle logic ──────────────────────────────────────
    btnWrite.addEventListener("click", (e) => {
      e.preventDefault();
      showWrite();
    });

    btnPreview.addEventListener("click", (e) => {
      e.preventDefault();
      showPreview();
    });

    function showWrite() {
      btnWrite.classList.add("active");
      btnPreview.classList.remove("active");
      textarea.style.display = "";
      preview.style.display = "none";
    }

    function showPreview() {
      btnPreview.classList.add("active");
      btnWrite.classList.remove("active");
      textarea.style.display = "none";

      const raw = textarea.value.trim();
      if (!raw) {
        preview.innerHTML =
          '<p class="md-preview-empty">Nothing to preview — start writing!</p>';
      } else {
        preview.innerHTML = marked.parse(raw);
      }
      preview.style.display = "block";
    }
  }

  /* ── Helpers ───────────────────────────────────────────── */
  function makeBtn(label, isActive) {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.textContent = label;
    if (isActive) btn.classList.add("active");
    return btn;
  }

  /* ── Kick off once the DOM is ready ────────────────────── */
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => waitForMarked(init));
  } else {
    waitForMarked(init);
  }
})();

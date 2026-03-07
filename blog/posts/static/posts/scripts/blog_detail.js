/* ═══════════════════════════════════════════════════════════════════
   blog_detail.js
   Handles: Highlight.js, copy buttons, TOC sidebar, reading progress
   ═══════════════════════════════════════════════════════════════════ */

document.addEventListener("DOMContentLoaded", () => {

    /* ── 1. Syntax highlighting ──────────────────────────────────────── */
    document.querySelectorAll(".prose-content pre code").forEach((block) => {
        hljs.highlightElement(block);
    });

    /* ── 2. Copy buttons on every code block ────────────────────────── */
    document.querySelectorAll(".prose-content pre").forEach((pre) => {
        // stamp data-lang from the hljs language class so CSS ::before works
        const code = pre.querySelector("code");
        if (code) {
            const langClass = [...code.classList].find((c) => c.startsWith("language-"));
            if (langClass) {
                pre.dataset.lang = langClass.replace("language-", "");
            }
        }

        const btn = document.createElement("button");
        btn.className = "copy-btn";
        btn.setAttribute("aria-label", "Copy code");
        btn.innerHTML = `
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
           stroke="currentColor" stroke-width="2"
           stroke-linecap="round" stroke-linejoin="round">
        <rect width="14" height="14" x="8" y="8" rx="2" ry="2"/>
        <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>
      </svg>
      Copy
    `;

        btn.addEventListener("click", () => {
            const text = pre.querySelector("code")?.innerText ?? "";
            navigator.clipboard.writeText(text).then(() => {
                btn.innerHTML = `
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
               stroke="currentColor" stroke-width="2"
               stroke-linecap="round" stroke-linejoin="round">
            <path d="M20 6 9 17l-5-5"/>
          </svg>
          Copied!
        `;
                setTimeout(() => {
                    btn.innerHTML = `
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
                 stroke="currentColor" stroke-width="2"
                 stroke-linecap="round" stroke-linejoin="round">
              <rect width="14" height="14" x="8" y="8" rx="2" ry="2"/>
              <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>
            </svg>
            Copy
          `;
                }, 2500);
            });
        });

        pre.appendChild(btn);
    });

    /* ── 3. Table of Contents builder ───────────────────────────────── */
    const prose = document.querySelector(".prose-content");
    const tocWidget = document.getElementById("toc-widget");
    const tocList = document.getElementById("toc-list");

    if (prose && tocWidget && tocList) {
        const headings = prose.querySelectorAll("h2, h3, h4");

        if (headings.length >= 2) {
            tocWidget.classList.remove("hidden");

            headings.forEach((h) => {
                // Ensure each heading has an id (toc extension usually sets one)
                if (!h.id) {
                    h.id = h.textContent
                        .toLowerCase()
                        .replace(/[^a-z0-9]+/g, "-")
                        .replace(/^-|-$/g, "");
                }

                const link = document.createElement("a");
                link.href = "#" + h.id;
                // Strip the ¶ permalink character added by the toc extension
                link.textContent = h.textContent.replace(/¶$/, "").trim();

                const indentClass =
                    h.tagName === "H3" ? "pl-6 text-xs" :
                        h.tagName === "H4" ? "pl-9 text-xs opacity-75" : "";

                link.className = [
                    "toc-item block py-1 px-3 rounded-lg text-muted",
                    "hover:text-accent hover:bg-accent/5",
                    "transition-colors duration-150 leading-snug",
                    indentClass,
                ].join(" ");

                link.addEventListener("click", (e) => {
                    e.preventDefault();
                    document.getElementById(h.id)?.scrollIntoView({
                        behavior: "smooth",
                        block: "start",
                    });
                });

                tocList.appendChild(link);
            });

            /* Active-section highlight via IntersectionObserver */
            const observer = new IntersectionObserver(
                (entries) => {
                    entries.forEach((entry) => {
                        const tocLink = tocList.querySelector(`a[href="#${entry.target.id}"]`);
                        if (!tocLink) return;
                        if (entry.isIntersecting) {
                            tocList.querySelectorAll("a").forEach((a) =>
                                a.classList.remove("text-accent", "font-semibold", "bg-accent/5")
                            );
                            tocLink.classList.add("text-accent", "font-semibold", "bg-accent/5");
                        }
                    });
                },
                { rootMargin: "-10% 0px -80% 0px" }
            );

            headings.forEach((h) => observer.observe(h));
        }
    }

    /* ── 4. Reading progress bar ─────────────────────────────────────── */
    const bar = document.getElementById("reading-progress");
    const article = document.querySelector("article");

    if (bar && article) {
        const update = () => {
            const top = article.getBoundingClientRect().top + window.scrollY;
            const height = article.offsetHeight;
            const scrolled = window.scrollY - top;
            const progress = Math.min(Math.max((scrolled / (height - window.innerHeight)) * 100, 0), 100);
            bar.style.width = progress + "%";
        };

        window.addEventListener("scroll", update, { passive: true });
        update(); // initialise on load
    }

});

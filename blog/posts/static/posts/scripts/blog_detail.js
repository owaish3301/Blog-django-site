
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

    /* ── 5. Share Buttons ───────────────────────────────────────────── */
    const shareBtns = [document.getElementById("share-btn"), document.getElementById("share-btn-footer")];
    
    function fallbackCopyTextToClipboard(text) {
        var textArea = document.createElement("textarea");
        textArea.value = text;
        textArea.style.top = "0";
        textArea.style.left = "0";
        textArea.style.position = "fixed";
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        try {
            document.execCommand('copy');
        } catch (err) {
            console.error('Fallback: Oops, unable to copy', err);
        }
        document.body.removeChild(textArea);
    }

    function copyTextToClipboard(text) {
        if (!navigator.clipboard) {
            fallbackCopyTextToClipboard(text);
            return Promise.resolve();
        }
        return navigator.clipboard.writeText(text);
    }

    const shareModal = document.getElementById("share-modal");
    const shareModalContent = document.getElementById("share-modal-content");
    const closeShareModal = document.getElementById("close-share-modal");
    const shareModalUrlInput = document.getElementById("share-modal-url-input");
    const shareModalCopyLink = document.getElementById("share-modal-copy-link");
    
    if (shareModal) {
        const currentUrl = encodeURIComponent(window.location.href);
        const currentTitle = encodeURIComponent(document.title);
        
        document.getElementById("share-x").href = `https://twitter.com/intent/tweet?url=${currentUrl}&text=${currentTitle}`;
        document.getElementById("share-linkedin").href = `https://www.linkedin.com/sharing/share-offsite/?url=${currentUrl}`;
        document.getElementById("share-whatsapp").href = `https://api.whatsapp.com/send?text=${currentTitle}%20${currentUrl}`;
        document.getElementById("share-reddit").href = `https://reddit.com/submit?url=${currentUrl}&title=${currentTitle}`;
        
        shareModalUrlInput.value = window.location.href;
        
        const openModal = () => {
            shareModal.classList.remove("opacity-0", "pointer-events-none");
            shareModal.classList.add("opacity-100", "pointer-events-auto");
            shareModalContent.classList.remove("translate-y-8");
            shareModalContent.classList.add("translate-y-0");
        };
        
        const closeModal = () => {
            shareModal.classList.add("opacity-0", "pointer-events-none");
            shareModal.classList.remove("opacity-100", "pointer-events-auto");
            shareModalContent.classList.add("translate-y-8");
            shareModalContent.classList.remove("translate-y-0");
        };
        
        closeShareModal.addEventListener("click", closeModal);
        shareModal.addEventListener("click", (e) => {
            if (e.target === shareModal) closeModal();
        });
        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape") closeModal();
        });
        
        shareBtns.forEach(btn => {
            if (!btn) return;
            btn.addEventListener("click", openModal);
        });
        
        shareModalCopyLink.addEventListener("click", () => {
            const indicateSuccess = () => {
                shareModalCopyLink.textContent = "Copied!";
                setTimeout(() => {
                    shareModalCopyLink.textContent = "Copy";
                }, 2000);
            };
            
            copyTextToClipboard(window.location.href).then(indicateSuccess).catch(() => {
                fallbackCopyTextToClipboard(window.location.href);
                indicateSuccess();
            });
        });
        
        shareModalUrlInput.addEventListener("click", () => {
             shareModalUrlInput.select();
        });
    }

});

/**
 * Comments — OTP verification + commenting + load-more
 * Works with the comments API endpoints.
 */
document.addEventListener("DOMContentLoaded", () => {
    const section = document.getElementById("comments-section");
    if (!section) return;

    const POST_SLUG = window.__POST_SLUG__;
    const CSRF_TOKEN = document.querySelector("[name=csrfmiddlewaretoken]")?.value
        || document.cookie.match(/csrftoken=([^;]+)/)?.[1]
        || "";

    // ── Element refs ──
    const verifyPrompt = document.getElementById("verify-prompt");
    const emailForm = document.getElementById("email-form");
    const otpVerifyForm = document.getElementById("otp-verify-form");
    const commentBox = document.getElementById("comment-box");

    const nameInput = document.getElementById("commenter-name");
    const emailInput = document.getElementById("commenter-email");
    const sendOtpBtn = document.getElementById("send-otp-btn");
    const otpSendError = document.getElementById("otp-send-error");

    const otpInput = document.getElementById("otp-input");
    const verifyOtpBtn = document.getElementById("verify-otp-btn");
    const otpVerifyError = document.getElementById("otp-verify-error");

    const commentBody = document.getElementById("comment-body");
    const charCount = document.getElementById("char-count");
    const postCommentBtn = document.getElementById("post-comment-btn");
    const commentPostError = document.getElementById("comment-post-error");

    const commenterInitial = document.getElementById("commenter-initial");
    const commenterDisplayName = document.getElementById("commenter-display-name");
    const commenterDisplayEmail = document.getElementById("commenter-display-email");

    const commentsList = document.getElementById("comments-list");
    const commentCount = document.getElementById("comment-count");
    const loadMoreBtn = document.getElementById("load-more-btn");
    const loadMoreWrap = document.getElementById("load-more-wrap");

    let currentPage = 1;
    let storedEmail = "";

    // ── Helpers ──
    function showError(el, msg) {
        if (!el) return;
        el.textContent = msg;
        el.classList.remove("hidden");
    }
    function hideError(el) {
        if (!el) return;
        el.classList.add("hidden");
    }
    function setLoading(btn, loading) {
        if (!btn) return;
        btn.disabled = loading;
        btn.style.opacity = loading ? "0.6" : "1";
        btn.style.pointerEvents = loading ? "none" : "auto";
    }

    // ── Character count ──
    if (commentBody && charCount) {
        commentBody.addEventListener("input", () => {
            charCount.textContent = `${commentBody.value.length} / 2000`;
        });
    }

    // ── 1. Send OTP ──
    if (sendOtpBtn) {
        sendOtpBtn.addEventListener("click", async () => {
            hideError(otpSendError);
            const name = nameInput.value.trim();
            const email = emailInput.value.trim();

            if (!name || !email) {
                showError(otpSendError, "Please enter both name and email.");
                return;
            }

            setLoading(sendOtpBtn, true);
            storedEmail = email;

            try {
                const res = await fetch("/comments/send-otp/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": CSRF_TOKEN,
                    },
                    body: JSON.stringify({ name, email }),
                });
                const data = await res.json();

                if (!res.ok) {
                    showError(otpSendError, data.error || "Failed to send OTP.");
                    return;
                }

                // Show OTP input
                emailForm.classList.add("hidden");
                otpVerifyForm.classList.remove("hidden");
                otpInput.focus();
            } catch {
                showError(otpSendError, "Network error. Please try again.");
            } finally {
                setLoading(sendOtpBtn, false);
            }
        });
    }

    // ── 2. Verify OTP ──
    if (verifyOtpBtn) {
        verifyOtpBtn.addEventListener("click", async () => {
            hideError(otpVerifyError);
            const otp = otpInput.value.trim();

            if (!otp || otp.length !== 6) {
                showError(otpVerifyError, "Please enter the 6-digit code.");
                return;
            }

            setLoading(verifyOtpBtn, true);

            try {
                const res = await fetch("/comments/verify-otp/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": CSRF_TOKEN,
                    },
                    body: JSON.stringify({ email: storedEmail, otp }),
                });
                const data = await res.json();

                if (!res.ok) {
                    showError(otpVerifyError, data.error || "Verification failed.");
                    return;
                }

                // Switch to comment box
                verifyPrompt.classList.add("hidden");
                commentBox.classList.remove("hidden");

                if (commenterInitial) commenterInitial.textContent = data.name?.[0]?.toUpperCase() || "?";
                if (commenterDisplayName) commenterDisplayName.textContent = data.name || "";
                if (commenterDisplayEmail) commenterDisplayEmail.textContent = storedEmail;

                commentBody?.focus();
            } catch {
                showError(otpVerifyError, "Network error. Please try again.");
            } finally {
                setLoading(verifyOtpBtn, false);
            }
        });
    }

    // ── 3. Post Comment ──
    if (postCommentBtn) {
        postCommentBtn.addEventListener("click", async () => {
            hideError(commentPostError);
            const body = commentBody.value.trim();

            if (!body) {
                showError(commentPostError, "Comment cannot be empty.");
                return;
            }
            if (body.length > 2000) {
                showError(commentPostError, "Comment is too long (max 2000 characters).");
                return;
            }

            setLoading(postCommentBtn, true);

            try {
                const res = await fetch("/comments/post/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": CSRF_TOKEN,
                    },
                    body: JSON.stringify({ post_slug: POST_SLUG, body }),
                });
                const data = await res.json();

                if (!res.ok) {
                    showError(commentPostError, data.error || "Failed to post comment.");
                    return;
                }

                // Prepend the new comment
                const noComments = document.getElementById("no-comments");
                if (noComments) noComments.remove();

                const commentEl = createCommentElement(data.comment);
                commentEl.style.opacity = "0";
                commentEl.style.transform = "translateY(-8px)";
                commentsList.prepend(commentEl);

                // Micro-animation: fade in
                requestAnimationFrame(() => {
                    commentEl.style.transition = "opacity 300ms ease, transform 300ms ease";
                    commentEl.style.opacity = "1";
                    commentEl.style.transform = "translateY(0)";
                });

                // Update count
                const currentCount = parseInt(commentCount.textContent.replace(/[()]/g, "")) || 0;
                commentCount.textContent = `(${currentCount + 1})`;

                // Clear textarea
                commentBody.value = "";
                if (charCount) charCount.textContent = "0 / 2000";
            } catch {
                showError(commentPostError, "Network error. Please try again.");
            } finally {
                setLoading(postCommentBtn, false);
            }
        });
    }

    // ── 4. Load More ──
    if (loadMoreBtn) {
        loadMoreBtn.addEventListener("click", async () => {
            setLoading(loadMoreBtn, true);
            currentPage++;

            try {
                const res = await fetch(`/comments/list/${POST_SLUG}/?page=${currentPage}`);
                const data = await res.json();

                if (!res.ok) {
                    currentPage--;
                    return;
                }

                data.comments.forEach((c, i) => {
                    const el = createCommentElement(c);
                    el.style.opacity = "0";
                    el.style.transform = "translateY(8px)";
                    commentsList.append(el);

                    // Staggered fade-in
                    setTimeout(() => {
                        el.style.transition = "opacity 250ms ease, transform 250ms ease";
                        el.style.opacity = "1";
                        el.style.transform = "translateY(0)";
                    }, i * 60);
                });

                if (!data.has_more && loadMoreWrap) {
                    loadMoreWrap.remove();
                }
            } catch {
                currentPage--;
            } finally {
                setLoading(loadMoreBtn, false);
            }
        });
    }

    // ── Create comment DOM element ──
    function createCommentElement(c) {
        const div = document.createElement("div");
        div.className = "comment-item flex gap-3 p-3 rounded-2xl transition-colors duration-150 hover:bg-soft/60";
        div.innerHTML = `
            <div class="rounded-full flex items-center justify-center border"
                style="width: 32px; height: 32px; min-width: 32px; background: rgba(14,122,116,0.15); border-color: rgba(14,122,116,0.25);">
                <span class="font-ibmMono font-bold" style="font-size: 11px; color: #0e7a74;">${escapeHtml(c.initial)}</span>
            </div>
            <div class="min-w-0 flex-1">
                <div class="flex items-center gap-2 mb-1 flex-wrap">
                    <span class="text-xs font-ibmMono font-semibold text-ink">${escapeHtml(c.name)}</span>
                    <span class="text-muted font-ibmMono" style="font-size: 10px;">${escapeHtml(c.created_at)}</span>
                </div>
                <p class="text-sm text-muted leading-relaxed font-base" style="word-break: break-word;">${escapeHtml(c.body)}</p>
            </div>
        `;
        return div;
    }

    function escapeHtml(text) {
        const d = document.createElement("div");
        d.textContent = text || "";
        return d.innerHTML;
    }
});

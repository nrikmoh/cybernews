/* ═══════════════════════════════════════════════════════
   CYBERNEWS ADMIN JAVASCRIPT
═══════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', function () {

    // ── Delete Modal ──────────────────────────────────
    window.confirmDelete = function (articleId, title) {
        const modal   = document.getElementById('delete-modal');
        const form    = document.getElementById('delete-form');
        const message = document.getElementById('modal-message');

        if (message) {
            message.textContent = `Delete "${title}..."?`;
        }

        if (form) {
            form.action = `/admin/articles/delete/${articleId}`;
        }

        if (modal) {
            modal.classList.add('open');
        }
    };

    window.closeModal = function () {
        const modal = document.getElementById('delete-modal');
        if (modal) modal.classList.remove('open');
    };

    // Close modal when clicking the overlay
    const overlay = document.getElementById('delete-modal');
    if (overlay) {
        overlay.addEventListener('click', function (e) {
            if (e.target === overlay) closeModal();
        });
    }

    // Close on Escape key
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') closeModal();
    });

    // ── Character Counters ────────────────────────────
    function initCounter(inputId, countId, type = 'chars') {
        const input = document.getElementById(inputId);
        const count = document.getElementById(countId);
        if (!input || !count) return;

        function update() {
            if (type === 'words') {
                const words = input.value.trim()
                    ? input.value.trim().split(/\s+/).length
                    : 0;
                count.textContent = words;

                // Also update reading time
                const readTime = document.getElementById('read-time');
                if (readTime) {
                    readTime.textContent = Math.max(1, Math.round(words / 200));
                }
            } else {
                count.textContent = input.value.length;
            }
        }

        input.addEventListener('input', update);
        update(); // run on load to show existing content length
    }

    initCounter('title',   'title-count',   'chars');
    initCounter('summary', 'summary-count', 'chars');
    initCounter('body',    'body-count',    'words');


    // ── Image URL Preview ─────────────────────────────
    const imageInput   = document.getElementById('image_url');
    const preview      = document.getElementById('image-preview');
    const previewImg   = document.getElementById('preview-img');

    if (imageInput && preview) {
        function updatePreview() {
            const url = imageInput.value.trim();
            if (url && url.startsWith('http')) {
                preview.style.display = 'block';

                // Create img if it doesn't exist
                let img = preview.querySelector('img');
                if (!img) {
                    img = document.createElement('img');
                    img.alt = 'Preview';
                    preview.appendChild(img);
                }
                img.src = url;

                // Hide preview if image fails to load
                img.onerror = () => { preview.style.display = 'none'; };
            } else {
                preview.style.display = 'none';
            }
        }

        imageInput.addEventListener('input', updatePreview);
        updatePreview(); // show on load if editing existing article
    }


    // ── Animate Category Bars on Dashboard ───────────
    const bars = document.querySelectorAll('.category-bar-fill');
    bars.forEach(function (bar) {
        const targetWidth = bar.style.width;
        bar.style.width   = '0%';
        setTimeout(() => {
            bar.style.width = targetWidth;
        }, 200);
    });


    // ── Auto-dismiss flash messages ───────────────────
    const flashes = document.querySelectorAll('.flash');
    flashes.forEach(function (flash) {
        setTimeout(() => {
            flash.style.transition = 'opacity 0.5s ease';
            flash.style.opacity    = '0';
            setTimeout(() => flash.remove(), 500);
        }, 5000);
    });


    // ── Form dirty check ─────────────────────────────
    // Warn user before leaving if they have unsaved changes
    const form = document.getElementById('article-form');
    if (form) {
        let isDirty = false;

        form.addEventListener('input', () => { isDirty = true; });
        form.addEventListener('submit', () => { isDirty = false; });

        window.addEventListener('beforeunload', function (e) {
            if (isDirty) {
                e.preventDefault();
                e.returnValue = 'You have unsaved changes. Leave anyway?';
            }
        });
    }

    console.log('%c CyberNews Admin ✓ ',
        'background:#7c3aed; color:white; font-weight:bold; padding:4px 8px; border-radius:4px;'
    );
});

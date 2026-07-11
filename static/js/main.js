/* ═══════════════════════════════════════════════════════
   CYBERNEWS — MAIN JAVASCRIPT
   Structure:
   1.  Utility helpers
   2.  Current date display
   3.  Mobile navigation
   4.  Breaking news ticker
   5.  Search functionality
   6.  Category filtering
   7.  Search + Filter combined logic
   8.  Bookmark buttons
   9.  Share buttons
   10. Newsletter form
   11. Scroll effects
   12. Threat level counter animation
   13. Stats counter animation
   14. Article card stagger animation
   15. Keyboard shortcuts
   16. Init — runs everything on page load
═══════════════════════════════════════════════════════ */


/* ═══════════════════════════════════════════════════════
   1. UTILITY HELPERS
   Small reusable functions we use throughout the file
═══════════════════════════════════════════════════════ */

/**
 * Shorthand for document.getElementById
 * Instead of typing document.getElementById('x') every time,
 * we just type id('x')
 */
function id(selector) {
    return document.getElementById(selector);
}

/**
 * Shorthand for document.querySelector (finds ONE element)
 */
function qs(selector) {
    return document.querySelector(selector);
}

/**
 * Shorthand for document.querySelectorAll (finds ALL matching elements)
 * Returns an array we can loop through
 */
function qsa(selector) {
    return Array.from(document.querySelectorAll(selector));
}

/**
 * Show a toast notification (small popup message)
 * We'll create the toast element dynamically
 */
function showToast(message, type = 'info') {
    // Remove any existing toast first
    const existing = qs('.toast');
    if (existing) existing.remove();

    // Create the toast element
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <i class="fas ${type === 'success' ? 'fa-check-circle' :
                        type === 'error'   ? 'fa-times-circle' :
                                            'fa-info-circle'}"></i>
        <span>${message}</span>
    `;

    // Add styles directly (so we don't need extra CSS)
    Object.assign(toast.style, {
        position:     'fixed',
        bottom:       '2rem',
        right:        '2rem',
        background:   type === 'success' ? 'rgba(16,185,129,0.95)' :
                      type === 'error'   ? 'rgba(239,68,68,0.95)'  :
                                          'rgba(0,212,255,0.95)',
        color:        type === 'info' ? '#020408' : 'white',
        padding:      '0.85rem 1.4rem',
        borderRadius: '10px',
        display:      'flex',
        alignItems:   'center',
        gap:          '0.6rem',
        fontSize:     '0.9rem',
        fontWeight:   '600',
        fontFamily:   'Inter, sans-serif',
        zIndex:       '9999',
        boxShadow:    '0 8px 30px rgba(0,0,0,0.4)',
        transform:    'translateY(20px)',
        opacity:      '0',
        transition:   'all 0.3s ease',
    });

    document.body.appendChild(toast);

    // Animate it in
    requestAnimationFrame(() => {
        toast.style.transform = 'translateY(0)';
        toast.style.opacity   = '1';
    });

    // Auto-remove after 3 seconds
    setTimeout(() => {
        toast.style.transform = 'translateY(20px)';
        toast.style.opacity   = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}


/* ═══════════════════════════════════════════════════════
   2. CURRENT DATE DISPLAY
   Shows today's date in the top bar
═══════════════════════════════════════════════════════ */
function initDate() {
    const dateEl = id('current-date');
    if (!dateEl) return;   // if element doesn't exist, stop

    const now = new Date();
    const options = {
        weekday: 'long',
        year:    'numeric',
        month:   'long',
        day:     'numeric'
    };
    dateEl.textContent = now.toLocaleDateString('en-US', options);
}


/* ═══════════════════════════════════════════════════════
   3. MOBILE NAVIGATION
   Hamburger menu toggle for small screens
═══════════════════════════════════════════════════════ */
function initMobileNav() {
    var hamburger = document.getElementById('hamburger');
    var nav = document.querySelector('.main-nav');

    if (!hamburger || !nav) return;

    function openMenu() {
        nav.classList.add('nav-open');
        hamburger.classList.add('open');
        document.body.style.overflow = 'hidden';
    }

    function closeMenu() {
        nav.classList.remove('nav-open');
        hamburger.classList.remove('open');
        document.body.style.overflow = '';
    }

    hamburger.addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();

        if (nav.classList.contains('nav-open')) {
            closeMenu();
        } else {
            openMenu();
        }
    });

    // close when any nav link is clicked
    nav.querySelectorAll('a').forEach(function(link) {
        link.addEventListener('click', function() {
            closeMenu();
        });
    });

    // close on ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeMenu();
        }
    });

    // close if clicking outside
    document.addEventListener('click', function(e) {
        if (
            nav.classList.contains('nav-open') &&
            !nav.contains(e.target) &&
            !hamburger.contains(e.target)
        ) {
            closeMenu();
        }
    });
}




/* ═══════════════════════════════════════════════════════
   4. BREAKING NEWS TICKER
   Duplicates the ticker content so it loops seamlessly
═══════════════════════════════════════════════════════ */
function initTicker() {
    const tickerItems = qs('.ticker-items');
    if (!tickerItems) return;

    /*
     * To make the ticker loop smoothly, we duplicate its content.
     * The CSS animation moves it left by 50%, then resets.
     * With duplicated content, there's no visible jump.
     */
    const originalHTML = tickerItems.innerHTML;
    tickerItems.innerHTML = originalHTML + originalHTML;

    // Pause ticker when mouse hovers over it
    const tickerWrap = qs('.ticker-wrap');
    if (tickerWrap) {
        tickerWrap.addEventListener('mouseenter', () => {
            tickerItems.style.animationPlayState = 'paused';
        });
        tickerWrap.addEventListener('mouseleave', () => {
            tickerItems.style.animationPlayState = 'running';
        });
    }
}


/* ═══════════════════════════════════════════════════════
   5. SEARCH FUNCTIONALITY
   Filters article cards as the user types
═══════════════════════════════════════════════════════ */

function initSearch() {
    var searchInput = id('search-input');
    if (!searchInput) return;

    // Press "/" to focus search
    document.addEventListener('keydown', function(e) {
        var tag = document.activeElement.tagName.toLowerCase();
        if (tag === 'input' || tag === 'textarea') return;

        if (e.key === '/') {
            e.preventDefault();
            searchInput.focus();
            searchInput.select();
        }
    });

    // Press Escape to clear and unfocus
    searchInput.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            this.value = '';
            this.blur();
        }
    });
}


/* ═══════════════════════════════════════════════════════
   6. CATEGORY FILTERING
   Shows only cards matching the selected category
═══════════════════════════════════════════════════════ */

/* ═══════════════════════════════════════════════════════
   CATEGORY FILTERING
═══════════════════════════════════════════════════════ */
function initCategoryFilter() {
    var filterBtns = qsa('.filter-btn');
    if (!filterBtns.length) return;

    filterBtns.forEach(function(btn) {
        btn.addEventListener('click', function() {
            // Remove active from all
            filterBtns.forEach(function(b) { b.classList.remove('active'); });
            this.classList.add('active');

            currentCategory = this.getAttribute('data-category');

            // If searching, search within category
            var searchInput = id('search-input');
            if (searchInput && searchInput.value.trim()) {
                // Let applyFilters handle both
                applyFilters();
                return;
            }

            // Otherwise just filter visible cards
            var cards = qsa('.article-card');
            var visible = 0;
            var noResult = id('no-results');

            cards.forEach(function(card) {
                var cardCat = card.getAttribute('data-category');
                var matches = currentCategory === 'all' || cardCat === currentCategory;

                if (matches) {
                    card.style.display = '';
                    visible++;
                } else {
                    card.style.display = 'none';
                }
            });

            if (noResult) {
                noResult.style.display = visible === 0 ? 'block' : 'none';
            }

            var statEl = id('stat-articles');
            if (statEl) statEl.textContent = visible;
        });
    });
}



/* ═══════════════════════════════════════════════════════
   7. COMBINED FILTER LOGIC
   This function runs whenever search OR category changes.
   It checks both conditions at the same time.
═══════════════════════════════════════════════════════ */
function applyFilters() {
    const cards    = qsa('.article-card');
    const noResult = id('no-results');
    let   visible  = 0;

    cards.forEach(function (card) {
        // Get this card's category (set in data-category attribute)
        const cardCategory = card.getAttribute('data-category');

        // Get all the text inside the card (for search matching)
        const cardText = card.textContent.toLowerCase();

        // Check conditions
        const matchesCategory = currentCategory === 'all' ||
                                 cardCategory === currentCategory;

        const matchesSearch   = currentSearch === '' ||
                                 cardText.includes(currentSearch);

        if (matchesCategory && matchesSearch) {
            // Show this card
            card.style.display = '';         // restore default display
            card.style.animation = 'none';   // reset animation
            // Trigger reflow so animation restarts
            void card.offsetWidth;
            card.style.animation = '';
            visible++;
        } else {
            // Hide this card
            card.style.display = 'none';
        }
    });

    // Show "No results" message if nothing matches
    if (noResult) {
        noResult.style.display = visible === 0 ? 'block' : 'none';
    }

    // Update the article count in stats bar
    const statArticles = id('stat-articles');
    if (statArticles) {
        statArticles.textContent = visible;
    }
}


/* ═══════════════════════════════════════════════════════
   8. BOOKMARK BUTTONS
   Toggle bookmark state on article cards
═══════════════════════════════════════════════════════ */
function initBookmarks() {
    // Use event delegation: listen on the grid, not each button
    // This works even if cards are added dynamically later
    const grid = id('articles-grid');
    if (!grid) return;

    grid.addEventListener('click', function (e) {
        // Find the closest bookmark button (if that's what was clicked)
        const btn = e.target.closest('.action-btn[title="Bookmark"]');
        if (!btn) return;

        const icon = btn.querySelector('i');
        if (!icon) return;

        const isBookmarked = icon.classList.contains('fa-solid');

        if (isBookmarked) {
            // Un-bookmark
            icon.classList.replace('fa-solid', 'fa-regular');
            btn.style.color = '';
            showToast('Bookmark removed', 'info');
        } else {
            // Bookmark it
            icon.classList.replace('fa-regular', 'fa-solid');
            btn.style.color = '#00d4ff';
            showToast('Article bookmarked! 🔖', 'success');
        }
    });
}


/* ═══════════════════════════════════════════════════════
   9. SHARE BUTTONS
   Copy article URL to clipboard when share is clicked
═══════════════════════════════════════════════════════ */
function initShare() {
    const grid = id('articles-grid');
    if (!grid) return;

    grid.addEventListener('click', function (e) {
        const btn = e.target.closest('.action-btn[title="Share"]');
        if (!btn) return;

        // Find the article link inside the same card
        const card = btn.closest('.article-card');
        const link = card ? card.querySelector('.card-read-more') : null;
        const url  = link ? window.location.origin + link.getAttribute('href')
                          : window.location.href;

        // Try to use the modern clipboard API
        if (navigator.clipboard) {
            navigator.clipboard.writeText(url).then(() => {
                showToast('Link copied to clipboard! 📋', 'success');
            });
        } else {
            // Fallback for older browsers
            showToast('Copy this link: ' + url, 'info');
        }
    });
}


/* ═══════════════════════════════════════════════════════
   10. NEWSLETTER FORMS
   Handle subscribe button clicks
═══════════════════════════════════════════════════════ */
function initNewsletterForms() {
    const forms = [
        {
            input:  document.querySelector('.newsletter-form input'),
            button: document.querySelector('.newsletter-form button'),
        },
        {
            input:  document.querySelector('.footer-newsletter input'),
            button: document.querySelector('.footer-newsletter button'),
        }
    ];

    forms.forEach(function ({ input, button }) {
        if (!button || !input) return;

        button.addEventListener('click', async function () {
            const email = input.value.trim();

            if (!email) {
                showToast('Please enter your email address', 'error');
                input.focus();
                return;
            }

            if (!email.includes('@') || !email.includes('.')) {
                showToast('Please enter a valid email address', 'error');
                input.focus();
                return;
            }

            // Disable button while request is in flight
            button.disabled    = true;
            button.textContent = 'Subscribing...';

            try {
                // POST to our Flask API
                const response = await fetch('/api/subscribe', {
                    method:  'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body:    JSON.stringify({ email }),
                });

                const data = await response.json();

                if (data.success) {
                    showToast(data.message, 'success');
                    input.value = '';
                } else {
                    showToast(data.message, 'error');
                }

            } catch (err) {
                showToast('Connection error. Please try again.', 'error');
            } finally {
                // Re-enable the button
                button.disabled   = false;
                button.innerHTML  = 'Subscribe <i class="fas fa-paper-plane"></i>';
            }
        });

        input.addEventListener('keydown', function (e) {
            if (e.key === 'Enter') button.click();
        });
    });
}

/* ═══════════════════════════════════════════════════════
   11. SCROLL EFFECTS
   Header shadow on scroll, back-to-top button
═══════════════════════════════════════════════════════ */
function initScrollEffects() {
    const header = qs('.main-header');

    // Add shadow to header when user scrolls down
    window.addEventListener('scroll', function () {
        if (!header) return;

        if (window.scrollY > 10) {
            header.style.boxShadow = '0 4px 30px rgba(0, 0, 0, 0.5)';
        } else {
            header.style.boxShadow = 'none';
        }
    });

    // Create a Back-to-Top button dynamically
    const backBtn = document.createElement('button');
    backBtn.id = 'back-to-top';
    backBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
    backBtn.title = 'Back to top';

    Object.assign(backBtn.style, {
        position:     'fixed',
        bottom:       '2rem',
        left:         '2rem',
        width:        '44px',
        height:       '44px',
        background:   'rgba(0, 212, 255, 0.15)',
        border:       '1px solid rgba(0, 212, 255, 0.3)',
        borderRadius: '50%',
        color:        '#00d4ff',
        fontSize:     '1rem',
        cursor:       'pointer',
        display:      'flex',
        alignItems:   'center',
        justifyContent: 'center',
        opacity:      '0',
        transform:    'translateY(20px)',
        transition:   'all 0.3s ease',
        zIndex:       '999',
        fontFamily:   'inherit',
    });

    document.body.appendChild(backBtn);

    // Show/hide based on scroll position
    window.addEventListener('scroll', function () {
        if (window.scrollY > 400) {
            backBtn.style.opacity   = '1';
            backBtn.style.transform = 'translateY(0)';
        } else {
            backBtn.style.opacity   = '0';
            backBtn.style.transform = 'translateY(20px)';
        }
    });

    // Scroll to top when clicked
    backBtn.addEventListener('click', function () {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    // Hover effect
    backBtn.addEventListener('mouseenter', function () {
        this.style.background = 'rgba(0, 212, 255, 0.3)';
    });
    backBtn.addEventListener('mouseleave', function () {
        this.style.background = 'rgba(0, 212, 255, 0.15)';
    });
}


/* ═══════════════════════════════════════════════════════
   12. THREAT LEVEL ANIMATION
   Animates the threat percentage bar on load
═══════════════════════════════════════════════════════ */
function initThreatMeter() {
    const fill = qs('.threat-fill');
    if (!fill) return;

    // Read the target width from the inline style
    const targetWidth = fill.style.width;

    // Start from 0 and animate to target
    fill.style.width = '0%';

    // Delay slightly so the animation is visible after page load
    setTimeout(function () {
        fill.style.transition = 'width 1.5s ease';
        fill.style.width = targetWidth;
    }, 500);
}


/* ═══════════════════════════════════════════════════════
   13. STATS COUNTER ANIMATION
   Numbers count up from 0 to their final value
═══════════════════════════════════════════════════════ */
function animateCounter(element, target, duration = 1500) {
    /*
     * This function counts from 0 to `target` over `duration` ms.
     * It uses requestAnimationFrame for smooth animation.
     */
    let start     = null;
    const initial = 0;

    function step(timestamp) {
        if (!start) start = timestamp;

        // How far through the animation are we? (0.0 to 1.0)
        const progress = Math.min((timestamp - start) / duration, 1);

        // Ease out: starts fast, slows down at the end
        const eased = 1 - Math.pow(1 - progress, 3);

        // Calculate current number
        const current = Math.round(initial + (target - initial) * eased);
        element.textContent = current;

        if (progress < 1) {
            requestAnimationFrame(step);  // keep going
        }
    }

    requestAnimationFrame(step);  // start
}

function initStatsCounters() {
    // Find all stat numbers and animate them
    const statNumbers = qsa('.stat-number');

    statNumbers.forEach(function (el) {
        // Only animate numbers (not the "live" count — it already has a dot)
        const target = parseInt(el.textContent, 10);
        if (!isNaN(target) && target > 0) {
            animateCounter(el, target, 1500);
        }
    });
}


/* ═══════════════════════════════════════════════════════
   14. INTERSECTION OBSERVER — Fade in on scroll
   Cards fade in smoothly as user scrolls down to them
═══════════════════════════════════════════════════════ */
function initScrollAnimations() {
    /*
     * IntersectionObserver watches elements and fires a callback
     * when they enter or leave the viewport (visible area).
     * This is much better than listening to the scroll event.
     */
    const observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (entry.isIntersecting) {
                // Element is now visible — add the 'visible' class
                entry.target.classList.add('is-visible');
                // Stop observing (we only want this to happen once)
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1,       // trigger when 10% of element is visible
        rootMargin: '0px 0px -50px 0px'  // 50px before it enters viewport
    });

    // Observe widgets in the sidebar
    qsa('.widget').forEach(el => observer.observe(el));

    // Observe category cards on the categories page
    qsa('.category-card').forEach(el => observer.observe(el));

    // Observe feature cards on the about page
    qsa('.feature-card').forEach(el => observer.observe(el));
}


/* ═══════════════════════════════════════════════════════
   15. KEYBOARD SHORTCUTS
   Power-user features that make the site feel professional
═══════════════════════════════════════════════════════ */
function initKeyboardShortcuts() {
    document.addEventListener('keydown', function (e) {

        // Don't trigger shortcuts if user is typing in an input
        const tag = document.activeElement.tagName.toLowerCase();
        if (tag === 'input' || tag === 'textarea') return;

        switch (e.key) {
            case '/':
                // Press "/" to focus the search bar (like GitHub/Reddit)
                e.preventDefault();
                const searchInput = id('search-input');
                if (searchInput) {
                    searchInput.focus();
                    searchInput.select();
                }
                break;

            case 'Escape':
                // Press Escape to clear search
                const si = id('search-input');
                if (si && si.value) {
                    si.value      = '';
                    currentSearch = '';
                    const notice  = id('search-notice');
                    if (notice) notice.style.display = 'none';
                    applyFilters();
                }
                break;

            case '1':
                // Press 1 to filter All
                clickFilterBtn('all');
                break;
            case '2':
                clickFilterBtn('Malware');
                break;
            case '3':
                clickFilterBtn('Data Breaches');
                break;
            case '4':
                clickFilterBtn('Vulnerabilities');
                break;
        }
    });
}

// Helper for keyboard shortcuts — simulates clicking a filter button
function clickFilterBtn(category) {
    const btn = qs(`.filter-btn[data-category="${category}"]`);
    if (btn) btn.click();
}


/* ═══════════════════════════════════════════════════════
   16. ACTIVE NAV LINK HIGHLIGHT
   Marks the current page's nav link as active
═══════════════════════════════════════════════════════ */
function initActiveNav() {
    const currentPath = window.location.pathname;
    const navLinks    = qsa('.nav-link');

    navLinks.forEach(function (link) {
        const href = link.getAttribute('href');
        if (href === currentPath) {
            link.classList.add('active');
        } else if (currentPath !== '/' && href !== '/' && currentPath.startsWith(href)) {
            link.classList.add('active');
        }
    });
}


/* ═══════════════════════════════════════════════════════
   ADD CSS for scroll-triggered animations
   We inject this into the page dynamically
═══════════════════════════════════════════════════════ */
function injectAnimationCSS() {
    const style = document.createElement('style');
    style.textContent = `
        /* Elements start invisible and slide up */
        .widget,
        .category-card,
        .feature-card {
            opacity: 0;
            transform: translateY(24px);
            transition: opacity 0.5s ease, transform 0.5s ease;
        }

        /* When JS adds this class, they become visible */
        .widget.is-visible,
        .category-card.is-visible,
        .feature-card.is-visible {
            opacity: 1;
            transform: translateY(0);
        }

        /* Stagger category cards */
        .category-card:nth-child(1) { transition-delay: 0.05s; }
        .category-card:nth-child(2) { transition-delay: 0.10s; }
        .category-card:nth-child(3) { transition-delay: 0.15s; }
        .category-card:nth-child(4) { transition-delay: 0.20s; }
        .category-card:nth-child(5) { transition-delay: 0.25s; }
        .category-card:nth-child(6) { transition-delay: 0.30s; }

        /* Hamburger open state — turns into X */
        .hamburger.open span:nth-child(1) {
            transform: translateY(7px) rotate(45deg);
        }
        .hamburger.open span:nth-child(2) {
            opacity: 0;
            transform: scaleX(0);
        }
        .hamburger.open span:nth-child(3) {
            transform: translateY(-7px) rotate(-45deg);
        }

        /* Smooth hamburger span transitions */
        .hamburger span {
            transition: transform 0.3s ease, opacity 0.3s ease;
        }
    `;
    document.head.appendChild(style);
}


/* ═══════════════════════════════════════════════════════
   LIVE THREAT COUNTER
   Randomly updates the "live threats" number to feel dynamic
═══════════════════════════════════════════════════════ */
function initLiveCounter() {
    const liveCount = qs('.live-count');
    if (!liveCount) return;

    // Every 8 seconds, update the live threat count slightly
    setInterval(function () {
        const current = parseInt(liveCount.textContent, 10);
        // Random change between -1 and +2
        const change  = Math.floor(Math.random() * 4) - 1;
        const next    = Math.max(8, Math.min(20, current + change));

        if (next !== current) {
            // Flash effect
            liveCount.style.transition = 'color 0.3s ease';
            liveCount.style.color      = next > current ? '#ef4444' : '#10b981';

            setTimeout(() => {
                liveCount.textContent  = next;
                liveCount.style.color  = '';
            }, 300);
        }
    }, 8000);
}


/* ═══════════════════════════════════════════════════════
   READING PROGRESS BAR
   Shows a thin bar at top of article pages showing
   how far through the article the user has scrolled
═══════════════════════════════════════════════════════ */
function initReadingProgress() {
    // Only on article pages
    if (!qs('.article-body')) return;

    // Create the progress bar element
    const bar = document.createElement('div');
    bar.id = 'reading-progress';

    Object.assign(bar.style, {
        position:   'fixed',
        top:        '0',
        left:       '0',
        height:     '3px',
        width:      '0%',
        background: 'linear-gradient(90deg, #00d4ff, #7c3aed)',
        zIndex:     '9999',
        transition: 'width 0.1s linear',
    });

    document.body.appendChild(bar);

    // Update bar width as user scrolls
    window.addEventListener('scroll', function () {
        const scrollTop    = window.scrollY;
        const docHeight    = document.documentElement.scrollHeight;
        const windowHeight = window.innerHeight;
        const scrollable   = docHeight - windowHeight;

        if (scrollable > 0) {
            const progress = (scrollTop / scrollable) * 100;
            bar.style.width = progress + '%';
        }
    });
}

/* ═══════════════════════════════════════════════════════
   ALERTS DROPDOWN
═══════════════════════════════════════════════════════ */
function initAlerts() {
    var btn   = document.getElementById('alerts-btn');
    var panel = document.getElementById('alerts-panel');
    var badge = document.getElementById('alerts-count');

    if (!btn || !panel) return;

    // Add overlay for mobile
    var overlay = document.createElement('div');
    overlay.id = 'alerts-overlay';
    overlay.style.cssText = [
        'display: none',
        'position: fixed',
        'inset: 0',
        'background: rgba(0,0,0,0.5)',
        'z-index: 99998',
    ].join(';');
    document.body.appendChild(overlay);

    function openAlerts() {
        panel.classList.add('open');
        overlay.style.display = 'block';
        if (badge) badge.style.display = 'none';
        document.body.style.overflow = 'hidden';
    }

    function closeAlerts() {
        panel.classList.remove('open');
        overlay.style.display = 'none';
        document.body.style.overflow = '';
    }

    btn.addEventListener('click', function(e) {
        e.stopPropagation();
        if (panel.classList.contains('open')) {
            closeAlerts();
        } else {
            openAlerts();
        }
    });

    // Close when clicking overlay
    overlay.addEventListener('click', closeAlerts);

    // Close on Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') closeAlerts();
    });

    // Update badge count
    if (badge) {
        var items = document.querySelectorAll('.alert-item');
        badge.textContent = items.length;
    }
}




/* ═══════════════════════════════════════════════════════
   INIT — Run everything when the page loads
   This is the entry point. Everything starts here.
═══════════════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', function () {

    // Inject animation CSS first
    injectAnimationCSS();

    // Core UI
    initDate();
    initMobileNav();
    initTicker();
    initActiveNav();

    // Interactivity
    initSearch();
    initCategoryFilter();
    initBookmarks();
    initShare();
    initNewsletterForms();

    // Visual effects
    initScrollEffects();
    initThreatMeter();
    initStatsCounters();
    initScrollAnimations();
    initLiveCounter();
    initReadingProgress();

    // Power features
    initKeyboardShortcuts();

    // Personal touches
    initThemeToggle();
    initEasterEgg();

    // Alerts dropdown
    initAlerts();

    // Cool effects
    initTypingEffect();
    initParticles();
    initTerminal();
    initScrollReveal();
    initAboutPage();

    // Show a welcome hint toast after 2 seconds
    setTimeout(function () {
        showToast('💡 Press "/" to quickly search articles', 'info');
    }, 2000);

    console.log('%c CyberNews Loaded ✓ ', 
        'background:#00d4ff; color:#020408; font-weight:bold; padding:4px 8px; border-radius:4px;'
    );
});

/* ═══════════════════════════════════════════════════════
   DARK / LIGHT MODE TOGGLE
═══════════════════════════════════════════════════════ */
function initThemeToggle() {
    var toggle = document.getElementById('theme-toggle');
    var icon   = document.getElementById('theme-icon');
    if (!toggle || !icon) return;

    // Check for saved preference
    var saved = localStorage.getItem('cybernews-theme');
    if (saved === 'light') {
        document.body.classList.add('light-mode');
        icon.className = 'fas fa-moon';
    }

    toggle.addEventListener('click', function () {
        var isLight = document.body.classList.toggle('light-mode');

        if (isLight) {
            icon.className = 'fas fa-moon';
            localStorage.setItem('cybernews-theme', 'light');
            showToast('Light mode activated ☀️', 'info');
        } else {
            icon.className = 'fas fa-sun';
            localStorage.setItem('cybernews-theme', 'dark');
            showToast('Dark mode activated 🌙', 'info');
        }
    });
}


/* ═══════════════════════════════════════════════════════
   EASTER EGG — KONAMI CODE
   ↑ ↑ ↓ ↓ ← → ← → B A
═══════════════════════════════════════════════════════ */
function initEasterEgg() {
    var sequence = [
        'ArrowUp', 'ArrowUp',
        'ArrowDown', 'ArrowDown',
        'ArrowLeft', 'ArrowRight',
        'ArrowLeft', 'ArrowRight',
        'b', 'a'
    ];
    var position = 0;

    document.addEventListener('keydown', function (e) {
        // Don't trigger when typing in inputs
        var tag = document.activeElement.tagName.toLowerCase();
        if (tag === 'input' || tag === 'textarea') return;

        if (e.key === sequence[position]) {
            position++;
            if (position === sequence.length) {
                position = 0;
                activateEasterEgg();
            }
        } else {
            position = 0;
        }
    });
}

function activateEasterEgg() {
    showToast('🎮 Konami Code activated! Welcome, hacker!', 'success');

    // Rainbow border on all cards
    var cards = document.querySelectorAll('.article-card');
    cards.forEach(function (card, i) {
        setTimeout(function () {
            card.style.border = '2px solid';
            card.style.borderImage = 'linear-gradient(135deg, #ef4444, #f59e0b, #10b981, #3b82f6, #8b5cf6) 1';
        }, i * 150);
    });

    // Green overlay flash — Matrix style
    var overlay = document.createElement('div');
    overlay.style.cssText = [
        'position: fixed',
        'inset: 0',
        'z-index: 9998',
        'pointer-events: none',
        'background: rgba(0, 255, 0, 0.05)',
        'transition: opacity 3s ease',
    ].join(';');
    document.body.appendChild(overlay);

    // Create falling characters
    for (var i = 0; i < 50; i++) {
        createMatrixChar(i);
    }

    // Fade out and clean up after 4 seconds
    setTimeout(function () {
        overlay.style.opacity = '0';
        setTimeout(function () {
            overlay.remove();
        }, 3000);
    }, 1000);

    // Reset card borders after 5 seconds
    setTimeout(function () {
        cards.forEach(function (card) {
            card.style.border = '';
            card.style.borderImage = '';
        });
    }, 5000);
}

function createMatrixChar(index) {
    var chars = '01アイウエオカキクケコサシスセソ';
    var el = document.createElement('div');
    var x = Math.random() * 100;

    el.textContent = chars[Math.floor(Math.random() * chars.length)];
    el.style.cssText = [
        'position: fixed',
        'top: -20px',
        'left: ' + x + '%',
        'color: rgba(0, 255, 0, 0.6)',
        'font-family: monospace',
        'font-size: ' + (12 + Math.random() * 14) + 'px',
        'z-index: 9999',
        'pointer-events: none',
        'text-shadow: 0 0 10px rgba(0, 255, 0, 0.8)',
        'animation: matrixFall ' + (2 + Math.random() * 3) + 's linear forwards',
        'animation-delay: ' + (index * 0.1) + 's',
    ].join(';');

    document.body.appendChild(el);

    // Remove after animation
    setTimeout(function () {
        el.remove();
    }, 6000);
}


/* ═══════════════════════════════════════════════════════
   TYPING EFFECT ON HERO SUMMARY
═══════════════════════════════════════════════════════ */
function initTypingEffect() {
    var summary = document.querySelector('.hero-summary');
    if (!summary) return;

    var fullText = summary.textContent.trim();
    summary.textContent = '';
    summary.style.borderRight = '2px solid var(--primary)';

    var i = 0;
    var speed = 20; // milliseconds per character

    function type() {
        if (i < fullText.length) {
            summary.textContent += fullText.charAt(i);
            i++;
            setTimeout(type, speed);
        } else {
            // Remove cursor after typing is done
            setTimeout(function() {
                summary.style.borderRight = 'none';
            }, 1500);
        }
    }

    // Start typing after a short delay
    setTimeout(type, 800);
}


/* ═══════════════════════════════════════════════════════
   FLOATING PARTICLE BACKGROUND
   Creates a network of connected dots — like a cyber map
═══════════════════════════════════════════════════════ */
function initParticles() {
    // Only on homepage (don't slow down other pages)
    if (!document.querySelector('.hero')) return;

    var canvas = document.createElement('canvas');
    canvas.id = 'particle-canvas';
    canvas.style.cssText = [
        'position: fixed',
        'top: 0',
        'left: 0',
        'width: 100%',
        'height: 100%',
        'z-index: -1',
        'pointer-events: none',
        'opacity: 0.4',
    ].join(';');
    document.body.appendChild(canvas);

    var ctx = canvas.getContext('2d');
    var particles = [];
    var particleCount = 40;
    var connectDistance = 150;
    var mouseX = 0;
    var mouseY = 0;

    function resize() {
        canvas.width  = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    resize();
    window.addEventListener('resize', resize);

    // Track mouse for interactive effect
    document.addEventListener('mousemove', function(e) {
        mouseX = e.clientX;
        mouseY = e.clientY;
    });

    // Create particles
    for (var i = 0; i < particleCount; i++) {
        particles.push({
            x:  Math.random() * canvas.width,
            y:  Math.random() * canvas.height,
            vx: (Math.random() - 0.5) * 0.5,
            vy: (Math.random() - 0.5) * 0.5,
            size: Math.random() * 2 + 1,
            color: Math.random() > 0.5 ? '0, 212, 255' : '124, 58, 237',
        });
    }

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Update and draw particles
        for (var i = 0; i < particles.length; i++) {
            var p = particles[i];

            // Move
            p.x += p.vx;
            p.y += p.vy;

            // Bounce off edges
            if (p.x < 0 || p.x > canvas.width)  p.vx *= -1;
            if (p.y < 0 || p.y > canvas.height) p.vy *= -1;

            // Draw particle
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(' + p.color + ', 0.6)';
            ctx.fill();

            // Connect particles near each other
            for (var j = i + 1; j < particles.length; j++) {
                var p2 = particles[j];
                var dx = p.x - p2.x;
                var dy = p.y - p2.y;
                var dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < connectDistance) {
                    var opacity = (1 - dist / connectDistance) * 0.3;
                    ctx.beginPath();
                    ctx.moveTo(p.x, p.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.strokeStyle = 'rgba(0, 212, 255, ' + opacity + ')';
                    ctx.lineWidth = 0.5;
                    ctx.stroke();
                }
            }

            // Connect particles near mouse
            var mx = p.x - mouseX;
            var my = p.y - mouseY;
            var mouseDist = Math.sqrt(mx * mx + my * my);

            if (mouseDist < 200) {
                var mOpacity = (1 - mouseDist / 200) * 0.5;
                ctx.beginPath();
                ctx.moveTo(p.x, p.y);
                ctx.lineTo(mouseX, mouseY);
                ctx.strokeStyle = 'rgba(0, 255, 136, ' + mOpacity + ')';
                ctx.lineWidth = 0.8;
                ctx.stroke();
            }
        }

        requestAnimationFrame(animate);
    }

    animate();
}


/* ═══════════════════════════════════════════════════════
   LIVE TERMINAL WIDGET — Shows REAL website activity
═══════════════════════════════════════════════════════ */

function initTerminal() {
    var terminal = document.getElementById('live-terminal');
    if (!terminal) return;

    var maxLines = 25;
    var commandIndex = 0;

    var staticCommands = [
        'nmap -sS --top-ports 100 192.168.1.0/24',
        'tail -f /var/log/auth.log | grep FAILED',
        'fail2ban-client status sshd',
        'grep BLOCKED /var/log/security.log | tail -5',
        'openssl s_client -connect server:443',
        'systemctl status nginx gunicorn',
        'netstat -tlnp | grep LISTEN',
        'iptables -L INPUT -n | grep DROP',
        'journalctl -u cybernews --since "1 hour ago"',
        'curl -sI https://cyber-news.duckdns.org | head -5',
        'wc -l /var/log/nginx/cybernews_access.log',
        'du -sh /home/hassan007/cybernews/cybernews.db',
    ];

    function addLine(type, text) {
        var line = document.createElement('div');
        line.className = 'terminal-line';

        if (type === 'cmd') {
            line.innerHTML =
                '<span class="t-prompt">sec@cybernews ~$</span> ' +
                '<span class="t-cmd">' + text + '</span>';
        } else {
            var icon = '';
            if (type === 'error')   icon = '&#9888; ';
            if (type === 'warn')    icon = '&#9888; ';
            if (type === 'success') icon = '&#10004; ';

            line.innerHTML =
                '<span class="t-' + type + '">' + icon + text + '</span>';
        }

        terminal.appendChild(line);

        var lines = terminal.querySelectorAll('.terminal-line');
        while (lines.length > maxLines) {
            lines[0].remove();
            lines = terminal.querySelectorAll('.terminal-line');
        }

        terminal.scrollTop = terminal.scrollHeight;
    }

    function fetchRealData() {
        fetch('/api/live-feed')
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (!data.events || data.events.length === 0) return;

                // Show a command first
                var cmd = staticCommands[commandIndex % staticCommands.length];
                addLine('cmd', cmd);
                commandIndex++;

                // Show real events one by one with delays
                var events = data.events;
                var delay = 600;

                events.forEach(function(event, i) {
                    setTimeout(function() {
                        var prefix = '[' + event.time + '] ';
                        addLine(event.type, prefix + event.text);
                    }, delay * (i + 1));
                });
            })
            .catch(function() {
                addLine('warn', 'Connection timeout. Retrying...');
            });
    }

    // Initial boot sequence
    addLine('cmd', 'cybernews --security-monitor --start');
    addLine('success', 'Security monitor v2.0 initialized');
    addLine('info', 'Loading threat intelligence feeds...');

    setTimeout(function() {
        addLine('success', 'Connected to security.log');
        addLine('success', 'Connected to nginx access log');
        addLine('info', 'Monitoring for threats...');
    }, 1500);

    // Fetch real data every 12 seconds
    setTimeout(fetchRealData, 3000);
    setInterval(fetchRealData, 12000);
}


/* ═══════════════════════════════════════════════════════
   SCROLL REVEAL — Fade in elements as they scroll into view
═══════════════════════════════════════════════════════ */
function initScrollReveal() {
    // Add the reveal class to elements we want to animate
    var selectors = [
        '.stat-item',
        '.article-card',
        '.widget',
        '.category-card',
        '.feature-card',
        '.about-text h2',
        '.tech-badge',
    ];

    selectors.forEach(function(selector) {
        var elements = document.querySelectorAll(selector);
        elements.forEach(function(el) {
            el.classList.add('reveal-on-scroll');
        });
    });

    // Create the observer
    var observer = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                entry.target.classList.add('revealed');
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -30px 0px',
    });

    // Observe all elements with the reveal class
    document.querySelectorAll('.reveal-on-scroll').forEach(function(el) {
        observer.observe(el);
    });
}


/* ═══════════════════════════════════════════════════════
   ABOUT PAGE — ANIMATED COUNTERS AND SKILL BARS
═══════════════════════════════════════════════════════ */
function initAboutPage() {
    // Only run on the about page
    if (!document.querySelector('.about-stats-row')) return;

    // ── Animate stat counters ──────────────────────────
    var statNumbers = document.querySelectorAll('.about-stat-number');

    var counterObserver = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (!entry.isIntersecting) return;

            var el     = entry.target;
            var target = parseInt(el.getAttribute('data-target'), 10);
            var start  = 0;
            var duration = 2000;
            var startTime = null;

            function countUp(timestamp) {
                if (!startTime) startTime = timestamp;
                var progress = Math.min((timestamp - startTime) / duration, 1);
                // Ease out cubic
                var eased = 1 - Math.pow(1 - progress, 3);
                el.textContent = Math.round(start + (target - start) * eased);
                if (progress < 1) {
                    requestAnimationFrame(countUp);
                }
            }

            requestAnimationFrame(countUp);
            counterObserver.unobserve(el);
        });
    }, { threshold: 0.5 });

    statNumbers.forEach(function(el) {
        counterObserver.observe(el);
    });

    // ── Animate skill bars ─────────────────────────────
    var skillFills = document.querySelectorAll('.skill-fill');

    var skillObserver = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (!entry.isIntersecting) return;

            var bar   = entry.target;
            var width = bar.getAttribute('data-width');

            setTimeout(function() {
                bar.style.width = width + '%';
            }, 200);

            skillObserver.unobserve(bar);
        });
    }, { threshold: 0.3 });

    skillFills.forEach(function(bar) {
        skillObserver.observe(bar);
    });

    // ── Timeline item animations ───────────────────────
    var timelineItems = document.querySelectorAll('.timeline-item');

    var timelineObserver = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (!entry.isIntersecting) return;

            entry.target.style.opacity  = '1';
            entry.target.style.transform = 'translateX(0)';
            timelineObserver.unobserve(entry.target);
        });
    }, { threshold: 0.2 });

    timelineItems.forEach(function(item, index) {
        item.style.opacity   = '0';
        item.style.transform = 'translateX(-20px)';
        item.style.transition = 'opacity 0.5s ease ' + (index * 0.15) + 's, transform 0.5s ease ' + (index * 0.15) + 's';
        timelineObserver.observe(item);
    });
}

// main.js - CyberNews Interactive Features
// (We'll build this out fully on Day 4)

// Set current date in top bar
document.addEventListener('DOMContentLoaded', function() {
    const dateEl = document.getElementById('current-date');
    if (dateEl) {
        const now = new Date();
        dateEl.textContent = now.toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }

    // Mobile hamburger menu toggle
    const hamburger = document.getElementById('hamburger');
    const nav = document.querySelector('.main-nav');
    if (hamburger && nav) {
        hamburger.addEventListener('click', function() {
            nav.classList.toggle('nav-open');
            hamburger.classList.toggle('open');
        });
    }
});

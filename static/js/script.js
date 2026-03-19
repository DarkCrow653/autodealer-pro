/* AutoDealer Pro — script.js */
'use strict';

document.addEventListener('DOMContentLoaded', function () {

  /* ---- Navbar scroll shadow ---- */
  const navbar = document.querySelector('.navbar-main');
  if (navbar) {
    window.addEventListener('scroll', function () {
      if (window.scrollY > 10) {
        navbar.style.boxShadow = '0 4px 30px rgba(0,0,0,0.5)';
      } else {
        navbar.style.boxShadow = 'none';
      }
    });
  }

  /* ---- Animate cards on scroll ---- */
  const observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });

  document.querySelectorAll('.card-auto').forEach(function (card, i) {
    card.style.opacity = '0';
    card.style.transform = 'translateY(28px)';
    card.style.transition = 'opacity 0.45s ease ' + (i * 0.07) + 's, transform 0.45s ease ' + (i * 0.07) + 's';
    observer.observe(card);
  });

  /* ---- KPI card number animation ---- */
  document.querySelectorAll('.kpi-num').forEach(function (el) {
    const raw = el.textContent.replace(/[^0-9]/g, '');
    if (!raw || raw.length > 8) return;
    const target = parseInt(raw, 10);
    if (isNaN(target) || target === 0) return;
    let current = 0;
    const step = Math.ceil(target / 50);
    const timer = setInterval(function () {
      current = Math.min(current + step, target);
      // Keep original formatting with $ and ,
      const prefix = el.textContent.includes('$') ? '$' : '';
      el.textContent = prefix + current.toLocaleString('es-MX');
      if (current >= target) clearInterval(timer);
    }, 25);
  });

  /* ---- Toggle switch CSS fix ---- */
  document.querySelectorAll('.toggle-switch input').forEach(function (input) {
    input.addEventListener('change', function () {
      const thumb = this.parentElement.querySelector('.toggle-thumb');
      if (thumb) {
        thumb.style.transform = this.checked ? 'translateX(20px)' : 'translateX(0)';
      }
    });
    // Set initial state
    if (input.checked) {
      const thumb = input.parentElement.querySelector('.toggle-thumb');
      if (thumb) thumb.style.transform = 'translateX(20px)';
    }
  });

  /* ---- File upload label update ---- */
  document.querySelectorAll('input[type="file"]').forEach(function (input) {
    input.addEventListener('change', function () {
      const area = this.closest('.file-upload-area');
      if (area && this.files[0]) {
        const p = area.querySelector('p');
        if (p) p.textContent = this.files[0].name;
      }
    });
  });

  /* ---- Search auto-submit debounce ---- */
  const tableSearchInput = document.getElementById('tableSearch');
  if (tableSearchInput) {
    // Already handled inline, just style focus
    tableSearchInput.addEventListener('focus', function () {
      this.style.borderColor = 'var(--gold)';
    });
    tableSearchInput.addEventListener('blur', function () {
      this.style.borderColor = '';
    });
  }

});

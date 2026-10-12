(function () {
  var root = document.documentElement;

  /* theme toggle (dark is the default) */
  var tbtn = document.getElementById('themeBtn');
  if (tbtn) tbtn.addEventListener('click', function () {
    var next = root.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
    root.setAttribute('data-theme', next);
    tbtn.setAttribute('aria-label', next === 'light' ? 'Switch to dark theme' : 'Switch to light theme');
    try { localStorage.setItem('vas-theme', next); } catch (e) {}
  });

  /* header border on scroll */
  var hdr = document.querySelector('.hdr');
  function onScroll() { if (hdr) hdr.classList.toggle('is-scrolled', window.scrollY > 8); }
  onScroll(); window.addEventListener('scroll', onScroll, { passive: true });

  /* mobile menu */
  var burger = document.getElementById('burger'), mnav = document.getElementById('mnav');
  if (burger && mnav) {
    burger.addEventListener('click', function () {
      var open = burger.getAttribute('aria-expanded') !== 'true';
      burger.setAttribute('aria-expanded', open); mnav.classList.toggle('open', open);
      document.body.style.overflow = open ? 'hidden' : '';
    });
    mnav.addEventListener('click', function (e) { if (e.target.closest('a')) { burger.setAttribute('aria-expanded', 'false'); mnav.classList.remove('open'); document.body.style.overflow = ''; } });
  }

  /* reveal on scroll */
  var els = document.querySelectorAll('.rv');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } });
    }, { rootMargin: '0px 0px -8% 0px' });
    els.forEach(function (el) { io.observe(el); });
  } else els.forEach(function (el) { el.classList.add('in'); });

  /* card spotlight */
  document.addEventListener('pointermove', function (e) {
    var c = e.target.closest && e.target.closest('.card'); if (!c) return;
    var r = c.getBoundingClientRect();
    c.style.setProperty('--mx', (e.clientX - r.left) + 'px'); c.style.setProperty('--my', (e.clientY - r.top) + 'px');
  });

  /* count-up numbers */
  var nums = document.querySelectorAll('[data-count]');
  if ('IntersectionObserver' in window && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
    var no = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return; no.unobserve(en.target);
        var el = en.target, end = parseFloat(el.getAttribute('data-count')), dec = (el.getAttribute('data-count').split('.')[1] || '').length;
        var suf = el.getAttribute('data-suffix') || '', t0 = performance.now();
        (function tick(t) {
          var p = Math.min((t - t0) / 1400, 1), v = end * (1 - Math.pow(1 - p, 3));
          el.textContent = v.toFixed(dec) + suf; if (p < 1) requestAnimationFrame(tick);
        })(t0);
      });
    }, { threshold: .6 });
    nums.forEach(function (n) { no.observe(n); });
  }

  /* contact form → opens the visitor's email app */
  var form = document.getElementById('contactForm');
  if (form) form.addEventListener('submit', function (e) {
    e.preventDefault();
    var f = form.elements, topic = f.topic.value;
    var body = 'Name: ' + f.name.value + '\nEmail: ' + f.email.value + (f.company.value ? '\nCompany: ' + f.company.value : '') + '\n\n' + f.message.value;
    window.location.href = 'mailto:info@vasventures.in?subject=' + encodeURIComponent(topic + ' — ' + f.name.value) + '&body=' + encodeURIComponent(body);
  });

  if (form) {
    var key = (location.search.match(/[?&]topic=([a-z]+)/) || [])[1];
    if (key) { var opt = form.querySelector('option[data-key="' + key + '"]'); if (opt) opt.selected = true; }
  }

  var y = document.getElementById('year'); if (y) y.textContent = new Date().getFullYear();
})();

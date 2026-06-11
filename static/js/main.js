// Navbar scroll
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
  navbar?.classList.toggle('scrolled', window.scrollY > 40);
});

// Hamburger
const hamburger = document.getElementById('hamburger');
const navLinks  = document.getElementById('nav-links');
hamburger?.addEventListener('click', () => navLinks?.classList.toggle('open'));
document.querySelectorAll('.nav-links a').forEach(a =>
  a.addEventListener('click', () => navLinks?.classList.remove('open'))
);

// AOS
const aobs = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      const d = parseInt(e.target.dataset.delay || 0);
      setTimeout(() => e.target.classList.add('visible'), d);
    }
  });
}, { threshold: 0.12 });
document.querySelectorAll('[data-aos]').forEach(el => aobs.observe(el));

// Counter
function animateCount(el) {
  const target = parseInt(el.dataset.target);
  const suffix = el.dataset.suffix || '';
  const dur = 1600;
  const start = performance.now();
  const tick = t => {
    const p = Math.min((t - start) / dur, 1);
    const e = 1 - Math.pow(1 - p, 3);
    el.textContent = Math.floor(e * target).toLocaleString('id-ID') + suffix;
    if (p < 1) requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
}
const cobs = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting && !e.target.dataset.animated) {
      e.target.dataset.animated = '1';
      animateCount(e.target);
    }
  });
}, { threshold: 0.5 });
document.querySelectorAll('[data-target]').forEach(el => cobs.observe(el));

// FAQ
document.querySelectorAll('.faq-q').forEach(btn => {
  btn.addEventListener('click', () => {
    const item = btn.closest('.faq-item');
    const open = item.classList.contains('open');
    document.querySelectorAll('.faq-item').forEach(i => i.classList.remove('open'));
    if (!open) item.classList.add('open');
  });
});

// Toast
function showToast(msg, type = 'success') {
  const c = document.getElementById('toast-container') || (() => {
    const el = document.createElement('div');
    el.id = 'toast-container'; el.className = 'toast-container';
    document.body.appendChild(el); return el;
  })();
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.innerHTML = `
    <span style="font-size:1rem;">${type === 'success' ? '✅' : '❌'}</span>
    <div>
      <div style="font-weight:700;font-size:0.82rem;color:var(--slate-800);">${type === 'success' ? 'Berhasil' : 'Gagal'}</div>
      <div style="font-size:0.75rem;color:var(--slate-500);">${msg}</div>
    </div>`;
  c.appendChild(t);
  setTimeout(() => t.remove(), 4000);
}

// Hero search form
document.getElementById('search-form')?.addEventListener('submit', e => {
  e.preventDefault();
  const tipe  = document.getElementById('search-tipe')?.value;
  const harga = document.getElementById('search-harga')?.value;
  const ranges = {
    '0-500000':     [0, 500000],
    '500000-800000':[500000, 800000],
    '800000-1200000':[800000, 1200000],
    '1200000+':[1200000, 9999999]
  };
  let url = '/kos?';
  if (tipe) url += `tipe=${tipe}&`;
  if (harga && ranges[harga]) url += `harga_min=${ranges[harga][0]}&harga_max=${ranges[harga][1]}&`;
  window.location.href = url;
});

// Contact form
document.getElementById('contact-form')?.addEventListener('submit', async e => {
  e.preventDefault();
  const btn = e.target.querySelector('button[type="submit"]');
  btn.disabled = true;
  btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Mengirim…';
  try {
    const res = await fetch('/api/contact', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        nama:   document.getElementById('c-nama')?.value,
        email:  document.getElementById('c-email')?.value,
        subjek: document.getElementById('c-subjek')?.value,
        pesan:  document.getElementById('c-pesan')?.value
      })
    });
    const data = await res.json();
    if (data.success) { showToast(data.message); e.target.reset(); }
    else showToast('Gagal mengirim pesan', 'error');
  } catch { showToast('Terjadi kesalahan', 'error'); }
  finally { btn.disabled = false; btn.innerHTML = '<i class="fas fa-paper-plane"></i> Kirim Pesan'; }
});
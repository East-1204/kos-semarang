// ─── KosSemarang Chatbot — Tanpa API Key, Rule-based + Survey Kos ──────────

const KOS_DATA_CHAT = [
  { id:1, nama:'Kos Putri Cendana', tipe:'putri', harga:800000, harga_display:'Rp 800.000/bulan', kecamatan:'Tembalang', alamat:'Jl. Cendana No. 12, Tembalang', fasilitas:['WiFi','AC','KM Dalam','Parkir'], tersedia:true, kamar_tersisa:3, rating:4.8, pemilik:'Ibu Sari', no_hp:'08123456789', jarak_kampus:'500m dari UNDIP' },
  { id:2, nama:'Kos Putra Merbabu', tipe:'putra', harga:650000, harga_display:'Rp 650.000/bulan', kecamatan:'Banyumanik', alamat:'Jl. Merbabu No. 5, Banyumanik', fasilitas:['WiFi','Kipas','KM Bersama','Parkir'], tersedia:true, kamar_tersisa:5, rating:4.5, pemilik:'Pak Budi', no_hp:'08234567890', jarak_kampus:'1km dari UNDIP' },
  { id:3, nama:'Kos Eksklusif Simpang Lima', tipe:'campur', harga:1500000, harga_display:'Rp 1.500.000/bulan', kecamatan:'Semarang Tengah', alamat:'Jl. Pahlawan No. 21, Semarang Tengah', fasilitas:['WiFi','AC','KM Dalam','Parkir Mobil','CCTV'], tersedia:true, kamar_tersisa:2, rating:4.9, pemilik:'Ibu Dewi', no_hp:'08345678901', jarak_kampus:'3km dari UNDIP' },
  { id:4, nama:'Kos Putri Pelangi', tipe:'putri', harga:700000, harga_display:'Rp 700.000/bulan', kecamatan:'Tembalang', alamat:'Jl. Ngesrep Timur V No. 8, Tembalang', fasilitas:['WiFi','AC','KM Dalam','Parkir'], tersedia:true, kamar_tersisa:4, rating:4.6, pemilik:'Ibu Ratna', no_hp:'08456789012', jarak_kampus:'800m dari UNDIP' },
  { id:5, nama:'Kos Putra Gajahmada', tipe:'putra', harga:550000, harga_display:'Rp 550.000/bulan', kecamatan:'Semarang Barat', alamat:'Jl. Gajahmada No. 45, Semarang Barat', fasilitas:['WiFi','Kipas','KM Bersama','Parkir'], tersedia:true, kamar_tersisa:6, rating:4.3, pemilik:'Pak Agus', no_hp:'08567890123', jarak_kampus:'5km dari UNDIP' },
  { id:6, nama:'Kos Premium Pleburan', tipe:'campur', harga:1200000, harga_display:'Rp 1.200.000/bulan', kecamatan:'Semarang Selatan', alamat:'Jl. Pleburan No. 17, Semarang Selatan', fasilitas:['WiFi','AC','KM Dalam','Parkir','Laundry'], tersedia:true, kamar_tersisa:3, rating:4.7, pemilik:'Ibu Hana', no_hp:'08678901234', jarak_kampus:'300m dari UNDIP Pleburan' },
  { id:7, nama:'Kos Putri Bunga Indah', tipe:'putri', harga:900000, harga_display:'Rp 900.000/bulan', kecamatan:'Tembalang', alamat:'Jl. Prof. Sudarto No. 5, Tembalang', fasilitas:['WiFi','AC','KM Dalam','Parkir','Taman'], tersedia:false, kamar_tersisa:0, rating:4.7, pemilik:'Ibu Lestari', no_hp:'08789012345', jarak_kampus:'400m dari UNDIP' },
  { id:8, nama:'Kos Putra Erlangga', tipe:'putra', harga:750000, harga_display:'Rp 750.000/bulan', kecamatan:'Semarang Selatan', alamat:'Jl. Erlangga Raya No. 9, Semarang Selatan', fasilitas:['WiFi','AC','KM Dalam','Parkir','Dapur'], tersedia:true, kamar_tersisa:2, rating:4.4, pemilik:'Pak Joko', no_hp:'08890123456', jarak_kampus:'1.5km dari UNDIP' },
];

// ─── Simple rule-based chat engine ──────────────────────────────────────────

function processMessage(text, history) {
  const t = text.toLowerCase().trim();

  // Survei kos (kunjungan fisik)
  if (t.includes('survei') || t.includes('survey') || t.includes('kunjungi') || t.includes('lihat langsung') || t.includes('cek langsung')) {
    return {
      type: 'survey_form',
      text: 'Oke, saya bantu jadwalkan survei (kunjungan) ke kos yang Anda minati! 📋\n\nSilakan isi form berikut:'
    };
  }

  // Cari kos murah / budget
  if (t.includes('murah') || t.includes('hemat') || t.includes('ekonomis') || t.match(/\d{3}rb/) || t.includes('budget')) {
    const cheap = KOS_DATA_CHAT.filter(k => k.tersedia && k.harga <= 700000).sort((a,b) => a.harga - b.harga).slice(0, 3);
    return { type: 'kos_list', text: '💰 Berikut kos-kos dengan harga terjangkau yang tersedia:', kos: cheap };
  }

  // Kos putri
  if (t.includes('putri') || t.includes('perempuan') || t.includes('wanita') || t.includes('cewek')) {
    const list = KOS_DATA_CHAT.filter(k => k.tipe === 'putri').slice(0, 3);
    return { type: 'kos_list', text: '👩 Kos putri yang tersedia:', kos: list };
  }

  // Kos putra
  if (t.includes('putra') || t.includes('laki') || t.includes('cowok') || t.includes('pria')) {
    const list = KOS_DATA_CHAT.filter(k => k.tipe === 'putra').slice(0, 3);
    return { type: 'kos_list', text: '👨 Kos putra yang tersedia:', kos: list };
  }

  // Kos campur
  if (t.includes('campur') || t.includes('mixed') || t.includes('bersama')) {
    const list = KOS_DATA_CHAT.filter(k => k.tipe === 'campur').slice(0, 3);
    return { type: 'kos_list', text: '👫 Kos campur yang tersedia:', kos: list };
  }

  // Kos dekat UNDIP / kampus
  if (t.includes('undip') || t.includes('kampus') || t.includes('dekat kampus') || t.includes('tembalang')) {
    const list = KOS_DATA_CHAT.filter(k => k.kecamatan === 'Tembalang').slice(0, 3);
    return { type: 'kos_list', text: '🎓 Kos di sekitar UNDIP (Tembalang):', kos: list };
  }

  // Kos di kecamatan tertentu
  const kecamatanMap = { banyumanik:'Banyumanik', tengah:'Semarang Tengah', selatan:'Semarang Selatan', barat:'Semarang Barat', pleburan:'Semarang Selatan' };
  for (const [key, val] of Object.entries(kecamatanMap)) {
    if (t.includes(key)) {
      const list = KOS_DATA_CHAT.filter(k => k.kecamatan === val).slice(0, 3);
      if (list.length) return { type: 'kos_list', text: `📍 Kos di ${val}:`, kos: list };
    }
  }

  // Booking
  if (t.includes('booking') || t.includes('pesan') || t.includes('sewa') || t.includes('book')) {
    return { type: 'text', text: '📝 Untuk booking kos, silakan:\n1. Buka halaman detail kos yang Anda minati\n2. Isi form booking (nama, HP, tanggal mulai, durasi)\n3. Konfirmasi dan scan QR untuk pembayaran\n\nAtau saya bisa rekomendasikan kos dulu — mau kos seperti apa?' };
  }

  // Harga / tarif
  if (t.includes('harga') || t.includes('tarif') || t.includes('berapa') || t.includes('biaya')) {
    return { type: 'text', text: '💰 Rentang harga kos di KosSemarang.id:\n\n• Ekonomis: Rp 500.000 – 700.000/bulan\n• Standar: Rp 700.000 – 1.000.000/bulan\n• Premium: Rp 1.000.000 – 1.500.000+/bulan\n\nMau rekomendasi sesuai budget tertentu?' };
  }

  // Tips
  if (t.includes('tips') || t.includes('cara memilih') || t.includes('saran') || t.includes('rekomendasi')) {
    return { type: 'text', text: '💡 Tips memilih kos yang baik:\n\n1. **Tentukan budget** — alokasikan maks 30% penghasilan/uang saku\n2. **Cek lokasi** — jarak ke kampus/kantor, akses transportasi\n3. **Perhatikan fasilitas** — WiFi, AC, kamar mandi dalam/luar\n4. **Survei langsung** — jangan hanya dari foto, kunjungi dulu!\n5. **Tanya penghuni lain** — soal keamanan dan kebersihan\n6. **Baca syarat kontrak** — deposit, ketentuan hewan peliharaan, tamu\n\nMau jadwalkan survei ke kos tertentu?' };
  }

  // Perbedaan tipe
  if (t.includes('beda') || t.includes('perbedaan') || t.includes('apa itu') || (t.includes('putra') && t.includes('putri'))) {
    return { type: 'text', text: '🏠 Perbedaan tipe kos:\n\n• **Kos Putra** — khusus laki-laki, biasanya lebih bebas jam malam\n• **Kos Putri** — khusus perempuan, biasanya lebih ketat keamanannya\n• **Kos Campur** — untuk semua gender, biasanya lebih fleksibel\n\nMasing-masing punya peraturan berbeda tergantung pemilik kos.' };
  }

  // Semua kos
  if (t.includes('semua kos') || t.includes('daftar kos') || t.includes('list kos') || t.includes('tampilkan semua')) {
    const list = KOS_DATA_CHAT.filter(k => k.tersedia).slice(0, 4);
    return { type: 'kos_list', text: '🏠 Kos-kos yang saat ini tersedia:', kos: list };
  }

  // Default
  return {
    type: 'text',
    text: 'Halo! Saya Kosi, asisten pencarian kos di Semarang 🏠\n\nSaya bisa bantu Anda:\n• Cari kos sesuai budget & lokasi\n• Info fasilitas dan harga kos\n• Jadwalkan survei (kunjungan) ke kos\n• Tips memilih kos yang baik\n\nCoba tanya: "kos murah di Tembalang" atau "mau survei kos"'
  };
}

// ─── Chatbot Class ────────────────────────────────────────────────────────────

class KosChatbot {
  constructor(opts = {}) {
    this.isWidget = opts.isWidget ?? true;
    this.messages = [];
    this.isTyping = false;
    this.isOpen   = false;

    if (this.isWidget) this.initWidget();
    else               this.initPage();

    this.addWelcome();
  }

  initWidget() {
    this.window     = document.getElementById('chat-window');
    this.btn        = document.getElementById('chat-fab');
    this.messagesEl = document.getElementById('chat-win-msgs');
    this.inputEl    = document.getElementById('chat-win-input');
    this.sendBtn    = document.getElementById('chat-win-send');
    this.closeBtn   = document.getElementById('chat-win-close');

    this.btn?.addEventListener('click',      () => this.toggle());
    this.closeBtn?.addEventListener('click', () => this.close());
    this.sendBtn?.addEventListener('click',  () => this.send());
    this.inputEl?.addEventListener('keydown', e => {
      if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); this.send(); }
    });
    document.querySelectorAll('.quick-chip').forEach(c => {
      c.addEventListener('click', () => {
        if (this.inputEl) this.inputEl.value = c.textContent.trim();
        if (!this.isOpen) this.open();
        this.send();
      });
    });
  }

  initPage() {
    this.messagesEl = document.getElementById('chat-main-messages');
    this.inputEl    = document.getElementById('chat-main-input');
    this.sendBtn    = document.getElementById('chat-main-send');

    this.sendBtn?.addEventListener('click', () => this.send());
    this.inputEl?.addEventListener('keydown', e => {
      if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); this.send(); }
    });
    this.inputEl?.addEventListener('input', () => {
      this.inputEl.style.height = 'auto';
      this.inputEl.style.height = Math.min(this.inputEl.scrollHeight, 150) + 'px';
    });
  }

  toggle() { this.isOpen ? this.close() : this.open(); }
  open() {
    this.isOpen = true;
    this.window?.classList.add('open');
    const icon = this.btn?.querySelector('i');
    if (icon) { icon.classList.remove('fa-robot'); icon.classList.add('fa-times'); }
    setTimeout(() => this.inputEl?.focus(), 250);
  }
  close() {
    this.isOpen = false;
    this.window?.classList.remove('open');
    const icon = this.btn?.querySelector('i');
    if (icon) { icon.classList.remove('fa-times'); icon.classList.add('fa-robot'); }
  }

  time() { return new Date().toLocaleTimeString('id-ID', { hour:'2-digit', minute:'2-digit' }); }

  fmt(text) {
    return text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\n/g, '<br>');
  }

  scroll() { if (this.messagesEl) this.messagesEl.scrollTop = this.messagesEl.scrollHeight; }

  addMsg(content, role = 'bot', extra = '') {
    this.messages.push({ role, content, time: this.time() });
    const formatted = this.fmt(content);
    const t = this.time();
    const el = document.createElement('div');

    if (this.isWidget) {
      el.className = `msg-row ${role}`;
      el.innerHTML = `
        <div class="msg-av"><i class="fas ${role === 'bot' ? 'fa-robot' : 'fa-user'}"></i></div>
        <div>
          <div class="msg-bubble">${formatted}${extra}</div>
          <div class="msg-time">${t}</div>
        </div>`;
    } else {
      el.className = `page-msg-row ${role}`;
      el.innerHTML = `
        <div class="page-msg-av"><i class="fas ${role === 'bot' ? 'fa-robot' : 'fa-user'}"></i></div>
        <div>
          <div class="page-msg-bubble">${formatted}${extra}</div>
          <div class="page-msg-time">${t}</div>
        </div>`;
    }

    this.messagesEl?.appendChild(el);
    this.scroll();
    return el;
  }

  addWelcome() {
    const msg = `Halo! Saya **Kosi**, asisten pencarian kos di Semarang 🏠

Saya bisa bantu:
- Cari kos sesuai budget & lokasi
- Jadwalkan **survei** (kunjungan) ke kos
- Info harga, fasilitas, dan booking
- Tips memilih kos yang tepat

Coba tanya`;
    setTimeout(() => this.addMsg(msg, 'bot'), 400);
  }

  showTyping() {
    const el = document.createElement('div');
    el.id = 'typing-ind';
    el.className = this.isWidget ? 'msg-row bot' : 'page-msg-row bot';
    el.innerHTML = `
      <div class="${this.isWidget ? 'msg-av' : 'page-msg-av'}"><i class="fas fa-robot"></i></div>
      <div class="typing-indicator"><div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div></div>`;
    this.messagesEl?.appendChild(el);
    this.scroll();
  }
  hideTyping() { document.getElementById('typing-ind')?.remove(); }

  // Render kos cards
  buildKosList(kosList) {
    return '<div style="display:flex;flex-direction:column;gap:8px;margin-top:8px;">' +
      kosList.map(k => `
        <a href="/kos/${k.id}" style="
          display:block;padding:10px 12px;
          background:${k.tersedia ? 'var(--blue-50)' : 'var(--slate-100)'};
          border:1px solid ${k.tersedia ? 'var(--blue-100)' : 'var(--slate-200)'};
          border-radius:8px;text-decoration:none;transition:all 0.15s;
        " onmouseover="this.style.borderColor='var(--blue-600)'" onmouseout="this.style.borderColor='${k.tersedia?'var(--blue-100)':'var(--slate-200)'}'">
          <div style="font-weight:700;font-size:0.82rem;color:var(--slate-900);margin-bottom:2px;">${k.nama}</div>
          <div style="font-size:0.72rem;color:var(--slate-500);margin-bottom:4px;">📍 ${k.kecamatan} · ${k.jarak_kampus}</div>
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <span style="font-weight:800;color:var(--blue-600);font-size:0.85rem;">${k.harga_display}</span>
            <span style="font-size:0.7rem;font-weight:600;color:${k.tersedia?'var(--green-500)':'var(--red-500)'};">${k.tersedia?'✅ '+k.kamar_tersisa+' kamar':'❌ Penuh'}</span>
          </div>
        </a>`).join('') +
      '</div>';
  }

  // Survey form HTML
  buildSurveyForm() {
    return `<div class="survey-form" id="survey-form-${Date.now()}">
      <div class="survey-form-row">
        <label class="survey-form-lbl">Nama Lengkap</label>
        <input type="text" placeholder="Nama Anda" class="sf-nama">
      </div>
      <div class="survey-form-row">
        <label class="survey-form-lbl">Nomor HP / WhatsApp</label>
        <input type="tel" placeholder="08xxxxxxxxxx" class="sf-hp">
      </div>
      <div class="survey-form-row">
        <label class="survey-form-lbl">Kos yang Ingin Disurvei</label>
        <select class="sf-kos">
          <option value="">Pilih kos...</option>
          ${KOS_DATA_CHAT.map(k => `<option value="${k.id}">${k.nama} (${k.kecamatan})</option>`).join('')}
        </select>
      </div>
      <div class="survey-form-row">
        <label class="survey-form-lbl">Tanggal Kunjungan</label>
        <input type="date" class="sf-tanggal" min="${new Date().toISOString().split('T')[0]}">
      </div>
      <div class="survey-form-row">
        <label class="survey-form-lbl">Waktu Kunjungan</label>
        <select class="sf-waktu">
          <option value="">Pilih waktu...</option>
          <option>08:00 – 10:00</option>
          <option>10:00 – 12:00</option>
          <option>13:00 – 15:00</option>
          <option>15:00 – 17:00</option>
        </select>
      </div>
      <div class="survey-form-row">
        <label class="survey-form-lbl">Catatan (opsional)</label>
        <textarea placeholder="Hal yang ingin ditanyakan saat survei..." class="sf-catatan" rows="2"></textarea>
      </div>
      <button onclick="window.chatbot.submitSurvey(this.closest('.survey-form'))" class="btn btn-primary btn-sm btn-block" style="margin-top:4px;">
        <i class="fas fa-calendar-check"></i> Jadwalkan Survei
      </button>
    </div>`;
  }

  submitSurvey(form) {
    const nama     = form.querySelector('.sf-nama').value.trim();
    const hp       = form.querySelector('.sf-hp').value.trim();
    const kosId    = form.querySelector('.sf-kos').value;
    const tanggal  = form.querySelector('.sf-tanggal').value;
    const waktu    = form.querySelector('.sf-waktu').value;
    const catatan  = form.querySelector('.sf-catatan').value.trim();

    if (!nama || !hp || !kosId || !tanggal || !waktu) {
      this.addMsg('⚠️ Mohon lengkapi semua field yang wajib diisi ya!', 'bot');
      return;
    }

    const kos = KOS_DATA_CHAT.find(k => k.id === parseInt(kosId));
    const tgl = new Date(tanggal).toLocaleDateString('id-ID', { weekday:'long', year:'numeric', month:'long', day:'numeric' });

    // Disable form
    form.querySelectorAll('input, select, textarea, button').forEach(el => el.disabled = true);

    const konfirmasi = `✅ **Survei berhasil dijadwalkan!**

📋 **Detail Kunjungan:**
- Nama: ${nama}
- Kos: ${kos.nama}
- Alamat: ${kos.alamat}
- Tanggal: ${tgl}
- Waktu: ${waktu}
- HP Pemilik: ${kos.no_hp} (${kos.pemilik})

${catatan ? '📝 Catatan: ' + catatan + '\n\n' : ''}Pemilik kos akan dikonfirmasi melalui WhatsApp ke nomor Anda. Jangan lupa hadir tepat waktu ya! 🏠`;

    setTimeout(() => this.addMsg(konfirmasi, 'bot'), 500);
  }

  sendDirect(text) {
    if (this.isTyping) return;
    document.querySelectorAll('.survey-opt-btn').forEach(b => b.disabled = true);
    if (this.inputEl) { this.inputEl.value = text; this.send(); }
  }

  async send() {
    const text = this.inputEl?.value?.trim();
    if (!text || this.isTyping) return;
    this.inputEl.value = '';
    if (this.inputEl.tagName === 'TEXTAREA') this.inputEl.style.height = 'auto';

    this.addMsg(text, 'user');
    this.isTyping = true;
    this.showTyping();
    if (this.sendBtn) { this.sendBtn.disabled = true; this.sendBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>'; }

    // Simulate small delay for natural feel
    await new Promise(r => setTimeout(r, 600 + Math.random() * 400));

    this.hideTyping();

    const result = processMessage(text, this.messages);

    if (result.type === 'kos_list') {
      const extra = this.buildKosList(result.kos);
      this.addMsg(result.text, 'bot', extra);
    } else if (result.type === 'survey_form') {
      const extra = this.buildSurveyForm();
      this.addMsg(result.text, 'bot', extra);
    } else {
      this.addMsg(result.text, 'bot');
    }

    this.isTyping = false;
    if (this.sendBtn) { this.sendBtn.disabled = false; this.sendBtn.innerHTML = '<i class="fas fa-paper-plane"></i>'; }
  }

  sendMessage() { return this.send(); }
}

// ─── Init ────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const isPage   = !!document.getElementById('chat-main-messages');
  const isWidget = !!document.getElementById('chat-window');

  if (isPage)        window.chatbot = new KosChatbot({ isWidget: false });
  else if (isWidget) window.chatbot = new KosChatbot({ isWidget: true });

  // Booking form
  const bookingForm = document.getElementById('booking-form');
  bookingForm?.addEventListener('submit', async e => {
    e.preventDefault();
    const btn = bookingForm.querySelector('button[type="submit"]');
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Memproses…';

    const data = {
      kos_id:        parseInt(bookingForm.dataset.kosId),
      nama:          document.getElementById('b-nama').value,
      no_hp:         document.getElementById('b-hp').value,
      tanggal_mulai: document.getElementById('b-tanggal').value,
      durasi:        parseInt(document.getElementById('b-durasi').value)
    };

    try {
      const res    = await fetch('/api/booking', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data) });
      const result = await res.json();

      if (result.success) {
        document.getElementById('booking-modal').style.display = 'none';
        document.getElementById('booking-success').style.display = 'block';
        document.getElementById('booking-id-display').textContent = result.booking_id;

        const payUrl = `${window.location.origin}/payment/confirm/${result.booking_id}`;
        const qrImg = document.getElementById('qr-code-img');
        if (qrImg) qrImg.src = `https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=${encodeURIComponent(payUrl)}&bgcolor=ffffff&color=1D4ED8&qzone=1`;

        const priceEl  = document.querySelector('.price-display');
        const amountEl = document.getElementById('payment-amount');
        if (priceEl && amountEl) amountEl.textContent = priceEl.textContent.trim();

        showToast(result.message || 'Booking berhasil!');
      } else {
        showToast(result.message, 'error');
      }
    } catch { showToast('Terjadi kesalahan, coba lagi.', 'error'); }
    finally { btn.disabled = false; btn.innerHTML = '<i class="fas fa-calendar-check"></i> Konfirmasi Booking'; }
  });
});
document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('extScan');
  btn.addEventListener('click', async () => {
    const url = document.getElementById('extUrl').value.trim();
    const out = document.getElementById('extResult');
    out.classList.add('hidden'); out.innerHTML = '';
    if (!url) { out.classList.remove('hidden'); out.innerText = 'Enter a URL first.'; return; }

    try {
      const res = await fetch('http://127.0.0.1:5000/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })
      });
      if (!res.ok) throw new Error('scan failed');
      const data = await res.json();
      const color = data.final_score >= 70 ? 'bg-red-100' : data.final_score >= 40 ? 'bg-yellow-100' : 'bg-green-100';
      out.className = `mt-3 p-3 rounded shadow ${color}`;
      out.innerHTML = `<strong>${data.final_score}</strong> — ${escapeHtml(data.advice || '')}<div class="text-xs text-gray-600 mt-2">${(data.signals || []).slice(0,3).join(', ')}</div>`;
    } catch (e) {
      out.classList.remove('hidden'); out.innerText = 'Error: could not reach backend.';
    }
  });
});

function escapeHtml(unsafe) {
  return String(unsafe).replace(/&/g, '&amp;').replace(/</g, '&lt;');
}

/* script.js
   Simple, beginner-friendly code to integrate the frontend with the Flask backend.
   Expects backend at http://127.0.0.1:5000 exposing:
     - POST /scan  (body: {url: "..."}) -> responds JSON with final_score, signals, redirect_trace, advice
     - GET  /logs   -> array of log objects {url, final_score, signals, timestamp}
*/

// CONFIG: backend endpoints (change if needed)
const BACKEND_SCAN = "http://127.0.0.1:5000/scan";
const BACKEND_LOGS = "http://127.0.0.1:5000/logs";

// Elements
const urlInput = document.getElementById('urlInput');
const scanBtn = document.getElementById('scanBtn');
const toast = document.getElementById('toast');
const signalsCard = document.getElementById('signalsCard');
const signalsList = document.getElementById('signalsList');
const verdictCard = document.getElementById('verdictCard');
const scoreBadge = document.getElementById('scoreBadge');
const adviceText = document.getElementById('adviceText');
const timelineDiv = document.getElementById('timeline');
const scoreChartCtx = document.getElementById('scoreChart')?.getContext('2d');

let localScoreHistory = [];
let scoreChart = null;

// Helper: show small toast
function showToast(text, colorClass='bg-gray-700') {
  toast.innerText = text;
  toast.className = `${colorClass} fixed right-6 top-6 px-4 py-2 rounded shadow text-white`;
  toast.classList.remove('hidden');
  setTimeout(()=> toast.classList.add('hidden'), 2500);
}

// Helper: badge color class
function scoreColorClass(score) {
  if (score >= 70) return 'bg-red-600';
  if (score >= 40) return 'bg-yellow-500 text-black';
  return 'bg-green-600';
}

// Trigger scan
async function scanUrl(url) {
  if (!url) { showToast('Please paste a URL', 'bg-gray-600'); return; }

  showToast('Scanning…', 'bg-blue-500');

  try {
    const res = await fetch(BACKEND_SCAN, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url })
    });

    if (!res.ok) {
      showToast('Server error (scan failed)', 'bg-red-600');
      return;
    }

    const data = await res.json();
    renderResult(data);
    showToast(`Result: ${data.final_score} — ${data.advice}`, scoreColorClass(data.final_score));
  } catch (err) {
    console.error(err);
    showToast('Could not reach backend. Is it running?', 'bg-red-600');
  }
}

// Render the returned JSON into UI
function renderResult(data) {
  // Signals
  signalsList.innerHTML = '';
  if (Array.isArray(data.signals) && data.signals.length) {
    data.signals.forEach(s => {
      const li = document.createElement('li');
      li.className = 'p-2 border rounded text-sm';
      li.innerText = s;
      signalsList.appendChild(li);
    });
    signalsCard.classList.remove('hidden');
  } else {
    signalsCard.classList.add('hidden');
  }

  // Score + advice
  const score = Number(data.final_score) || 0;
  scoreBadge.innerText = score;
  scoreBadge.className = `px-4 py-2 rounded font-semibold text-white ${scoreColorClass(score)}`;
  adviceText.innerText = data.advice || '';

  // Timeline
  timelineDiv.innerHTML = '';
  if (Array.isArray(data.redirect_trace) && data.redirect_trace.length) {
    data.redirect_trace.forEach((hop, idx) => {
      const urlText = (typeof hop === 'string') ? hop : (hop.url || JSON.stringify(hop));
      const node = document.createElement('div');
      node.className = 'inline-flex items-center gap-2';
      node.innerHTML = `<div class="px-3 py-1 bg-gray-100 rounded text-sm">${escapeHtml(urlText)}</div>`;
      timelineDiv.appendChild(node);
      if (idx < data.redirect_trace.length - 1) {
        const arrow = document.createElement('div');
        arrow.className = 'text-gray-400 mx-2';
        arrow.innerText = '➜';
        timelineDiv.appendChild(arrow);
      }
    });
  }

  verdictCard.classList.remove('hidden');

  // Chart update
  localScoreHistory.push(score);
  drawChart();
}

// Simple escape helper
function escapeHtml(unsafe) {
  return String(unsafe).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// Draw or update Chart.js chart
function drawChart() {
  if (!scoreChartCtx) return;
  const labels = localScoreHistory.map((_, i) => `#${i+1}`);
  const data = localScoreHistory;

  if (scoreChart) {
    scoreChart.data.labels = labels;
    scoreChart.data.datasets[0].data = data;
    scoreChart.update();
    return;
  }

  scoreChart = new Chart(scoreChartCtx, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: 'Score (session)',
        data,
        fill: false,
        tension: 0.3,
        borderWidth: 2
      }]
    },
    options: { scales: { y: { min: 0, max: 100 } }, plugins: { legend: { display: false } } }
  });
}

// Event handlers
scanBtn.addEventListener('click', () => scanUrl(urlInput.value.trim()));
urlInput.addEventListener('keydown', (e) => { if (e.key === 'Enter') scanUrl(urlInput.value.trim()); });

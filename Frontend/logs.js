/* logs.js - fetches logs and renders them */

const LOGS_ENDPOINT = "http://127.0.0.1:5000/logs";

const logsTable = document.getElementById('logsTable');
const logSearch = document.getElementById('logSearch');
const refreshBtn = document.getElementById('refreshLogs');

async function fetchLogs() {
  try {
    const res = await fetch(LOGS_ENDPOINT + '?limit=50');
    if (!res.ok) throw new Error('fetch failed');
    const logs = await res.json();
    return logs;
  } catch (e) {
    console.error(e);
    return [];
  }
}

function renderLogs(logs) {
  let html = `<thead class="bg-gray-100"><tr>
      <th class="p-3 text-left">URL</th>
      <th class="p-3">Score</th>
      <th class="p-3">Signals</th>
      <th class="p-3">Time</th>
    </tr></thead><tbody>`;

  if (!Array.isArray(logs) || logs.length === 0) {
    html += `<tr><td class="p-3" colspan="4">No logs found</td></tr>`;
  } else {
    for (const row of logs) {
      const score = row.final_score ?? row.final_score ?? row.heuristic_score ?? 0;
      const signals = row.signals || '';
      const ts = row.timestamp ? (new Date(Number(row.timestamp) * 1000)).toLocaleString() : (row.time || '');
      const bg = score >= 70 ? 'bg-red-50' : score >= 40 ? 'bg-yellow-50' : 'bg-green-50';
      html += `<tr class="${bg}"><td class="p-3 border">${escapeHtml(row.url)}</td><td class="p-3 border">${score}</td><td class="p-3 border">${escapeHtml(signals)}</td><td class="p-3 border">${escapeHtml(ts)}</td></tr>`;
    }
  }

  html += '</tbody>';
  logsTable.innerHTML = html;
}

async function loadAndRenderLogs() {
  const logs = await fetchLogs();
  renderLogs(logs);
}

logSearch?.addEventListener('input', async (e) => {
  const q = e.target.value.trim().toLowerCase();
  const logs = await fetchLogs();
  if (!q) { renderLogs(logs); return; }
  const filtered = logs.filter(r => (r.url || '').toLowerCase().includes(q));
  renderLogs(filtered);
});

refreshBtn?.addEventListener('click', loadAndRenderLogs);

loadAndRenderLogs();

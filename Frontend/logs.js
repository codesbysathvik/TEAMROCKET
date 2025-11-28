// logs.js
const BACKEND_LOGS = "http://127.0.0.1:5000/logs";

const logsTable = document.getElementById("logsTable");
const refreshBtn = document.getElementById("refreshLogs");
const searchBox = document.getElementById("logSearch");

async function loadLogs() {
  logsTable.innerHTML = `
    <tr><td class="p-4 text-gray-500">Loading logs...</td></tr>
  `;
  try {
    const res = await fetch(BACKEND_LOGS, { cache: "no-store" });
    if (!res.ok) {
      logsTable.innerHTML = `
        <tr><td class="p-4 text-red-600">Error loading logs (status ${res.status})</td></tr>
      `;
      return;
    }
    const logs = await res.json();
    renderLogs(logs || []);
  } catch (err) {
    console.error("loadLogs error:", err);
    logsTable.innerHTML = `
      <tr><td class="p-4 text-red-600">Backend unreachable</td></tr>
    `;
  }
}

function renderLogs(logs) {
  const search = (searchBox?.value || "").trim().toLowerCase();
  const filtered = Array.isArray(logs)
    ? logs.filter(l => (l.url || "").toLowerCase().includes(search))
    : [];
  if (!filtered.length) {
    logsTable.innerHTML = `
      <tr><td class="p-4 text-gray-500">No matching logs</td></tr>
    `;
    return;
  }
  logsTable.innerHTML = `
    <thead class="bg-gray-100">
      <tr>
        <th class="p-3 text-left">URL</th>
        <th class="p-3 text-left">Score</th>
        <th class="p-3 text-left">Signals</th>
        <th class="p-3 text-left">Time</th>
      </tr>
    </thead>
    <tbody id="logsBody"></tbody>
  `;
  const body = document.getElementById("logsBody");
  body.innerHTML = "";
  filtered.forEach(log => {
    const tr = document.createElement("tr");
    tr.className = "border-b";
    const ts = log.timestamp ? (new Date(Number(log.timestamp)*1000)).toLocaleString() : "";
    tr.innerHTML = `
      <td class="p-3 align-top break-words">${escapeHtml(log.url || "")}</td>
      <td class="p-3 align-top">${Number(log.final_score || 0)}</td>
      <td class="p-3 align-top break-words">${escapeHtml(log.signals || "")}</td>
      <td class="p-3 align-top">${ts}</td>
    `;
    body.appendChild(tr);
  });
}

function escapeHtml(unsafe) {
  return String(unsafe || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

if (refreshBtn) refreshBtn.addEventListener("click", loadLogs);
if (searchBox) searchBox.addEventListener("input", loadLogs);

// load logs when page opens
window.addEventListener("load", loadLogs);
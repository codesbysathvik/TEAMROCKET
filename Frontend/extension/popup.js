const BACKEND_SCAN = "http://127.0.0.1:5000/scan";

document.addEventListener("DOMContentLoaded", () => {

  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    try {
      let url = tabs?.[0]?.url || "";
      console.log("Active Tab URL:", url);

      // Chrome restricted pages will produce empty
      if (url.startsWith("chrome://") || url.startsWith("chrome-extension://")) {
        document.getElementById("urlInput").value = "";
      } else {
        document.getElementById("urlInput").value = url;
      }
    } catch (e) {
      console.warn("Unable to fetch URL", e);
    }
  });

  document.getElementById("scanBtn").addEventListener("click", scan);
});


async function scan() {
  const url = document.getElementById("urlInput").value.trim();
  if (!url) return alert("Enter a valid URL!");

  toggleLoading(true);

  try {
    const res = await fetch(BACKEND_SCAN, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url })
    });

    const data = await res.json();
    renderResult(data);

  } catch (err) {
    alert("Backend not reachable!");
  }

  toggleLoading(false);
}

function toggleLoading(show) {
  document.getElementById("loader").classList.toggle("hidden", !show);
}

function renderResult(data) {
  document.getElementById("resultBox").classList.remove("hidden");

  let circle = document.querySelector(".score-circle");
  let score = data.final_score;

  circle.style.borderColor =
    score >= 70 ? "#ff3b3b" :
    score >= 40 ? "#ffcc33" :
    "#44ff75";

  document.getElementById("scoreText").innerText = score;
  document.getElementById("adviceText").innerText = data.advice;

  const list = document.getElementById("signalsList");
  list.innerHTML = "";
  data.signals.forEach(sig => {
    const li = document.createElement("li");
    li.innerText = sig;
    list.appendChild(li);
  });
}

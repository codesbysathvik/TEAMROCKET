document.addEventListener("DOMContentLoaded", () => {
    const params = new URLSearchParams(window.location.search);
    const riskyUrl = params.get("url");

    document.getElementById("urlText").innerText = riskyUrl;

    document.getElementById("backBtn").addEventListener("click", () => {
        chrome.tabs.update({ url: "https://www.google.com" });
    });

    document.getElementById("continueBtn").addEventListener("click", () => {
        chrome.tabs.update({ url: riskyUrl });
    });
});

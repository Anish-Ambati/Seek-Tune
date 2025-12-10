// frontend/app.js

const BACKEND_URL = "http://localhost:8000";

const spotifyInput = document.getElementById("spotifyLink");
const spotifyBtn = document.getElementById("spotifyBtn");
const spotifyStatus = document.getElementById("spotifyStatus");
const spotifyResult = document.getElementById("spotifyResult");

const saveFileInput = document.getElementById("saveFile");
const saveBtn = document.getElementById("saveBtn");
const saveStatus = document.getElementById("saveStatus");
const saveResult = document.getElementById("saveResult");

const findFileInput = document.getElementById("findFile");
const findBtn = document.getElementById("findBtn");
const findStatus = document.getElementById("findStatus");
const findResult = document.getElementById("findResult");

async function uploadFile(endpoint, file, statusElem, resultElem) {
  statusElem.textContent = "";
  resultElem.style.display = "none";
  resultElem.textContent = "";

  if (!file) {
    statusElem.textContent = "Please select a file first.";
    statusElem.className = "status error";
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  statusElem.textContent = "Uploading...";
  statusElem.className = "status";

  try {
    const resp = await fetch(`${BACKEND_URL}${endpoint}`, {
      method: "POST",
      body: formData,
    });

    const data = await resp.json();

    if (!resp.ok || data.status === "error") {
      throw new Error(data.detail || "Request failed");
    }

    statusElem.textContent = "Success ✅";
    statusElem.className = "status ok";

    if (endpoint === "/api/save") {
      resultElem.innerHTML =
        `Song saved:<br>` +
        `song_id: <code>${data.song_id}</code><br>` +
        `hashes: <code>${data.hashes}</code><br>` +
        `filename: <code>${data.filename}</code>`;
    } else if (endpoint === "/api/find") {
      const pred = data.prediction;
      resultElem.innerHTML =
        `Prediction:<br>` +
        `Title: <strong>${pred.title}</strong><br>` +
        `Artist: <strong>${pred.artist || "Unknown"}</strong><br>` +
        `Score: <code>${pred.score}</code>`;
    }

    resultElem.style.display = "block";
  } catch (err) {
    console.error(err);
    statusElem.textContent = `Error: ${err.message}`;
    statusElem.className = "status error";
  }
}

saveBtn.addEventListener("click", async () => {
  saveBtn.disabled = true;
  await uploadFile("/api/save", saveFileInput.files[0], saveStatus, saveResult);
  saveBtn.disabled = false;
});

findBtn.addEventListener("click", async () => {
  findBtn.disabled = true;
  await uploadFile("/api/find", findFileInput.files[0], findStatus, findResult);
  findBtn.disabled = false;
});

async function downloadFromSpotify() {
  spotifyStatus.textContent = "";
  spotifyResult.style.display = "none";
  spotifyResult.textContent = "";

  const url = spotifyInput.value.trim();

  if (!url) {
    spotifyStatus.textContent = "Please paste a Spotify track link.";
    spotifyStatus.className = "status error";
    return;
  }

  spotifyStatus.textContent = "Downloading from Spotify...";
  spotifyStatus.className = "status";

  try {
    const resp = await fetch(`${BACKEND_URL}/api/download`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ spotify_url: url }),
    });

    const data = await resp.json();

    if (!resp.ok || data.status === "error") {
      throw new Error(data.detail || "Spotify download failed");
    }

    spotifyStatus.textContent = "Downloaded & fingerprinted ✅";
    spotifyStatus.className = "status ok";

    spotifyResult.innerHTML =
      `Title: <strong>${data.title}</strong><br>` +
      `Artist: <strong>${data.artist}</strong><br>` +
      `Hashes: <code>${data.hashes}</code><br>` +
      `Song ID: <code>${data.song_id}</code>`;

    spotifyResult.style.display = "block";
  } catch (err) {
    console.error(err);
    spotifyStatus.textContent = `Error: ${err.message}`;
    spotifyStatus.className = "status error";
  }
}

spotifyBtn.addEventListener("click", async () => {
  spotifyBtn.disabled = true;
  await downloadFromSpotify();
  spotifyBtn.disabled = false;
});

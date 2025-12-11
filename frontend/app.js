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
      let html = `Prediction:<br>Title: <strong>${pred.title}</strong><br>Artist: <strong>${pred.artist || "Unknown"}</strong>`;
      html+='<br>Score: <code>${pred.score}</code><br>';
      if (pred.spotify_url) {
        html += `<div style="margin-top:0.5rem;"><a href="${pred.spotify_url}" target="_blank" rel="noopener">Open on Spotify</a></div>`;
      }
      if (pred.youtube_url) {
        html += `<div style="margin-top:0.25rem;"><a href="${pred.youtube_url}" target="_blank" rel="noopener">Watch on YouTube</a></div>`;
      }

      resultElem.innerHTML = html;
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

// -------------------- Microphone recording -> POST /api/find --------------------

const micBtn = document.getElementById("micBtn");
const micTimer = document.getElementById("micTimer");
const micStatus = document.getElementById("micStatus");

let mediaRecorder = null;
let micStream = null;
let recordChunks = [];
let recordTimeout = null;
let countdownInterval = null;

async function startRecording() {
  // Reset UI
  micStatus.textContent = "";
  micTimer.textContent = "00:10";
  recordChunks = [];

  try {
    // Ask permission and get stream
    micStream = await navigator.mediaDevices.getUserMedia({ audio: true });
  } catch (err) {
    micStatus.textContent = "Microphone access denied";
    micStatus.className = "status error";
    console.error("getUserMedia error:", err);
    return;
  }

  // Some browsers produce webm/opus; MediaRecorder will pick a supported mime
  try {
    mediaRecorder = new MediaRecorder(micStream);
  } catch (err) {
    micStatus.textContent = "Recording not supported in this browser";
    micStatus.className = "status error";
    console.error("MediaRecorder error:", err);
    micStream.getTracks().forEach(t => t.stop());
    return;
  }

  mediaRecorder.ondataavailable = (e) => {
    if (e.data && e.data.size > 0) recordChunks.push(e.data);
  };

  mediaRecorder.onstart = () => {
    micStatus.textContent = "Recording...";
    micStatus.className = "status";
    micBtn.textContent = "⏹ Stop Recording";
    // start countdown from 10
    let timeLeft = 10;
    micTimer.textContent = `00:${timeLeft.toString().padStart(2,"0")}`;
    countdownInterval = setInterval(() => {
      timeLeft -= 1;
      micTimer.textContent = `00:${timeLeft.toString().padStart(2,"0")}`;
      if (timeLeft <= 0) clearInterval(countdownInterval);
    }, 1000);
  };

  mediaRecorder.onstop = async () => {
    clearInterval(countdownInterval);
    micTimer.textContent = "idle";
    micBtn.textContent = "🎤 Start Recording";
    micStatus.textContent = "Processing clip...";
    micStatus.className = "status";

    // Stop stream tracks
    if (micStream) {
      micStream.getTracks().forEach((t) => t.stop());
      micStream = null;
    }

    // Create blob and create File to send
    const blob = new Blob(recordChunks, { type: recordChunks[0]?.type || "audio/webm" });
    const file = new File([blob], "mic_clip.webm", { type: blob.type });

    // Send to /api/find using existing helper
    try {
      await uploadFile("/api/find", file, findStatus, findResult);
      micStatus.textContent = "Done";
      micStatus.className = "status ok";
    } catch (err) {
      micStatus.textContent = "Error sending clip";
      micStatus.className = "status error";
      console.error("uploadFile error:", err);
    }
  };

  // Start recording
  mediaRecorder.start();

  // Stop automatically after 10 seconds
  recordTimeout = setTimeout(() => {
    if (mediaRecorder && mediaRecorder.state === "recording") {
      mediaRecorder.stop();
    }
  }, 10000);
}

function stopRecordingImmediate() {
  if (recordTimeout) {
    clearTimeout(recordTimeout);
    recordTimeout = null;
  }
  if (mediaRecorder && mediaRecorder.state === "recording") {
    mediaRecorder.stop();
  }
  // Stop mic stream if still active
  if (micStream) {
    micStream.getTracks().forEach((t) => t.stop());
    micStream = null;
  }
}

// Toggle handler
micBtn.addEventListener("click", async () => {
  try {
    if (!mediaRecorder || mediaRecorder.state === "inactive") {
      await startRecording();
    } else if (mediaRecorder.state === "recording") {
      stopRecordingImmediate();
    }
  } catch (err) {
    console.error("mic toggle error:", err);
    micStatus.textContent = "Recording failed";
    micStatus.className = "status error";
  }
});

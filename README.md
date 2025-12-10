# 🎧 SeekTune — Shazam-Style Music Recognition System (Python)

SeekTune is a **Shazam-like music recognition system** built using **Python + FastAPI** that identifies songs from short audio clips using **audio fingerprinting**.

---

# 🚀 Quick Start (Run the Project in 3 Steps)

### **1️⃣ Install dependencies**

```bash
pip install -r requirements.txt
```

(or manually)

```bash
pip install fastapi uvicorn librosa numpy scipy soundfile yt-dlp python-multipart requests
```

---

### **2️⃣ Install FFmpeg**

**Windows:**  
Download from https://ffmpeg.org and add to PATH  
**Linux:**  
```bash
sudo apt install ffmpeg
```

---

### **3️⃣ Set Spotify API Keys**

Create a free app at:  
https://developer.spotify.com/dashboard

Then set:

```bash
setx SPOTIFY_CLIENT_ID "your_client_id"
setx SPOTIFY_CLIENT_SECRET "your_client_secret"
```

Restart terminal once.

---

# ▶️ Run Backend Server

```bash
python main.py serve --port 8000
```

Server will start at:

```
http://localhost:8000
```

---

# ▶️ Run Frontend

```bash
cd frontend
python -m http.server 5500
```

Open browser:

```
http://localhost:5500
```

---

# 🎵 Example Commands

### **Download a song from Spotify + fingerprint it**

```bash
python main.py download https://open.spotify.com/track/0pqnGHJpmpxLKifKRmU6WP
```

### **Recognize a song from clip**

```bash
python main.py find clip.wav
```

---

# 📝 Project Overview

---

## 🚀 Features

- 🎵 Audio fingerprinting using FFT + peak pairing  
- 🔍 Song identification from short audio clips  
- 🌐 FastAPI backend with REST APIs  
- 🎧 Spotify integration (Track → YouTube → WAV → Fingerprint)  
- 🧠 SQLite database for storing fingerprints  
- 🖥️ Web frontend for real-time recognition  
- ⚙️ CLI support (`save`, `find`, `download`, `serve`, `erase`)

---

## 🏗️ System Architecture

```
Spotify URL / Audio File / Audio Clip
              ↓
           FFmpeg
              ↓
        Spectrogram (FFT)
              ↓
     Spectral Peak Detection
              ↓
         Hash Generation
              ↓
        Fingerprint Database
              ↓
       Offset Voting Matcher
              ↓
        🎯 Song Prediction
```


---

## 🧪 API Endpoints

| Method | Route | Description |
|--------|--------|-------------|
| POST | `/api/save` | Upload full song |
| POST | `/api/find` | Upload short clip |
| POST | `/api/download` | Spotify track download |
| GET  | `/health` | Health check |

---

## 🧠 How the Algorithm Works

1. Convert audio → spectrogram using **FFT**
2. Detect **local spectral peaks**
3. Create **hash pairs** from peak combinations
4. Store **(hash, time_offset)** in database
5. For clips:
   - Compute hashes
   - Match against database
   - Vote using **time offset consistency**
6. Song with the **highest match score** is returned

This makes the system:

- ✅ Noise-resistant  
- ✅ Fast  
- ✅ Scalable  

---

## 👨‍💻 Tech Stack

- **Backend:** Python, FastAPI  
- **Audio Processing:** Librosa, NumPy, SciPy  
- **Media Tools:** FFmpeg, yt-dlp  
- **Database:** SQLite  
- **Frontend:** HTML, CSS, JavaScript  
- **External APIs:** Spotify Web API  

---

## 🧪 Demo Flow

1. Paste a Spotify link → Download & fingerprint  
2. Upload a short clip → Recognize song  
3. Get real-time prediction on the UI  

---

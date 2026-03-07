# 🔬 AdaptiveLens: AI-Driven Personalized Learning

[![Hackathon](https://img.shields.io/badge/Hackathon-AI4Dev%20'26-blueviolet?style=for-the-badge)](https://ai4dev.example.com)
[![Team ID](https://img.shields.io/badge/Team%20ID-PS060152-orange?style=for-the-badge)](#)
[![Domain](https://img.shields.io/badge/Domain-Education%20Technology-green?style=for-the-badge)](#)

> **AdaptiveLens** is an AI-powered educational ecosystem designed to democratize learning and improve accessibility. It transforms complex academic content into personalized, level-appropriate knowledge using advanced RAG (Retrieval-Augmented Generation) and NLP techniques.

---

## 🌍 Global Impact & Vision
Built for the **AI4Dev '26 Hackathon** under the theme **AI-Enabled Transformative Technologies for Global Development**, AdaptiveLens addresses the global education gap by:
- **Personalizing Education**: Tailoring content for students, researchers, and lifelong learners.
- **Enhancing Accessibility**: Simplifying jargon-heavy academic papers into digestible knowledge.
- **Skill Assessment**: Generating real-time quizzes to validate understanding.

---

## ✨ Key Features

- **🎯 5-Level Complexity Control**: Instantly shift the explanation depth from *Beginner* to *Researcher* using a dynamic slider.
- **📄 Smart RAG Engine**: Upload PDFs and chat with them using a hybrid search system (Vector + Keyword) for pinpoint accuracy.
- **📊 Readability Scoring**: Every AI response is validated with a real-time **Flesch Reading Ease** score to ensure it matches the target level.
- **📝 Intelligent Quiz Generation**: Automatically generates MCQs and conceptual questions based on your specific learning material.
- **🧠 Knowledge Scaffolding**: Detects prerequisite concepts in the text and offers "bridge" summaries to help you understand advanced topics.
- **⚡ TL;DR Summaries**: Get the "too long; didn't read" essence of any complex document in seconds.

---

## 🔧 Tech Stack

| Layer | Technology | Role |
| :--- | :--- | :--- |
| **Frontend** | Next.js 14, TypeScript, Tailwind CSS | High-performance, responsive UI |
| **Backend** | Python FastAPI | Scalable asynchronous API |
| **AI Model** | Gemini 1.5 Pro | State-of-the-art reasoning |
| **Embeddings** | Google Gemini Embeddings | Semantic representation |
| **Vector DB** | ChromaDB (Persistent) | Contextual document storage |
| **NLP Utilities** | Textstat, Rank Fusion | Readability & Search optimization |

---

## 📁 Project Structure

```bash
AdaptiveLens/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── routers/             # API endpoints (Upload, Chat, Quiz)
│   │   ├── services/            # RAG, NLP & Gemini Logic
│   │   └── db/                  # Vector storage handling
│   └── requirements.txt         # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── app/                 # Next.js Pages
│   │   ├── components/          # React Components (Slider, Chat, PDF)
│   │   └── lib/                 # API Client integration
│   └── package.json             # Frontend dependencies
└── README.md                    # You are here!
```

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- Gemini API Key

### 1. Clone & Install Backend
```bash
cd backend
python -m venv venv
# Activate venv:
# Windows: .\venv\Scripts\activate | Unix: source venv/bin/activate
pip install -r requirements.txt
```
Create a `.env` file in the `backend/` directory:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

### 2. Install Frontend
```bash
cd frontend
npm install
```

---

## 🛠️ Running Locally

1. **Start Backend**:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
2. **Start Frontend**:
   ```bash
   npm run dev
   ```
3. **Access**:
   - Web App: `http://localhost:3000`
   - API Docs: `http://localhost:8000/docs`

---

## ☁️ Deployment Guide

### Deployment Options
For the hackathon demo, we recommend:
1. **Frontend**: [Vercel](https://vercel.com/) (Best for Next.js)
2. **Backend**: [Render](https://render.com/) or [Railway](https://railway.app/) (Best for FastAPI)
3. **Database**: Since ChromaDB uses local storage by default, for persistent cloud storage, use [ChromaDB Managed](https://www.trychroma.com/) or a Dockerized instance with persistent volumes.

### Push to GitHub (Steps for Team)
1. Initialize Git (if not done): `git init`
2. Add files: `git add .`
3. Commit: `git commit -m "feat: initial release for AI4Dev '26"`
4. Create Repo on GitHub and link: `git remote add origin YOUR_REPO_URL`
5. Push: `git push -u origin main`

---

## 🏆 Team Info
- **Team ID**: PS060152
- **Hackathon**: AI4Dev '26
- **Track**: AI-Enabled Transformative Technologies for Global Development

---
*Created with ❤️ for a smarter, more accessible future.*

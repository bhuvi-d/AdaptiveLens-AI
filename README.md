🔬 AdaptiveLens

> **Note** Since this is a live demo hosted on Render's free tier, the backend might need a moment to "wake up" the first time you visit. Also, because we're using a local vector store (ChromaDB) on a temporary server, uploaded documents are session-based , so if the server restarts, you might need to re-upload your PDF to start a new chat!

AdaptiveLens is our take on making learning feel a bit more... human. Academic papers and complex textbooks can be intimidating, so we built a system that translates that complexity into something you can actually use, whether you're a curious student or a deep-dive researcher.



---

### 🌟 What is AdaptiveLens?

Imagine you're reading a dense research paper about quantum physics. Instead of getting stuck on jargon, you just move a slider.
*   **Slide left**, and it explains it like you're in high school. 
*   **Slide right**, and it opens up the technical details for a professional level.

It’s about **AI-driven personalized learning**. We don't just summarize; we adapt the actual language and complexity to match your "vibe" and skill level.

### 🛠️ What it does
- **Smart Conversations**: Upload a PDF and just talk to it. It uses RAG to stay grounded in the actual facts of your document.
- **Complexity at Your Command**: A 5-level slider that shifts the depth of explanations in real-time.
- **Checking Your Progress**: It generates quizzes on the fly to help you see what you've actually absorbed.
- **Bridge the Gap**: It identifies concepts you might not know yet and offers small summaries to help you understand the bigger picture.

---

### 🧩 How it works (The Stack)
We kept it modern and fast:
- **Frontend**: Next.js (React) with a clean, intuitive look.
- **Backend**: Python FastAPI handling the heavy lifting.
- **AI Core**: Powered by **Gemini 1.5 Pro** for the smarts.
- **Memory**: ChromaDB keeps track of your documents and their context.

---

### 🚀 Getting it running on your machine

**1. Backend**
```bash
cd backend
python -m venv venv
# Activate it (venv\Scripts\activate on Windows)
pip install -r requirements.txt
# Add your GOOGLE_API_KEY to a .env file
uvicorn app.main:app --reload
```

**2. Frontend**
```bash
cd frontend
npm install
npm run dev
```

Point your browser to `http://localhost:3000` and you're good to go!

---


*Built with ❤️ to make learning a little less scary and a lot more accessible.*

<div align="center">

<img src="https://img.shields.io/badge/LearnForge_AI-Turn_Every_Page_Into_Progress-6366f1?style=for-the-badge&labelColor=0f0f23&color=6366f1" alt="LearnForge AI"/>

<br/>

```
██╗     ███████╗ █████╗ ██████╗ ███╗   ██╗███████╗ ██████╗ ██████╗  ██████╗ ███████╗     █████╗ ██╗
██║     ██╔════╝██╔══██╗██╔══██╗████╗  ██║██╔════╝██╔═══██╗██╔══██╗██╔════╝ ██╔════╝    ██╔══██╗██║
██║     █████╗  ███████║██████╔╝██╔██╗ ██║█████╗  ██║   ██║██████╔╝██║  ███╗█████╗      ███████║██║
██║     ██╔══╝  ██╔══██║██╔══██╗██║╚██╗██║██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══╝      ██╔══██║██║
███████╗███████╗██║  ██║██║  ██║██║ ╚████║██║     ╚██████╔╝██║  ██║╚██████╔╝███████╗    ██║  ██║██║
╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝    ╚═╝  ╚═╝╚═╝
```

### ✨ *"Turn Every Page Into Progress"* ✨

<br/>

[![React](https://img.shields.io/badge/React_19-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python_3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS_v4-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![Vite](https://img.shields.io/badge/Vite-646CFF?style=flat-square&logo=vite&logoColor=white)](https://vitejs.dev/)
[![Google Gemini](https://img.shields.io/badge/Google_Gemini_AI-4285F4?style=flat-square&logo=google&logoColor=white)](https://deepmind.google/technologies/gemini/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

<br/>

**[🚀 Live Demo](#-quick-start)** • **[📸 Screenshots](#-screenshots)** • **[⚙️ Features](#-features)** • **[🏗️ Architecture](#️-architecture)** • **[📖 Docs](#-api-documentation)**

</div>

---

## 🎯 What is LearnForge AI?

**LearnForge AI** is a **production-grade, AI-powered student learning and assessment platform** that transforms any study material into a personalized learning experience. Upload your PDFs, DOCX, PPTX, or TXT files — LearnForge AI will intelligently extract content, generate unique exam questions, run timed assessments, provide deep AI feedback, and build a tailored revision plan — all powered by **Google Gemini AI**.

> 🔥 **No two exams are alike.** Our AI engine generates fresh, non-repeating questions every single time — grounded strictly in *your* study materials.

---

## ✨ Features

### 📚 Smart Document Studio
- **Multi-format upload**: PDF, DOCX, PPTX, TXT — including scanned PDFs with OCR
- **Drag-and-drop** interface with real-time upload progress
- **AI Document Analysis**: Auto-generates summaries, key concepts, definitions, and detected topics
- **Chunk Preview**: See exactly how your document was parsed and indexed
- **Search, filter, tag, rename, delete** — full document management

### 🤖 AI Question Generation Engine
- Powered by **Google Gemini** — questions grounded in *your* source material
- Configurable: **MCQ, True/False, Fill-in-the-blank, Short Answer**
- Difficulty levels: **Easy, Medium, Hard, Mixed**
- Test types: **Practice, Timed Exam, Revision, Challenge**
- **Zero repetition guarantee** — tracks all previously generated questions per user
- 6 question archetypes: definition, mechanism, scenario, differentiation, constraint, implication
- Structured **Pydantic-validated JSON** responses with source references

### ⏱️ Exam Arena
- **Server-enforced countdown timer** — backend validates deadlines, not just JS
- **Question palette** with Answered / Unanswered / Marked-for-Review states
- **Autosave** on every answer change
- Resume after accidental refresh
- Auto-submit on timer expiry
- Full-screen immersive exam layout
- Shuffleable question & option order
- Idempotent submission — safe to submit multiple times

### 📊 Results & Performance Analytics
- Total score, percentage, grade badge
- Topic-wise and difficulty-wise accuracy breakdown
- **Recharts** visualizations: score history, topic accuracy bars, performance distribution
- Full answer review with correct answers + AI explanations
- Comparison with previous attempts

### 🧠 AI Feedback Coach
- For every wrong answer: what you selected → what's correct → why → underlying concept → example → which section to revise → follow-up question
- Personalized performance summary
- Recurring error pattern detection
- Actionable study plan recommendations

### 🔁 Adaptive Revision System — *"Forge My Weaknesses"*
- Identifies low-accuracy topics from your full attempt history
- Auto-generates **targeted practice tests**
- **Spaced-repetition flashcards** (SM-2 algorithm) with 3D flip animation
- **Mistake notebook** — review every wrong answer ever made
- **Daily learning plan** with time-boxed revision sessions
- Topic mastery tracking with visual progress indicators

### 💬 Doubt Solver
- Real-time AI Q&A grounded in your uploaded documents
- Source citations with page/section references
- Context-aware follow-up questions

### 👤 Authentication & Security
- JWT-based access tokens with bcrypt password hashing
- Protected routes — students access only their own data
- Demo mode: instant login for evaluation
- Role-based access (Student / Admin)

### 🎨 Premium UI/UX
- **Dark navy + deep indigo** foundation with electric violet and cyan accents
- Glassmorphism cards, soft gradients, elegant shadows
- Skeleton loading states, empty states, error states
- Fully responsive: desktop, tablet, mobile
- Smooth Framer Motion animations
- Collapsible sidebar with streak indicator

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        LearnForge AI                                │
│                                                                     │
│  ┌──────────────────────┐        ┌──────────────────────────────┐  │
│  │   React 19 Frontend  │ ◄────► │    FastAPI Backend            │  │
│  │                      │  HTTP  │                              │  │
│  │  • Vite + TypeScript │        │  • Python 3.11+              │  │
│  │  • Tailwind CSS v4   │        │  • SQLAlchemy ORM            │  │
│  │  • shadcn/ui         │        │  • Pydantic v2               │  │
│  │  • Framer Motion     │        │  • JWT Auth                  │  │
│  │  • Recharts          │        │  • Modular Routers           │  │
│  │  • TanStack Query    │        │  • Service Layer             │  │
│  └──────────────────────┘        └──────────────────────────────┘  │
│                                            │                        │
│              ┌─────────────────────────────┼───────────────┐        │
│              │                             │               │        │
│    ┌─────────▼──────┐         ┌────────────▼────┐  ┌──────▼──────┐ │
│    │   SQLite DB    │         │  Google Gemini  │  │  PyMuPDF /  │ │
│    │  (PostgreSQL   │         │   AI (LLM)      │  │  python-    │ │
│    │  compatible)   │         │                 │  │  docx/pptx  │ │
│    └────────────────┘         └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### Backend Structure
```
backend/
├── app/
│   ├── main.py              # FastAPI app, CORS, lifespan
│   ├── config.py            # Pydantic Settings
│   ├── database.py          # SQLAlchemy engine
│   ├── dependencies.py      # JWT auth dependency
│   ├── models/              # 6 SQLAlchemy models
│   │   ├── user.py
│   │   ├── document.py
│   │   ├── test.py
│   │   ├── attempt.py
│   │   ├── revision.py
│   │   └── doubt.py
│   ├── schemas/             # Pydantic DTOs
│   ├── routers/             # 9 API routers
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── documents.py
│   │   ├── tests.py
│   │   ├── attempts.py
│   │   ├── analytics.py
│   │   ├── revision.py
│   │   ├── doubts.py
│   │   └── export.py
│   ├── services/            # Business logic
│   │   ├── ai_generator.py  # Gemini + question synthesis
│   │   ├── document_service.py
│   │   ├── exam_service.py
│   │   ├── feedback_coach.py
│   │   ├── revision_service.py
│   │   └── pdf_service.py
│   └── seeds/
│       └── seed_data.py     # Demo student + data
├── tests/
│   ├── test_auth.py
│   └── test_tests_and_exam.py
├── requirements.txt
└── Dockerfile
```

### Frontend Structure
```
frontend/
├── src/
│   ├── App.tsx               # Router + ProtectedRoute
│   ├── context/
│   │   └── AuthContext.tsx   # JWT auth context
│   ├── lib/
│   │   └── api.ts            # apiFetch wrapper
│   ├── components/
│   │   ├── logo/             # Custom SVG logo
│   │   └── layout/           # AppLayout, sidebar
│   ├── pages/
│   │   ├── LandingPage.tsx
│   │   ├── LoginPage.tsx
│   │   ├── RegisterPage.tsx
│   │   ├── DashboardPage.tsx
│   │   ├── DocumentsPage.tsx
│   │   ├── CreateTestPage.tsx
│   │   ├── ExamPage.tsx
│   │   ├── ExamResultsPage.tsx
│   │   ├── RevisionHubPage.tsx
│   │   ├── DoubtSolverPage.tsx
│   │   └── ProfilePage.tsx
│   └── types/
│       └── index.ts          # TypeScript interfaces
├── vite.config.ts
└── Dockerfile
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git

### 1️⃣ Clone the repository
```bash
git clone https://github.com/SANTHOSH478dev/LearnForge-.git
cd LearnForge-
```

### 2️⃣ Set up the Backend
```bash
# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Copy environment file
cp backend/.env.example backend/.env
# Optional: Add your GEMINI_API_KEY in backend/.env for real AI features

# Start the backend
cd backend
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
> 📝 The database auto-creates and seeds demo data on first run!

### 3️⃣ Set up the Frontend
```bash
cd frontend
npm install
npm run dev
```

### 4️⃣ Open the app
```
http://localhost:5173
```

### 🎭 Demo Login (no signup needed!)
| Field    | Value                    |
|----------|--------------------------|
| Email    | `student@learnforge.ai`  |
| Password | `password123`            |

> Or click the **"⚡ Instant Demo Login"** button on the login page!

---

## 🐳 Docker (Full Stack)

```bash
# From the project root
docker-compose up --build
```
- Frontend → `http://localhost:3000`
- Backend API → `http://localhost:8000`
- API Docs → `http://localhost:8000/docs`

---

## 🔑 Environment Variables

Create `backend/.env` from the example:

```env
# AI (optional — fallback synthesizer works without a key)
GEMINI_API_KEY=your_gemini_api_key_here

# Security
SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Database (defaults to SQLite)
DATABASE_URL=sqlite:///./learnforge.db

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

> 💡 **No API key needed!** LearnForge AI ships with a built-in Smart Grounded Synthesizer that generates quality questions from document content — completely offline.

---

## 📖 API Documentation

Once the backend is running, explore the auto-generated interactive docs:

| Interface | URL |
|-----------|-----|
| 🔵 Swagger UI | [http://localhost:8000/docs](http://localhost:8000/docs) |
| 🟠 ReDoc | [http://localhost:8000/redoc](http://localhost:8000/redoc) |

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/register` | Create student account |
| `POST` | `/api/auth/login` | Get JWT access token |
| `GET`  | `/api/dashboard/stats` | Live dashboard metrics |
| `POST` | `/api/documents/upload` | Upload study material |
| `GET`  | `/api/documents/` | List user documents |
| `POST` | `/api/tests/generate` | Generate AI questions |
| `POST` | `/api/attempts/start` | Start exam attempt |
| `PUT`  | `/api/attempts/{id}/answer` | Save answer (autosave) |
| `POST` | `/api/attempts/{id}/submit` | Submit exam |
| `GET`  | `/api/attempts/{id}/results` | Get results + feedback |
| `GET`  | `/api/revision/weaknesses` | Get weak topic analysis |
| `POST` | `/api/doubts/ask` | Ask a doubt (AI chat) |
| `GET`  | `/api/export/report/{id}` | Download PDF report |

---

## 🧪 Testing

```bash
cd backend

# Run all tests
pytest tests/ -v

# Expected output:
# test_auth.py::test_register_student PASSED
# test_auth.py::test_login_success PASSED
# test_auth.py::test_login_wrong_password PASSED
# test_auth.py::test_protected_route PASSED
# test_auth.py::test_get_profile PASSED
# test_tests_and_exam.py::test_dashboard_stats PASSED
# test_tests_and_exam.py::test_list_documents PASSED
# test_tests_and_exam.py::test_generate_and_exam_flow PASSED
# test_tests_and_exam.py::test_doubt_solver PASSED
# test_tests_and_exam.py::test_pdf_export PASSED
#
# ✅ 10 passed in ~8s
```

---

## 🗺️ Complete User Journey

```
📄 Upload PDF/DOCX/PPTX
        │
        ▼
🔍 AI Extracts & Chunks Content
        │
        ▼
📋 Configure Test (type, difficulty, question count)
        │
        ▼
🤖 Gemini Generates Fresh Questions (zero repeats)
        │
        ▼
⏱️ Exam Arena (server-enforced timer, autosave)
        │
        ▼
✅ Server-side Scoring & Grade
        │
        ▼
🧠 AI Feedback Coach (per-mistake deep explanations)
        │
        ▼
📊 Performance Analytics (charts, topic accuracy)
        │
        ▼
🔁 Forge My Weaknesses (targeted revision plan)
        │
        ▼
🃏 Flashcards + Mistake Notebook + Daily Plan
        │
        ▼
📈 Track Improvement Over Time
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend Framework** | React 19 + TypeScript + Vite |
| **Styling** | Tailwind CSS v4 + shadcn/ui |
| **Animations** | Framer Motion |
| **Charts** | Recharts |
| **State & Routing** | TanStack Query + React Router v7 |
| **Forms** | React Hook Form + Zod |
| **Backend Framework** | FastAPI (Python 3.11+) |
| **Database ORM** | SQLAlchemy + Alembic |
| **Validation** | Pydantic v2 |
| **Auth** | JWT (python-jose) + bcrypt |
| **Database** | SQLite (dev) / PostgreSQL (prod) |
| **AI** | Google Gemini API + Smart Fallback |
| **PDF Processing** | PyMuPDF + pypdf |
| **DOCX/PPTX** | python-docx + python-pptx |
| **PDF Export** | ReportLab |
| **Containers** | Docker + Docker Compose |
| **Web Server** | Nginx (frontend prod) |

---

## 🗓️ Roadmap

- [ ] 🌐 Full PostgreSQL + Redis + Celery for production scale
- [ ] 📱 React Native mobile app
- [ ] 🎓 Instructor dashboard with class analytics
- [ ] 🔗 LMS integrations (Google Classroom, Canvas)
- [ ] 🌍 Multi-language support
- [ ] 🏆 Gamification: Leaderboards, XP, Badges
- [ ] 🤝 Collaborative study rooms
- [ ] 🧩 Plugin system for custom question types
- [ ] 📡 Real-time collaboration via WebSockets
- [ ] ☁️ Firebase Hosting + Cloud Run deployment

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork this repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**SANTHOSH** — [@SANTHOSH478dev](https://github.com/SANTHOSH478dev)

---

<div align="center">

**Built with ❤️ and a lot of ☕**

⭐ **Star this repo** if LearnForge AI helped you! ⭐

*LearnForge AI — Turn Every Page Into Progress*

</div>

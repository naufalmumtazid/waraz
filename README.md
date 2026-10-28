# WARAZ — Coordinated Behavior Detection & Narrative Clarification

> **Kartika Cyber Hackathon 2026 Submission**

**WARAZ** is an AI-powered intelligence platform designed as an advanced analytical layer to detect coordinated bot/buzzer networks and social media narrative manipulation accurately while preserving user privacy. It equips cyber analysts, verification teams, and authorities with powerful tools to map disinformation campaigns and mitigate their impacts systematically.

---

## 🛠️ Tech Stack

- **Frontend:** Next.js (React), Tailwind CSS
- **Backend:** FastAPI (Python 3.10+), Pydantic, Uvicorn
- **Package Management:** `uv` (Fast Python packaging and environment management)
- **Database & Storage:** PostgreSQL / SQLite (via SQLAlchemy)

---

## 🚀 Key Features

1. **Network & Coordinated Behavior Detector**  
   Analyzes simultaneous behavioral patterns, posting time stamps, and interaction structures to identify coordinated bot or buzzer networks[cite: 1].
2. **Issue Clarification & Narrative Engine**  
   Processes and clarifies circulating narratives by rapidly mapping claims, fundamental facts, and actual contexts[cite: 1].
3. **Recycled Media Tracker**  
   Detects old visual content or videos that have been cropped, edited, or reused to push new disinformation narratives[cite: 1].
4. **Manipulation Technique Mapping**  
   Categorizes manipulation methods (such as *framing*, *cherry-picking*, *fear-mongering*, or *astroturfing*) to provide tactical insights for cyber analysts[cite: 1].
5. **Interactive Dashboard & Audit Trail**  
   Presents relationship graphs, narrative flows, and transparent audit trails for deeper analysis and mitigation actions[cite: 1].

---

## ⚡ Getting Started with `uv`

Follow these instructions to set up and run the project locally. Make sure you have **`uv`** installed on your system.

### Prerequisites
- **Node.js**: v18.x or higher
- **Python**: v3.10 or higher
- **`uv`**: Fast Python package installer and resolver ([Installation Guide](https://github.2com/astral-sh/uv))

---

### 1. Backend Setup (FastAPI + `uv`)

1. **Navigate to the backend directory:**
   ```bash
   cd backend
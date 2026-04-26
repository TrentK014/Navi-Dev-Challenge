# Navi Manufacturing Operations Chatbot

A chatbot that answers natural-language questions about a Turkish textile manufacturer's production data — machines, products, BOM variants, route steps, and operation parameters.

## Running Locally

**Prerequisites:** Python 3.11+, Node.js 20+

### 1. Clone the repo

```bash
git clone https://github.com/TrentK014/Navi-Dev-Challenge.git
cd Navi-Dev-Challenge
```

### 2. Start the backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file with your Anthropic API key:

```bash
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
```

Start the server:

```bash
uvicorn main:app --reload
# API runs at http://localhost:8000
```

### 3. Start the frontend

Open a new terminal tab:

```bash
cd frontend
npm install
echo "NEXT_PUBLIC_BACKEND_URL=http://localhost:8000" > .env.local
npm run dev
# UI runs at http://localhost:3000
```

### 4. Open the app

Go to [http://localhost:3000](http://localhost:3000) and start asking questions.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 16, Tailwind CSS |
| Backend | Python, FastAPI, uvicorn |
| Database | SQLite |
| AI | Anthropic Claude API (`claude-sonnet-4-5`) |

# Navi Manufacturing Operations Chatbot

A chatbot that answers natural-language questions about a Turkish textile manufacturer's production data — machines, products, BOM variants, route steps, and operation parameters.

## Tech stack

- **Frontend:** Next.js 16, Tailwind CSS, deployed on Vercel
- **Backend:** FastAPI + uvicorn, deployed on Railway
- **Database:** SQLite (`backend/data/seed.db`)
- **AI:** Anthropic Claude (`claude-sonnet-4-5`) with a `run_sql` tool

## Local development

**Prerequisites:** Python 3.11+, Node.js 20+

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create a .env file with your Anthropic key
echo "ANTHROPIC_API_KEY=sk-..." > .env

uvicorn main:app --reload
# Runs at http://localhost:8000
```

### Frontend

```bash
cd frontend
npm install

# Create .env.local pointing at the local backend
echo "NEXT_PUBLIC_BACKEND_URL=http://localhost:8000" > .env.local

npm run dev
# Runs at http://localhost:3000
```

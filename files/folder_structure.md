# AstroAgent — Folder Structure Reference

Use this as the canonical scaffold. Both Stitch (backend) and Antigravity (frontend)
should match these paths exactly so imports and scripts work out of the box.

```
astroagent/                          ← repo root
│
├── .env.example                     ← safe to commit — template only
├── .env                             ← NEVER commit — your real keys go here
├── .gitignore
├── README.md
├── requirements.txt
│
├── backend/
│   ├── main.py                      ← FastAPI app: CORS, rate limits, route registration
│   │
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── graph.py                 ← LangGraph StateGraph definition & compilation
│   │   ├── state.py                 ← AgentState TypedDict schema
│   │   ├── nodes.py                 ← router_node, reasoning_node, safety_guardrail_node
│   │   └── tools.py                 ← geocode_place, compute_birth_chart,
│   │                                   get_daily_transits, knowledge_lookup
│   │
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── seed.py                  ← One-time script: JSONL → Cohere embed → Chroma
│   │   └── retriever.py             ← retrieve(query, top_k) helper used by tools.py
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   └── session.py               ← SQLite async helpers: save/load/delete session
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── safety.py                ← Guardrail: detect + sanitize certainty claims
│   │   └── validators.py            ← Pydantic v2 schemas (BirthData, ChatRequest, etc.)
│   │
│   ├── data/
│   │   └── astrology_knowledge.jsonl  ← RAG source data (commit this)
│   │
│   ├── chroma_db/                   ← Auto-created by seed.py (gitignored)
│   └── astroagent.db                ← Auto-created at runtime (gitignored)
│
├── frontend/
│   ├── index.html
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   ├── package.json
│   ├── .env.example                 ← VITE_API_URL=http://localhost:8000
│   │
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       │
│       ├── components/
│       │   ├── BirthDetailsForm.tsx  ← react-hook-form + zod, all birth inputs
│       │   ├── ChatInterface.tsx     ← message list, streaming reader, input bar
│       │   ├── MessageBubble.tsx     ← single message: user (gold) or agent (lavender)
│       │   ├── ToolActivityFeed.tsx  ← collapsible panel, tool call status
│       │   └── ConstellationLoader.tsx ← 5-dot pulsing thinking indicator
│       │
│       ├── hooks/
│       │   ├── useChat.ts            ← fetch ReadableStream SSE, token append logic
│       │   └── useSession.ts         ← localStorage UUID, history load, reset
│       │
│       ├── types/
│       │   └── index.ts              ← shared TS interfaces (Message, BirthData, etc.)
│       │
│       └── utils/
│           └── sanitize.ts           ← DOMPurify wrapper for agent output
│
└── evals/
    ├── golden_set.jsonl              ← 25 test cases — commit this, version it
    ├── run_evals.py                  ← Single command runner: python evals/run_evals.py
    ├── EVALUATION.md                 ← Honest reflection on what evals revealed
    │
    └── results/                      ← gitignored — eval run CSVs go here
        └── run_{timestamp}.csv
```

## Setup Order (follow this sequence)

1. Clone repo → copy `.env.example` to `.env` → fill in keys
2. `cd backend && pip install -r requirements.txt`
3. `python rag/seed.py` — seeds Chroma DB (run once; idempotent on reruns)
4. `uvicorn main:app --reload --port 8000`
5. Open new terminal → `cd frontend && npm install && npm run dev`
6. Visit `http://localhost:5173`

## Running Evals

```bash
cd astroagent
python evals/run_evals.py
```

Scorecard prints to console. Results saved to `evals/results/run_{timestamp}.csv`.
Commit `golden_set.jsonl` after any changes so results are reproducible across runs.

## Key Technical Decisions (README summary block)

| Decision | Choice | Reason |
|---|---|---|
| Ephemeris library | `flatlib` | Pure Python — no C compilation on Windows |
| LLM provider | Groq (Llama 3 70B) | Free tier, fast inference |
| Vector DB | Chroma (local) | No cloud account needed |
| Embeddings | Cohere `embed-english-v3.0` | 1,000 free calls/month |
| Session store | SQLite (local) | Zero infrastructure |
| Styling | Tailwind CSS | Utility-first, works naturally with Vite |

**flatlib trade-off**: `flatlib` uses built-in astronomical tables with a fraction-of-an-arcminute
variance vs. the professional Swiss Ephemeris C library. This is imperceptible for chart
readings and daily transits. Accuracy is sufficient for all assignment requirements.
If submitting for production use, consider switching to `pyswisseph` on a Linux/Mac environment.

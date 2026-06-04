# AstroAgent — Daily Spiritual Astrology Companion

AstroAgent is a daily spiritual astrology guide built using a full-stack architecture. It geocodes birth locations, computes complete birth charts, compares daily planetary transits, references traditional astrological knowledge using RAG, and persists conversation histories safely in a local database.

---

## 🌌 System Architecture

The project is structured into three main layers:
1. **Frontend (React + TypeScript + Tailwind CSS)**
   - Capture user birth coordinates dynamically using a validated form.
   - Interactive stream panel supporting Server-Sent Events (SSE) for real-time tokens and tool activity tracing.
   - Collapsible **Astro Tool Chain** feed rendering triggered backend tools, parameters, and statuses.
   - Persistent session storage in `localStorage`.
2. **Backend (FastAPI + LangGraph + SQLite)**
   - **LangGraph Orchestrator**: Directs state loops with safety guards, intent routing, and tool coordination.
   - **Astrology Engine**: Uses `flatlib` to run birth chart calculations and transit separations.
   - **Database Persistence**: Employs async `aiosqlite` to store session details and messages history.
   - **SlowAPI Middleware**: Enforces rate limits (20 requests/minute per client).
3. **AI Subsystem & RAG (Cohere + Chroma DB + Groq)**
   - **Groq Llama 3 70B**: Powers the conversational reasoning loop.
   - **Vector Database**: Persistent local Chroma database storing semantic embeddings generated via Cohere's `embed-english-v3.0` model.

---

## 🛠️ Windows Compatibility & Astrological Math Decisions

### Choice of `flatlib` vs. `pyswisseph`
* **Context**: Traditional Python astrology setups often rely on `pyswisseph` (a wrapper around the Swiss Ephemeris C-library). However, compiling compiled C extensions in a Windows build environment frequently fails without complex Visual Studio build tools.
* **Decision**: We chose **`flatlib`** (a pure-Python astrology library). It runs out of the box on Windows, macOS, and Linux without compiling binary files.
* **Trade-off & Mitigation**:
  - `flatlib` calculations are accurate to within standard orb tolerances (8 degrees) required for general transit interpretations.
  - Coordinate inputs are resolved as standard decimal floats directly from the Google Geocoding API. Since `flatlib.geopos.GeoPos` accepts raw latitude/longitude floats directly (e.g. `GeoPos(19.07, 72.87)`), we completely bypass custom string coordinate parsing (like `'19n07'`), which is prone to format errors.
  - House allocations are calculated using Placidus houses, fortified with custom mathematical range checks to prevent edge-case boundary errors.

---

## 🚀 Setup & Execution

### 1. Prerequisites
Ensure you have Python 3.10+ and Node.js 18+ installed on your system.

### 2. Environment Configuration
Create a `.env` file in the project root containing your API credentials:
```env
# Groq API Key
GROQ_API_KEY=your_groq_api_key_here

# Google Maps API Key (Geocoding & Timezone APIs enabled)
GOOGLE_GEOCODING_API_KEY=your_google_api_key_here

# Cohere API Key (Embedding generation)
COHERE_API_KEY=your_cohere_api_key_here

# Database URL
DATABASE_URL=./astroagent.db

# Frontend CORS origin
ALLOWED_ORIGIN=http://localhost:5173
```

Also, create a `.env` file in the `frontend` directory:
```env
VITE_API_URL=http://localhost:8000
```

### 3. Backend Setup
1. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # macOS/Linux
   ```
2. Install python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Seed the local Chroma Vector Database with astrology context data:
   ```bash
   python backend/rag/seed.py
   ```
4. Start the FastAPI development server:
   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```

### 4. Frontend Setup
1. Navigate to the `frontend/` folder:
   ```bash
   cd frontend
   ```
2. Install npm packages:
   ```bash
   npm install
   ```
3. Launch the Vite local dev server:
   ```bash
   npm run dev
   ```
4. Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 🧪 Evaluation Harness

The project includes a built-in evaluation runner to assert coordinate accuracy, safety override triggers, and topic compliance.
* Test cases are defined in [golden_set.jsonl](evals/golden_set.jsonl).
* To run evaluations, execute:
  ```bash
  python evals/run_evals.py
  ```
The harness will run each case and output a final pass/fail report with statistics.

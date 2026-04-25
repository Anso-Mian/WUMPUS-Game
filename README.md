# Wumpus World Logic Agent

A web-based Knowledge-Based Agent that navigates a Wumpus World-style grid using **Propositional Logic** and **Resolution Refutation** to deduce safe cells and find the gold.

**Stack:** Python (FastAPI) + React (Vite)

## Features

- **Dynamic Grid Sizing**: User-configurable grid dimensions (3x3 to 10x10)
- **Dynamic Hazard Placement**: Randomly placed Pits and Wumpus each episode
- **Percept System**: Stench (adjacent to Wumpus), Breeze (adjacent to Pit), Glitter (on Gold)
- **Propositional Logic KB**: Agent builds knowledge base from percepts using logical rules
- **Resolution Refutation Engine**: Automated theorem prover that converts clauses to CNF and resolves to prove safety
- **Real-Time Metrics Dashboard**: Displays inference steps, KB size, percepts, and more
- **Manual & Auto Modes**: Step-by-step control or fully automated exploration

## Architecture

### Backend (Python / FastAPI)

| File | Purpose |
|---|---|
| `backend/resolution.py` | Resolution Refutation engine - `Clause` class and `ResolutionEngine` with full resolution algorithm |
| `backend/wumpus_world.py` | `WumpusWorld` environment + `WumpusAgent` with KB management |
| `backend/main.py` | FastAPI REST API (`/api/start`, `/api/move`, `/api/auto-step`) |

### Frontend (React / Vite)

| File | Purpose |
|---|---|
| `frontend/src/App.jsx` | Main app component, state management, API calls |
| `frontend/src/components/Grid.jsx` | Visual grid with color-coded cells |
| `frontend/src/components/Metrics.jsx` | Real-time inference metrics |
| `frontend/src/components/Controls.jsx` | Game configuration and movement buttons |
| `frontend/src/App.css` | Dark theme styling |

## How Resolution Refutation Works

1. **KB Construction**: Agent perceives Breeze at (1,1) and adds:
   - `P_0_1 v P_1_0 v P_1_2 v P_2_1` (at least one adjacent cell has a Pit)
   - If no Stench, adds `~W_X_Y` for all adjacent cells

2. **Query**: Before moving to (2,1), agent asks "Is (2,1) safe?"
   - Negates query and adds to KB
   - Runs resolution loop looking for contradiction

3. **Resolution Loop**:
   - Resolves all clause pairs on complementary literals
   - Empty clause = contradiction => query is TRUE (cell is safe)
   - No new clauses = query cannot be proven

## Getting Started

### Backend

```bash
cd backend
pip install -r requirements.txt
python main.py
```
Server runs at `http://localhost:8000`

### Frontend

```bash
cd frontend
npm install
npm run dev
```
App runs at `http://localhost:5173`

## API Endpoints

| Method | Endpoint | Body | Description |
|---|---|---|---|
| POST | `/api/start` | `{ rows, cols }` | Start new game |
| POST | `/api/move` | `{ game_id, direction }` | Move agent (up/down/left/right) |
| POST | `/api/auto-step` | `{ game_id }` | Agent decides and makes one move |

## Deployment

### Backend - Render / Railway

1. Push to GitHub
2. Connect repo on [render.com](https://render.com)
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `python main.py`

### Frontend - Vercel

1. Push to GitHub
2. Import on [vercel.com](https://vercel.com)
3. Root directory: `frontend`
4. Framework preset: Vite
5. Set env var `VITE_API_URL` to your backend URL
6. Deploy

## Project Structure

```
wumpus-world-app-py/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── resolution.py        # Resolution engine
│   ├── wumpus_world.py      # World + Agent
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── main.jsx
│   │   └── components/
│   │       ├── Grid.jsx
│   │       ├── Metrics.jsx
│   │       └── Controls.jsx
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
└── README.md
```

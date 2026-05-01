import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from wumpus_world import WumpusWorld, WumpusAgent

app = FastAPI(title="Wumpus World Logic Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GameRequest(BaseModel):
    rows: int
    cols: int

class MoveRequest(BaseModel):
    game_id: str
    direction: str

class AutoStepRequest(BaseModel):
    game_id: str

games: dict = {}

@app.get("/")
def root():
    return {"status": "ok", "message": "Wumpus World Logic Agent API"}

@app.post("/api/start")
def start_game(req: GameRequest):
    game_id = f"game_{len(games) + 1}"

    world = WumpusWorld(req.rows, req.cols)
    init_percepts = world.initialize()

    agent = WumpusAgent(req.rows, req.cols)
    agent.tell_kb(init_percepts)

    games[game_id] = {
        "world": world,
        "agent": agent,
        "game_over": False,
        "won": False,
        "death_reason": None,
        "revealed": False,
    }

    return {
        "game_id": game_id,
        "agent_pos": world.agent_pos,
        "gold_pos": world.gold_pos,
        "percepts": init_percepts,
        "safe_cells": sorted(agent.safe_cells),
        "visited_cells": sorted(agent.visited),
        "pit_cells": sorted(agent.pit_cells),
        "wumpus_cells": sorted(agent.wumpus_cells),
        "inference_steps": 0,
        "kb_size": len(agent.kb),
        "total_moves": 0,
        "game_over": False,
        "won": False,
    }

@app.post("/api/move")
def move_agent(req: MoveRequest):
    game = games.get(req.game_id)
    if not game or game["game_over"]:
        return {"error": "Invalid or finished game"}

    world = game["world"]
    agent = game["agent"]

    result = world.move_agent(req.direction)
    agent.tell_kb(result["percepts"])

    if result.get("dead"):
        agent.visited.add(f"{world.agent_pos['row']},{world.agent_pos['col']}")
        game["game_over"] = True
        game["revealed"] = True
        game["death_reason"] = result["deathReason"]

        return {
            "agent_pos": world.agent_pos,
            "percepts": result["percepts"],
            "safe_cells": sorted(agent.safe_cells),
            "visited_cells": sorted(agent.visited),
            "pit_cells": sorted(agent.pit_cells),
            "wumpus_cells": sorted(agent.wumpus_cells),
            "inference_steps": agent.total_inference_steps,
            "kb_size": len(agent.kb),
            "total_moves": agent.total_steps,
            "game_over": True,
            "won": False,
            "death_reason": result["deathReason"],
            "revealed": True,
            "bump": False,
        }

    if result.get("won"):
        agent.visited.add(f"{world.agent_pos['row']},{world.agent_pos['col']}")
        agent.safe_cells.add(f"{world.agent_pos['row']},{world.agent_pos['col']}")
        agent.run_inference()
        game["game_over"] = True
        game["won"] = True
        game["revealed"] = True

        return {
            "agent_pos": world.agent_pos,
            "percepts": result["percepts"],
            "safe_cells": sorted(agent.safe_cells),
            "visited_cells": sorted(agent.visited),
            "pit_cells": sorted(agent.pit_cells),
            "wumpus_cells": sorted(agent.wumpus_cells),
            "inference_steps": agent.total_inference_steps,
            "kb_size": len(agent.kb),
            "total_moves": agent.total_steps,
            "game_over": True,
            "won": True,
            "revealed": True,
            "bump": False,
        }

    agent.visited.add(f"{world.agent_pos['row']},{world.agent_pos['col']}")
    agent.safe_cells.add(f"{world.agent_pos['row']},{world.agent_pos['col']}")
    agent.current_pos = dict(world.agent_pos)
    agent.run_inference()

    return {
        "agent_pos": world.agent_pos,
        "percepts": result["percepts"],
        "safe_cells": sorted(agent.safe_cells),
        "visited_cells": sorted(agent.visited),
        "pit_cells": sorted(agent.pit_cells),
        "wumpus_cells": sorted(agent.wumpus_cells),
        "inference_steps": agent.total_inference_steps,
        "kb_size": len(agent.kb),
        "total_moves": agent.total_steps,
        "game_over": False,
        "won": False,
        "bump": result.get("bump", False),
        "revealed": False,
    }

@app.post("/api/auto-step")
def auto_step(req: AutoStepRequest):
    game = games.get(req.game_id)
    if not game or game["game_over"]:
        return {"error": "Invalid or finished game"}

    agent = game["agent"]
    next_move = agent.decide_next_move()

    if not next_move:
        return {"error": "No safe moves available", "stuck": True}

    dr = next_move["row"] - agent.current_pos["row"]
    dc = next_move["col"] - agent.current_pos["col"]

    if dr == -1:
        direction = "up"
    elif dr == 1:
        direction = "down"
    elif dc == -1:
        direction = "left"
    else:
        direction = "right"

    return move_agent(MoveRequest(game_id=req.game_id, direction=direction))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)

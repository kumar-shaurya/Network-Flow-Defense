from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, conlist
import networkx as nx
import sys
import os

# --- Robust Path Finding ---
# Get the directory where *this* file (game.py) is located
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# Go up 3 levels to get to the 'backend' directory
BACKEND_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, '..', '..'))
# Add the 'backend' root to the Python path
sys.path.append(BACKEND_ROOT)

# --- Module Imports (must come AFTER sys.path.append) ---
try:
    from core.graph.generation import generate_graph
    from core.infection.simulation import run_bfs_simulation
    from core.scoring.evaluation import calculate_score
    # We also import these from ml.py to use in the scoring
    from api.routes.ml import model as ml_model, feature_columns as ml_cols, extract_features
except ImportError:
    print("Error: Could not import core game modules. Check sys.path.")
    sys.exit(1)


# --- Global Variables ---
router = APIRouter()

# --- Pydantic Models for Request Body ---
class SimulationRequest(BaseModel):
    graph: dict
    source: int
    target: int
    user_picks: conlist(int, min_length=0) # List of node IDs
    ml_picks: conlist(int, min_length=0) # List of node IDs from ML

# --- API Endpoints ---
@router.post("/new_game")
def get_new_game():
    """
    Generates a new random graph, source, and target.
    """
    try:
        game_data = generate_graph()
        return game_data
    except Exception as e:
        print(f"Error generating new game: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {e}")

@router.post("/simulate")
def run_simulation(data: SimulationRequest = Body(...)):
    """
    Runs the infection simulation based on user's firewall picks.
    """
    try:
        # 1. Run the BFS simulation
        sim_results = run_bfs_simulation(
            graph_data=data.graph,
            source=data.source,
            target=data.target,
            firewalled_nodes=set(data.user_picks)
        )
        
        # 2. Calculate the score
        score_results = calculate_score(
            target_status=sim_results.get("target_status", "INFECTED"),
            user_picks=data.user_picks,
            ml_picks=data.ml_picks
        )
        
        # 3. Combine and return all results
        return {
            "simulation": sim_results,
            "scoring": score_results
        }
        
    except Exception as e:
        print(f"Error during simulation: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {e}")
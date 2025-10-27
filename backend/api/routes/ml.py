import joblib
import pandas as pd
import networkx as nx
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
import os
import sys
import json  # <--- FIX 1: IMPORT THE JSON LIBRARY

# --- Robust Path Finding ---
# This code builds an absolute path to your model files,
# which fixes the "model not found" error on Render.

# Get the directory where *this* file (ml.py) is located
# e.g., /.../backend/api/routes
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Go up 3 levels to get to the 'backend' directory
# /.../backend/api/routes -> /.../backend/api -> /.../backend
BACKEND_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, '..', '..'))

# Add the 'backend' root to the Python path
# This lets us import from 'core' and 'ml' modules
sys.path.append(BACKEND_ROOT)

# Now, build the absolute paths to the model files
MODEL_PATH = os.path.join(BACKEND_ROOT, 'ml', 'models', 'rf_model.pkl')
COLS_PATH = os.path.join(BACKEND_ROOT, 'ml', 'models', 'feature_columns.json')

# --- Module Imports (must come AFTER sys.path.append) ---
try:
    from ml.features.extraction import extract_features
except ImportError:
    print("Error: Could not import 'extract_features'. Check sys.path.")
    sys.exit(1)


# --- Global Variables ---
router = APIRouter()
model = None
feature_columns = None

def load_model():
    """Loads the model and feature columns from disk."""
    global model, feature_columns
    
    print(f"Attempting to load model from: {MODEL_PATH}")
    if not os.path.exists(MODEL_PATH):
        print(f"FATAL ERROR: Model not found at {MODEL_PATH}")
        print("Please run 'python ml/training/train.py' first.")
        return # App will fail, which is correct
        
    if not os.path.exists(COLS_PATH):
        print(f"FATAL ERROR: Feature columns not found at {COLS_PATH}")
        return

    try:
        # Load the model using joblib (binary file)
        model = joblib.load(MODEL_PATH)
        
        # --- FIX 2: USE json.load() for the .json file ---
        with open(COLS_PATH, 'r') as f:
            feature_columns = json.load(f)
        
        print("ML model and feature columns loaded successfully.")
    except Exception as e:
        print(f"Error loading model: {e}")

# --- Pydantic Models for Request Body ---
class MLRequest(BaseModel):
    graph: dict
    source: int
    target: int

# --- API Endpoints ---
@router.post("/predict")
def predict_critical_nodes(data: MLRequest = Body(...)):
    """
    Predicts which nodes are critical to firewall.
    """
    if not model or not feature_columns:
        raise HTTPException(status_code=500, detail="ML model is not loaded.")

    try:
        # Recreate graph from JSON data
        G = nx.node_link_graph(data.graph, directed=False, edges="links")
        
        # 1. Extract features
        features_df = extract_features(G, data.source, data.target)
        
        # 2. Ensure feature columns match training
        # Drop source/target from prediction
        nodes_to_predict = features_df.index.difference([data.source, data.target])
        X_predict = features_df.loc[nodes_to_predict]
        
        # Reorder/fill missing columns
        X_predict_final = pd.DataFrame(columns=feature_columns)
        for col in feature_columns:
            if col in X_predict.columns:
                X_predict_final[col] = X_predict[col]
            else:
                X_predict_final[col] = 0 # Fill missing (should not happen)
        
        # 3. Predict
        predictions = model.predict(X_predict_final)
        
        # 4. Get probabilities for the 'critical' class (1)
        # model.classes_ shows which column is 0 and which is 1
        critical_class_index = list(model.classes_).index(1)
        probabilities = model.predict_proba(X_predict_final)[:, critical_class_index]
        
        # 5. Format results
        results = []
        for node, pred, prob in zip(nodes_to_predict, predictions, probabilities):
            if pred == 1: # Only return nodes predicted as critical
                results.append({
                    "node_id": node,
                    "probability": round(prob, 3)
                })
                
        # Sort by probability (highest first)
        results.sort(key=lambda x: x['probability'], reverse=True)
        
        # Return top 5 suggestions
        return {"predictions": results[:5]}

    except Exception as e:
        print(f"Error during prediction: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {e}")
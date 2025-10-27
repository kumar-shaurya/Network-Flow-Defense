from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os # Import the os module

from api.routes import game, ml

# Create the FastAPI app
app = FastAPI(title="Social Network Infection Challenge")

# --- Event Handlers ---
@app.on_event("startup")
def on_startup():
    print("Server is starting up...")
    ml.load_model() # Load the ML model

# --- Middleware ---

# Define the origins that are allowed to make requests
origins = [
    "http://localhost:3000", # For local React development
]

# --- THIS IS THE KEY CHANGE ---
# We'll get the Vercel frontend URL from an environment variable
# In Render, you will set a variable named 'PROD_ORIGIN'
# to your Vercel URL (e.g., "https://my-app.vercel.app")
prod_origin = os.getenv("PROD_ORIGIN")
if prod_origin:
    print(f"Adding production origin: {prod_origin}")
    origins.append(prod_origin)
# -----------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Routers ---
app.include_router(game.router, prefix="/api/game", tags=["Game"])
app.include_router(ml.router, prefix="/api/ml", tags=["Machine Learning"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Network Flow Defence Backend"}

# To run the app:
# uvicorn api.main:app --reload --port 8000 --app-dir backend

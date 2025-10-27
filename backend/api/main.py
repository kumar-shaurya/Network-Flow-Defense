from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import game, ml

# Create the FastAPI app
app = FastAPI(title="Social Network Infection Challenge")

# --- Event Handlers ---
@app.on_event("startup")
def on_startup():
    print("Server is starting up...")
    ml.load_model() # Load the ML model

# --- Middleware ---
# Allow CORS for the React frontend (running on port 3000)
origins = [
    "http://localhost:3000",
]

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
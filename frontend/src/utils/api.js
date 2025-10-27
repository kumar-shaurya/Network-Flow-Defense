import axios from 'axios';

/**
 * This is the crucial part for deployment.
 * We check for a Vercel-provided "environment variable" called REACT_APP_API_URL.
 *
 * - When you deploy to Vercel, this variable is
 * "https://network-flow-backend.onrender.com"
 *
 * - When you run locally (`npm start`), this variable doesn't exist,
 * so it "falls back" to your local backend URL.
 */
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create a pre-configured axios instance
const api = axios.create({
  baseURL: API_URL,
});

/**
 * Export functions that your App.js imports.
 *
 * Notice how the paths now EXPLICITLY include the "/api" prefix.
 * This ensures the request is always correct, no matter what
 * the baseURL is.
 */

// POST /api/game/new_game
export const getNewGame = () => {
  return api.post('/api/game/new_game');
};

// POST /api/game/simulate
// (Data: { graph, source, target, user_picks })
export const runSimulation = (simulationData) => {
  return api.post('/api/game/simulate', simulationData);
};

// POST /api/ml/predict
// (Data: { graph, source, target })
export const getMlSuggestion = (mlData) => {
  return api.post('/api/ml/predict', mlData);
};

export default api;
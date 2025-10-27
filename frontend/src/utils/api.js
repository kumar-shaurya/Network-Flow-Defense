import axios from 'axios';


const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
// Set up a base instance for axios
const api = axios.create({
  baseURL: API_URL, // Your FastAPI backend URL
});

export const getNewGame = () => {
  return api.post('/game/new_game');
};

export const runSimulation = (graph, source, target, firewalled_nodes) => {
  return api.post('/game/simulate', {
    graph,
    source,
    target,
    firewalled_nodes,
  });
};

export const getMlSuggestion = (graph, source, target, k = 5) => {
  return api.post('/ml/predict', {
    graph,
    source,
    target,
    k,
  });
};
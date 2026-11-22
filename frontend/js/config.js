// Em dev o front roda em localhost:8080 e a API em localhost:8000;
// em produção a API fica no Render.
const LOCAL_HOSTS = ["localhost", "127.0.0.1"];

export const API_BASE_URL = LOCAL_HOSTS.includes(window.location.hostname)
  ? "http://localhost:8000"
  : "https://<servico>.onrender.com";

// ÚNICO módulo que conhece URLs e faz fetch.
import { API_BASE_URL } from "./config.js";

// 90 s cobre o cold start do Render (~1 min) somado à chamada ao Gemini.
const TIMEOUT_MS = 90_000;

export class ApiError extends Error {
  constructor(status, message) {
    super(message);
    this.name = "ApiError";
    this.status = status; // 0 = sem resposta (rede/timeout)
  }
}

// `detail` é string nos erros do app e array de objetos nos 422 do FastAPI.
function detailToText(detail, fallback) {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail) && detail.length > 0) {
    return detail
      .map((e) => {
        const field = Array.isArray(e.loc) ? e.loc[e.loc.length - 1] : null;
        return field ? `${field}: ${e.msg}` : e.msg;
      })
      .join("; ");
  }
  return fallback;
}

async function request(path, { method = "GET", body, headers = {} } = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      method,
      headers: body ? { "Content-Type": "application/json", ...headers } : headers,
      body: body ? JSON.stringify(body) : undefined,
      signal: controller.signal,
    });
  } catch (err) {
    if (err.name === "AbortError") {
      throw new ApiError(0, "O servidor demorou demais para responder.");
    }
    throw new ApiError(0, "Não foi possível conectar ao servidor.");
  } finally {
    clearTimeout(timer);
  }

  if (!response.ok) {
    let detail = null;
    try {
      detail = (await response.json()).detail;
    } catch {
      // corpo vazio ou não-JSON: cai na mensagem genérica
    }
    throw new ApiError(response.status, detailToText(detail, `Erro ${response.status}.`));
  }
  return response.status === 204 ? null : response.json();
}

export const getHealth = () => request("/health");

export function listProducts(query) {
  const q = (query ?? "").trim();
  return request(q ? `/api/products?q=${encodeURIComponent(q)}` : "/api/products");
}

export const getProduct = (id) => request(`/api/products/${id}`);

export const createProduct = ({ name, description }) =>
  request("/api/products", { method: "POST", body: { name, description } });

export const deleteProduct = (id, adminKey) =>
  request(`/api/products/${id}`, { method: "DELETE", headers: { "X-Admin-Key": adminKey } });

export const listTags = () => request("/api/tags");

// Banner de cold start: o Render free dorme após inatividade e a 1ª request demora ~1 min.
import { getHealth } from "../api.js";

const WAKING_AFTER_MS = 2000;

export function mount(element) {
  async function check() {
    element.replaceChildren();
    // Só mostra o aviso se o /health demorar; resposta rápida não pisca banner.
    const timer = setTimeout(() => {
      showBanner("waking", "Acordando servidor, pode levar até 1 minuto…");
    }, WAKING_AFTER_MS);

    try {
      await getHealth();
      element.replaceChildren();
    } catch (err) {
      showBanner("error", `${err.message} `, true);
    } finally {
      clearTimeout(timer);
    }
  }

  function showBanner(kind, text, withRetry = false) {
    const banner = document.createElement("div");
    banner.className = "banner";
    banner.dataset.kind = kind;
    banner.setAttribute("role", kind === "error" ? "alert" : "status");
    const span = document.createElement("span");
    span.textContent = text;
    banner.append(span);
    if (withRetry) {
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = "Tentar de novo";
      button.addEventListener("click", check);
      banner.append(button);
    }
    element.replaceChildren(banner);
  }

  check();
}

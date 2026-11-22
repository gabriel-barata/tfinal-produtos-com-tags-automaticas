// Guarda a chave de administrador no navegador. É só conveniência de UI: quem
// protege a exclusão de verdade é o backend (header X-Admin-Key).
const STORAGE_KEY = "catalog.adminKey";

// localStorage pode lançar (modo privado, dados bloqueados), então tudo passa por try/catch.
// O fallback em memória mantém a chave válida até fechar a aba.
let memoryKey = "";

function readKey() {
  try {
    return localStorage.getItem(STORAGE_KEY) ?? memoryKey;
  } catch {
    return memoryKey;
  }
}

function writeKey(key) {
  memoryKey = key;
  try {
    if (key) localStorage.setItem(STORAGE_KEY, key);
    else localStorage.removeItem(STORAGE_KEY);
  } catch {
    // sem persistência: segue só em memória
  }
}

export function mount(element, { onKeyChange } = {}) {
  element.innerHTML = `
    <form class="admin-form">
      <input type="password" name="key" placeholder="Chave de administrador"
             autocomplete="off" aria-label="Chave de administrador" />
      <button type="submit">Salvar</button>
    </form>
    <small class="admin-hint"></small>
  `;
  const form = element.querySelector("form");
  const hint = element.querySelector(".admin-hint");

  function refresh() {
    const hasKey = Boolean(readKey());
    form.elements.key.value = "";
    hint.textContent = hasKey
      ? "Chave salva: botão de excluir habilitado. Salve em branco para remover."
      : "Informe a chave para poder excluir produtos.";
  }

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    writeKey(form.elements.key.value.trim());
    refresh();
    onKeyChange?.();
  });

  function clearKey() {
    writeKey("");
    refresh();
    onKeyChange?.();
  }

  refresh();
  return { getKey: readKey, clearKey };
}

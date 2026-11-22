// Campo de busca com debounce. Os chips de tag (tag-filters) mexem no mesmo campo
// via addTerm/removeTerm, então o texto digitado é sempre a fonte da verdade.
const DEBOUNCE_MS = 300;
const QUERY_MAX = 200; // espelha o limite do backend

export function mount(element, { onSearch } = {}) {
  element.innerHTML = `
    <input type="search" placeholder="Buscar por tags: tênis azul corrida…"
           maxlength="${QUERY_MAX}" aria-label="Buscar produtos" />
  `;
  const input = element.querySelector("input");
  let timer = null;

  const getTerms = () => input.value.toLowerCase().split(/\s+/).filter(Boolean);

  // Chip clicado não espera o debounce: a ação é discreta, não digitação.
  function searchNow() {
    clearTimeout(timer);
    onSearch?.(input.value.trim());
  }

  input.addEventListener("input", () => {
    clearTimeout(timer);
    timer = setTimeout(searchNow, DEBOUNCE_MS);
  });

  function addTerm(term) {
    if (getTerms().includes(term)) return;
    input.value = `${input.value.trim()} ${term}`.trim();
    searchNow();
  }

  function removeTerm(term) {
    input.value = getTerms()
      .filter((t) => t !== term)
      .join(" ");
    searchNow();
  }

  return { addTerm, removeTerm, getTerms, getQuery: () => input.value.trim() };
}

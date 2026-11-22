// Chips das tags do vocabulário base, agrupadas. Tags livres (`free`) ficam de fora:
// seriam dezenas e poluiriam a tela; elas continuam buscáveis pelo campo de texto.
import { listTags } from "../api.js";

const GROUP_LABELS = [
  ["department", "Departamento"],
  ["sports", "Esporte"],
  ["audience", "Público"],
  ["colors", "Cor"],
];

export function mount(element, { onToggle } = {}) {
  let active = [];
  let tags = [];

  function draw() {
    const groups = [];
    for (const [group, label] of GROUP_LABELS) {
      const items = tags
        .filter((t) => t.group === group)
        .sort((a, b) => b.count - a.count || a.tag.localeCompare(b.tag));
      if (items.length === 0) continue;

      const row = document.createElement("div");
      const title = document.createElement("strong");
      title.textContent = `${label}: `;
      const chips = document.createElement("div");
      chips.className = "chips";
      for (const { tag, count } of items) {
        const chip = document.createElement("button");
        chip.type = "button";
        chip.className = "chip";
        chip.setAttribute("aria-pressed", String(active.includes(tag)));
        chip.append(tag, " ");
        const small = document.createElement("small");
        small.textContent = count;
        chip.append(small);
        chip.addEventListener("click", () => onToggle?.(tag));
        chips.append(chip);
      }
      row.append(title, chips);
      groups.push(row);
    }
    element.replaceChildren(...groups);
  }

  /** Recarrega as contagens da API (após cadastro/exclusão). */
  async function load() {
    try {
      tags = await listTags();
      draw();
    } catch {
      // filtros são acessório: se falharem, o campo de busca continua funcionando
      element.replaceChildren();
    }
  }

  /** `terms`: termos atuais da busca, para marcar os chips ativos. */
  function setActive(terms) {
    active = terms;
    draw();
  }

  return { load, setActive };
}

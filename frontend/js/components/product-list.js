// Grid de cards. Só desenha o que recebe; quem busca os dados é o main.js.
const DESCRIPTION_MAX = 140;

function truncate(text) {
  return text.length <= DESCRIPTION_MAX ? text : `${text.slice(0, DESCRIPTION_MAX).trimEnd()}…`;
}

export function mount(element, { onDelete } = {}) {
  // textContent (nunca innerHTML) nos dados da API: nome/descrição vêm de usuários.
  function buildCard({ product, matched_tags: matched }, canDelete) {
    const article = document.createElement("article");
    article.dataset.id = product.id;

    const title = document.createElement("h3");
    title.textContent = product.name;

    const description = document.createElement("p");
    description.textContent = truncate(product.description);

    const tags = document.createElement("ul");
    tags.className = "chips";
    for (const tag of product.tags) {
      const li = document.createElement("li");
      li.className = matched.includes(tag) ? "chip chip--matched" : "chip";
      li.textContent = tag;
      tags.append(li);
    }

    article.append(title, description, tags);

    if (canDelete) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "secondary outline delete-button";
      button.textContent = "excluir";
      button.addEventListener("click", () => onDelete?.(product));
      article.append(button);
    }
    return article;
  }

  /** `results`: lista de `SearchResultResponse`; `canDelete`: mostra o botão "excluir". */
  function render(results, { canDelete = false } = {}) {
    if (results.length === 0) {
      const empty = document.createElement("p");
      empty.textContent = "Nenhum produto encontrado.";
      element.replaceChildren(empty);
      return;
    }
    const grid = document.createElement("div");
    grid.className = "product-grid";
    grid.append(...results.map((result) => buildCard(result, canDelete)));
    element.replaceChildren(grid);
  }

  function renderError(message) {
    const p = document.createElement("p");
    p.className = "msg-error";
    p.textContent = message;
    element.replaceChildren(p);
  }

  return { render, renderError };
}

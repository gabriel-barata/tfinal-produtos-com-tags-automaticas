// Formulário de cadastro. Os limites espelham o schema do backend (ProductCreateRequest).
import { createProduct } from "../api.js";

const NAME_MIN = 2;
const NAME_MAX = 120;
const DESC_MIN = 10;
const DESC_MAX = 1000;

export function mount(element, { onCreated } = {}) {
  element.innerHTML = `
    <form novalidate>
      <label>Nome
        <input name="name" type="text" maxlength="${NAME_MAX}" required />
      </label>
      <label>Descrição
        <textarea name="description" rows="5" maxlength="${DESC_MAX}" required></textarea>
      </label>
      <button type="submit">Gerar tags e salvar</button>
    </form>
    <p class="form-feedback" role="status" aria-live="polite"></p>
    <ul class="chips form-tags"></ul>
  `;

  const form = element.querySelector("form");
  const button = element.querySelector("button");
  const feedback = element.querySelector(".form-feedback");
  const tagList = element.querySelector(".form-tags");

  function setFeedback(text, kind) {
    feedback.textContent = text;
    feedback.className = `form-feedback ${kind ? `msg-${kind}` : ""}`;
  }

  // Validação só para poupar uma ida ao servidor (e uma chamada ao Gemini);
  // a validação que vale é a do backend.
  function validate(name, description) {
    if (name.length < NAME_MIN || name.length > NAME_MAX) {
      return `O nome deve ter entre ${NAME_MIN} e ${NAME_MAX} caracteres.`;
    }
    if (description.length < DESC_MIN || description.length > DESC_MAX) {
      return `A descrição deve ter entre ${DESC_MIN} e ${DESC_MAX} caracteres.`;
    }
    return null;
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const name = form.elements.name.value.trim();
    const description = form.elements.description.value.trim();
    tagList.replaceChildren();

    const problem = validate(name, description);
    if (problem) {
      setFeedback(problem, "error");
      return;
    }

    button.disabled = true;
    button.setAttribute("aria-busy", "true");
    setFeedback("IA gerando tags…", "");
    try {
      const product = await createProduct({ name, description });
      setFeedback(`✓ Produto "${product.name}" criado com as tags:`, "ok");
      for (const tag of product.tags) {
        const li = document.createElement("li");
        li.className = "chip";
        li.textContent = tag;
        tagList.append(li);
      }
      form.reset();
      onCreated?.(product);
    } catch (err) {
      setFeedback(err.message, "error");
    } finally {
      button.disabled = false;
      button.removeAttribute("aria-busy");
    }
  });
}

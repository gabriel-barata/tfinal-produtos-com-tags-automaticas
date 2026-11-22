// Inicializa os componentes e conecta um ao outro por callbacks.
import { deleteProduct, listProducts } from "./api.js";
import { mount as mountAdminPanel } from "./components/admin-panel.js";
import { mount as mountProductForm } from "./components/product-form.js";
import { mount as mountProductList } from "./components/product-list.js";
import { mount as mountSearchBar } from "./components/search-bar.js";
import { mount as mountServerStatus } from "./components/server-status.js";
import { mount as mountTagFilters } from "./components/tag-filters.js";

const $ = (id) => document.getElementById(id);

let adminPanel;
let tagFilters;
let searchBar;

// Com debounce, uma resposta antiga pode chegar depois de uma nova; só a última vale.
let lastRequest = 0;

const productList = mountProductList($("product-list"), { onDelete: handleDelete });

async function reloadList() {
  const request = ++lastRequest;
  try {
    const results = await listProducts(searchBar.getQuery());
    if (request === lastRequest) {
      productList.render(results, { canDelete: Boolean(adminPanel.getKey()) });
    }
  } catch (err) {
    if (request === lastRequest) productList.renderError(err.message);
  }
}

async function handleDelete(product) {
  if (!confirm(`Excluir "${product.name}"?`)) return;
  try {
    await deleteProduct(product.id, adminPanel.getKey());
  } catch (err) {
    if (err.status === 401) {
      // Chave errada: apaga para os botões sumirem e o usuário digitar de novo.
      adminPanel.clearKey();
      alert("Chave de administrador inválida. A chave salva foi removida.");
      return;
    }
    alert(err.message);
    if (err.status !== 404) return; // 404: já não existe; segue para recarregar
  }
  reloadAll();
}

function onSearch() {
  tagFilters.setActive(searchBar.getTerms());
  reloadList();
}

function reloadAll() {
  reloadList();
  tagFilters.load();
}

mountServerStatus($("server-status"));
searchBar = mountSearchBar($("search-bar"), { onSearch });
tagFilters = mountTagFilters($("tag-filters"), {
  onToggle: (tag) => (searchBar.getTerms().includes(tag) ? searchBar.removeTerm(tag) : searchBar.addTerm(tag)),
});
adminPanel = mountAdminPanel($("admin-panel"), { onKeyChange: reloadList });
mountProductForm($("product-form"), { onCreated: reloadAll });
reloadAll();

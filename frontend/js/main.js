// Inicializa os componentes e conecta um ao outro por callbacks.
import { listProducts } from "./api.js";
import { mount as mountProductForm } from "./components/product-form.js";
import { mount as mountProductList } from "./components/product-list.js";
import { mount as mountSearchBar } from "./components/search-bar.js";
import { mount as mountServerStatus } from "./components/server-status.js";
import { mount as mountTagFilters } from "./components/tag-filters.js";

const $ = (id) => document.getElementById(id);

const productList = mountProductList($("product-list"));
let tagFilters;
let searchBar;

// Com debounce, uma resposta antiga pode chegar depois de uma nova; só a última vale.
let lastRequest = 0;

async function reloadList() {
  const request = ++lastRequest;
  try {
    const results = await listProducts(searchBar.getQuery());
    if (request === lastRequest) productList.render(results);
  } catch (err) {
    if (request === lastRequest) productList.renderError(err.message);
  }
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
mountProductForm($("product-form"), { onCreated: reloadAll });
reloadAll();

// Inicializa os componentes e conecta um ao outro por callbacks.
import { listProducts } from "./api.js";
import { mount as mountProductForm } from "./components/product-form.js";
import { mount as mountProductList } from "./components/product-list.js";
import { mount as mountServerStatus } from "./components/server-status.js";

const $ = (id) => document.getElementById(id);

const productList = mountProductList($("product-list"));

async function reloadList() {
  try {
    productList.render(await listProducts());
  } catch (err) {
    productList.renderError(err.message);
  }
}

mountServerStatus($("server-status"));
mountProductForm($("product-form"), { onCreated: reloadList });
reloadList();

// Inicializa os componentes e conecta um ao outro por callbacks.
import { mount as mountServerStatus } from "./components/server-status.js";

mountServerStatus(document.getElementById("server-status"));

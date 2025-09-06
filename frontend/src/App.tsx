import Productos from "./components/Productos";
import "./App.css";

function App() {
  return (
    <div className="app-card">
      <h1 className="title">
        EcoSmart{" "}
        <span role="img" aria-label="carrito de compra">
          🛒
        </span>
      </h1>
      <Productos />
    </div>
  );
}

export default App;

// App.tsx

import Productos from "./components/Productos";
import "./App.css";

function App() {
  return (
    <div className="app-card">
      <h1>
        <span role="img" aria-label="hoja de planta">🌱</span> EcoSmartCR
      </h1>
      <Productos />
    </div>
  );
}

export default App;
import { useState } from 'react'
import './App.css'
import Dashboard from './pages/Dashboard'
import Cardapio from './pages/Cardapio'
import Historico from './pages/Historico'

const ABAS = [
  { id: 'dashboard', label: '📊 Dashboard' },
  { id: 'cardapio',  label: '🍛 Cardápio' },
  { id: 'historico', label: '📈 Histórico' },
]

export default function App() {
  const [aba, setAba] = useState('dashboard')

  return (
    <div className="app">
      <header className="header">
        <div className="header-top">
          <span className="brasao">🎖️</span>
          <div>
            <h1>SISTEMA DE MARMITAS</h1>
            <p className="subtitulo">Operação: Alimentação Inteligente</p>
          </div>
        </div>
        <nav className="nav">
          {ABAS.map(a => (
            <button
              key={a.id}
              className={`nav-btn ${aba === a.id ? 'active' : ''}`}
              onClick={() => setAba(a.id)}
            >
              {a.label}
            </button>
          ))}
        </nav>
      </header>

      <main className="main">
        {aba === 'dashboard' && <Dashboard />}
        {aba === 'cardapio'  && <Cardapio />}
        {aba === 'historico' && <Historico />}
      </main>

      <footer className="footer">
        <span>🎖️ Minimizar desperdício. Maximizar eficiência. Garantir que ninguém fique sem comida.</span>
      </footer>
    </div>
  )
}

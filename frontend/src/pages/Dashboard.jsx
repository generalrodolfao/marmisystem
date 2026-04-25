import { useState, useEffect } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import { useApi, postPipeline, postData } from '../hooks/useApi'

function EfBadge({ v }) {
  const cls = v >= 90 ? 'ef-alta' : v >= 70 ? 'ef-media' : 'ef-baixa'
  return <span className={cls}>{v}%</span>
}

function PlanningPanel({ onSave }) {
  const { data: pratos } = useApi('/api/pratos')
  const [data, setData] = useState(new Date(Date.now() + 86400000).toISOString().split('T')[0])
  const [pratoId, setPratoId] = useState('')
  const [qtd, setQtd] = useState(0)
  const [sugestao, setSugestao] = useState(null)
  const [salvando, setSalvando] = useState(false)

  // Busca sugestão estatística
  useEffect(() => {
    if (data && pratoId) {
      fetch(`http://localhost:8000/api/planejamento/sugestao?data=${data}&prato_id=${pratoId}`)
        .then(r => r.json())
        .then(res => {
           setSugestao(res.sugestao)
           if (qtd === 0) setQtd(res.sugestao)
        })
    }
  }, [data, pratoId])

  async function salvar() {
    if (!pratoId || !qtd) return alert('Selecione um prato e quantidade')
    setSalvando(true)
    try {
      await postData('/api/planejamento', { data, prato_id: parseInt(pratoId), quantidade: parseInt(qtd) })
      alert('Planejamento registrado!')
      onSave()
    } catch (e) {
      alert('Erro ao salvar')
    } finally {
      setSalvando(false)
    }
  }

  return (
    <div className="card" style={{ marginBottom: 24 }}>
      <div className="form-row">
        <div style={{ flex: 1 }}>
          <label className="label-militar">Data da Operação</label>
          <input type="date" className="input-militar" value={data} onChange={e => setData(e.target.value)} />
        </div>
        <div style={{ flex: 2 }}>
          <label className="label-militar">Selecionar Prato</label>
          <select className="input-militar" value={pratoId} onChange={e => {
            setPratoId(e.target.value)
            setQtd(0) // Reseta para carregar sugestão
          }}>
            <option value="">Selecione...</option>
            {pratos?.map(p => <option key={p.id} value={p.id}>{p.nome}</option>)}
          </select>
        </div>
        <div style={{ flex: 1 }}>
          <label className="label-militar">
            Previsão {sugestao && <span style={{color: 'var(--amarelo)', fontSize: '0.6rem'}}>(Estatística: {sugestao})</span>}
          </label>
          <input type="number" className="input-militar" value={qtd} onChange={e => setQtd(e.target.value)} />
        </div>
        <button className="btn-militar" onClick={salvar} disabled={salvando}>
          {salvando ? '...' : 'REGISTRAR'}
        </button>
      </div>
    </div>
  )
}

export default function Dashboard() {
  const { data, loading, error, reload } = useApi('/api/dashboard')
  const [rodando, setRodando] = useState(false)

  async function executarPipeline() {
    if (rodando) return
    setRodando(true)
    try {
      await postPipeline()
      reload()
    } finally {
      setRodando(false)
    }
  }

  if (loading) return <div className="loading">CARREGANDO DADOS...</div>
  // ... resta do código ...
  if (error) return <div className="loading" style={{color:'#ff9999'}}>ERRO: API offline. Inicie o backend com: uvicorn services.api:app</div>

  const { producao_ontem: prod, previsao_hoje, alertas, destaque, eficiencia_pct } = data

  const graficoData = prod.pratos.map(p => ({
    name: p.nome.split(' ').slice(0, 2).join(' '),
    produzido: p.quantidade_produzida,
    consumido: p.quantidade_consumida,
    sobra: p.sobra,
  }))

  return (
    <div>
      {/* KPIs */}
      <div className="grid-4" style={{ marginBottom: 24 }}>
        <div className="card">
          <div className="card-title">Produzido ontem</div>
          <div className="card-value">{prod.total_produzido}</div>
          <div className="card-sub">marmitas</div>
        </div>
        <div className="card">
          <div className="card-title">Consumido</div>
          <div className="card-value">{prod.total_consumido}</div>
          <div className="card-sub">marmitas</div>
        </div>
        <div className="card">
          <div className="card-title">Sobra</div>
          <div className="card-value" style={{ color: prod.total_sobra > 30 ? '#ff9999' : '#90ee90' }}>
            {prod.total_sobra}
          </div>
          <div className="card-sub">marmitas desperdiçadas</div>
        </div>
        <div className="card">
          <div className="card-title">Eficiência</div>
          <div className="card-value"><EfBadge v={prod.eficiencia_pct} /></div>
          <div className="card-sub">consumo/produção</div>
        </div>
      </div>

      {/* Alertas */}
      <div className="secao-titulo">⚠ Alertas e Destaques</div>
      {alertas && alertas.length > 0
        ? alertas.map((a, i) => <div key={i} className="alerta">{a}</div>)
        : <div className="alerta alerta-ok">✓ Sem alertas. Operação normal.</div>
      }
      {destaque && (
        <div style={{ background: 'rgba(75,83,32,0.3)', border: '1px solid var(--verde-oliva)', borderRadius: 4, padding: '10px 16px', marginTop: 8, fontSize: '0.85rem' }}>
          🎖️ {destaque}
        </div>
      )}

      {/* Planejamento Manual */}
      <div className="secao-titulo">📝 Planejamento de Operação</div>
      <PlanningPanel onSave={reload} />

      {/* Gráfico produção vs consumo */}
      <div className="secao-titulo">📊 Produção vs Consumo (ontem)</div>
      <div className="card" style={{ marginBottom: 24 }}>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={graficoData} margin={{ top: 5, right: 10, left: 0, bottom: 40 }}>
            <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#aaa' }} angle={-30} textAnchor="end" />
            <YAxis tick={{ fontSize: 10, fill: '#aaa' }} />
            <Tooltip
              contentStyle={{ background: '#2d352d', border: '1px solid #4B5320', fontSize: 12 }}
              labelStyle={{ color: '#FFDF00' }}
            />
            <Bar dataKey="produzido" name="Produzido" fill="#4B5320" />
            <Bar dataKey="consumido" name="Consumido" fill="#FFDF00" />
            <Bar dataKey="sobra" name="Sobra" fill="#ff6b6b" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Previsão hoje */}
      <div className="secao-titulo">🎯 Previsão para Hoje</div>
      {previsao_hoje && previsao_hoje.length > 0 ? (
        <div className="card" style={{ marginBottom: 24 }}>
          <table className="tabela">
            <thead>
              <tr>
                <th>Prato</th>
                <th>Qtd Prevista</th>
              </tr>
            </thead>
            <tbody>
              {previsao_hoje.map((p, i) => (
                <tr key={i}>
                  <td>{p.nome}</td>
                  <td><strong>{p.quantidade_prevista}</strong> marmitas</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="card" style={{ marginBottom: 24, color: '#888', fontSize: '0.85rem' }}>
          Sem previsão para hoje. Execute o pipeline para gerar.
        </div>
      )}

      {/* Botão pipeline */}
      <div className="secao-titulo">⚙ Pipeline</div>
      <button className="btn-pipeline" onClick={executarPipeline} disabled={rodando}>
        {rodando ? '⏳ EXECUTANDO PIPELINE...' : '▶ EXECUTAR PIPELINE DIÁRIO'}
      </button>
      <p style={{ fontSize: '0.75rem', color: '#666', marginTop: 8 }}>
        Executa todos os 5 agentes em sequência e atualiza previsões.
      </p>
    </div>
  )
}

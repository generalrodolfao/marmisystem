import { useState } from 'react'
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer,
  AreaChart, Area, CartesianGrid, Legend
} from 'recharts'
import { useApi } from '../hooks/useApi'

function EfCor(v) {
  return v >= 90 ? 'ef-alta' : v >= 70 ? 'ef-media' : 'ef-baixa'
}

export default function Historico() {
  const [periodo, setPeriodo] = useState(30)
  const { data, loading, error } = useApi(`/api/historico?dias=${periodo}`, [periodo])

  if (loading) return <div className="loading">CARREGANDO HISTÓRICO...</div>
  if (error) return <div className="loading" style={{ color: '#ff9999' }}>API offline.</div>

  const hist = (data?.historico || []).slice().reverse()

  const grafico = hist.map(d => ({
    data: d.data.slice(5),
    produzido: d.total_produzido,
    consumido: d.total_consumido,
    sobra: d.total_sobra,
    eficiencia: d.eficiencia_pct,
  }))

  const mediaEf = grafico.length
    ? Math.round(grafico.reduce((s, d) => s + d.eficiencia, 0) / grafico.length)
    : 0

  const totalProduzido = hist.reduce((s, d) => s + d.total_produzido, 0)
  const totalSobra = hist.reduce((s, d) => s + d.total_sobra, 0)

  return (
    <div>
      {/* Filtro período */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 20 }}>
        {[7, 14, 30, 60].map(d => (
          <button
            key={d}
            onClick={() => setPeriodo(d)}
            style={{
              padding: '6px 16px',
              borderRadius: 4,
              background: periodo === d ? 'var(--amarelo)' : 'var(--cinza-medio)',
              color: periodo === d ? 'var(--cinza-escuro)' : 'var(--texto)',
              border: '1px solid var(--verde-oliva)',
              fontFamily: 'inherit',
              fontSize: '0.8rem',
              fontWeight: periodo === d ? 'bold' : 'normal',
            }}
          >
            {d}d
          </button>
        ))}
        <span style={{ fontSize: '0.75rem', color: '#666', alignSelf: 'center', marginLeft: 8 }}>
          {data?.total_dias || 0} dias carregados
        </span>
      </div>

      {/* KPIs resumo */}
      <div className="grid-3" style={{ marginBottom: 24 }}>
        <div className="card">
          <div className="card-title">Total produzido</div>
          <div className="card-value">{totalProduzido.toLocaleString('pt-BR')}</div>
          <div className="card-sub">marmitas em {periodo} dias</div>
        </div>
        <div className="card">
          <div className="card-title">Total desperdiçado</div>
          <div className="card-value" style={{ color: totalSobra > totalProduzido * 0.15 ? '#ff9999' : '#90ee90' }}>
            {totalSobra.toLocaleString('pt-BR')}
          </div>
          <div className="card-sub">{totalProduzido ? Math.round(totalSobra / totalProduzido * 100) : 0}% do total</div>
        </div>
        <div className="card">
          <div className="card-title">Eficiência média</div>
          <div className={`card-value ${EfCor(mediaEf)}`}>{mediaEf}%</div>
          <div className="card-sub">consumo/produção</div>
        </div>
      </div>

      {/* Gráfico área — evolução */}
      <div className="secao-titulo">📈 Evolução de Produção e Consumo</div>
      <div className="card" style={{ marginBottom: 24 }}>
        <ResponsiveContainer width="100%" height={240}>
          <AreaChart data={grafico} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
            <defs>
              <linearGradient id="gProd" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#4B5320" stopOpacity={0.6} />
                <stop offset="95%" stopColor="#4B5320" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="gCons" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#FFDF00" stopOpacity={0.6} />
                <stop offset="95%" stopColor="#FFDF00" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(75,83,32,0.3)" />
            <XAxis dataKey="data" tick={{ fontSize: 10, fill: '#888' }} />
            <YAxis tick={{ fontSize: 10, fill: '#888' }} />
            <Tooltip contentStyle={{ background: '#2d352d', border: '1px solid #4B5320', fontSize: 12 }} labelStyle={{ color: '#FFDF00' }} />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            <Area type="monotone" dataKey="produzido" name="Produzido" stroke="#4B5320" fill="url(#gProd)" />
            <Area type="monotone" dataKey="consumido" name="Consumido" stroke="#FFDF00" fill="url(#gCons)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Gráfico eficiência */}
      <div className="secao-titulo">⚡ Eficiência Diária (%)</div>
      <div className="card" style={{ marginBottom: 24 }}>
        <ResponsiveContainer width="100%" height={160}>
          <LineChart data={grafico} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(75,83,32,0.3)" />
            <XAxis dataKey="data" tick={{ fontSize: 10, fill: '#888' }} />
            <YAxis domain={[50, 105]} tick={{ fontSize: 10, fill: '#888' }} />
            <Tooltip contentStyle={{ background: '#2d352d', border: '1px solid #4B5320', fontSize: 12 }} labelStyle={{ color: '#FFDF00' }} />
            <Line type="monotone" dataKey="eficiencia" name="Eficiência %" stroke="#FFDF00" dot={false} strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Tabela */}
      <div className="secao-titulo">📋 Registro Diário</div>
      <div className="card" style={{ overflowX: 'auto' }}>
        <table className="tabela">
          <thead>
            <tr>
              <th>Data</th>
              <th>Produzido</th>
              <th>Consumido</th>
              <th>Sobra</th>
              <th>Eficiência</th>
              <th>Pratos</th>
            </tr>
          </thead>
          <tbody>
            {(data?.historico || []).slice(0, 20).map((d, i) => (
              <tr key={i}>
                <td>{d.data}</td>
                <td>{d.total_produzido}</td>
                <td>{d.total_consumido}</td>
                <td style={{ color: d.total_sobra > 20 ? '#ff9999' : '#90ee90' }}>{d.total_sobra}</td>
                <td><span className={EfCor(d.eficiencia_pct)}>{d.eficiencia_pct}%</span></td>
                <td style={{ fontSize: '0.75rem', color: '#888' }}>{d.pratos.slice(0, 3).join(', ')}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

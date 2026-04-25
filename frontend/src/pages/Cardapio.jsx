import { useApi } from '../hooks/useApi'

const CAT_COR = {
  tradicional: '#4B5320',
  massa: '#5a4a8a',
  peixe: '#1a5f7a',
  sopa: '#7a4a1a',
  vegetariano: '#2a7a2a',
}

const DIAS_PT = {
  '2026-04-26': 'Domingo', '2026-04-27': 'Segunda',
}

function formatDia(isoDate) {
  const d = new Date(isoDate + 'T12:00:00')
  const dias = ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado']
  const meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
  return `${dias[d.getDay()]}, ${d.getDate()} ${meses[d.getMonth()]}`
}

function PopBar({ v }) {
  const pct = Math.round(v * 100)
  const cor = pct >= 85 ? '#FFDF00' : pct >= 65 ? '#90ee90' : '#888'
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 4 }}>
      <div style={{ flex: 1, height: 4, background: '#1a1f1a', borderRadius: 2 }}>
        <div style={{ width: `${pct}%`, height: '100%', background: cor, borderRadius: 2 }} />
      </div>
      <span style={{ fontSize: '0.7rem', color: cor, minWidth: 30 }}>{pct}%</span>
    </div>
  )
}

export default function Cardapio() {
  const { data, loading, error } = useApi('/api/cardapio')

  if (loading) return <div className="loading">CARREGANDO CARDÁPIO...</div>
  if (error) return <div className="loading" style={{ color: '#ff9999' }}>API offline.</div>

  const dias = data?.dias || []

  return (
    <div>
      <div className="secao-titulo">🍽 Próximos 3 Dias</div>

      {dias.length === 0 ? (
        <div className="card" style={{ color: '#888', fontSize: '0.85rem' }}>
          Cardápio ainda não gerado. Execute o pipeline no Dashboard.
        </div>
      ) : (
        <div className="grid-3">
          {dias.map((dia, i) => (
            <div key={i} className="card">
              <div style={{ marginBottom: 16 }}>
                <div className="card-title">{formatDia(dia.data)}</div>
                <div style={{ fontSize: '0.75rem', color: '#666' }}>{dia.data}</div>
              </div>

              {dia.pratos.map((p, j) => (
                <div key={j} style={{
                  background: 'rgba(0,0,0,0.2)',
                  border: '1px solid rgba(75,83,32,0.4)',
                  borderRadius: 4,
                  padding: '10px 12px',
                  marginBottom: 8,
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <span style={{ fontSize: '0.9rem', fontWeight: 'bold' }}>{p.nome}</span>
                    <span className="badge">{p.categoria}</span>
                  </div>
                  <PopBar v={p.popularidade} />
                  <div style={{ fontSize: '0.7rem', color: '#666', marginTop: 4 }}>
                    popularidade
                  </div>
                </div>
              ))}
            </div>
          ))}
        </div>
      )}

      <div className="secao-titulo" style={{ marginTop: 32 }}>📋 Regras do Cardápio</div>
      <div className="grid-3">
        {[
          ['🔁', 'Sem repetição', 'Nenhum prato se repete em menos de 3 dias'],
          ['⚖️', 'Equilíbrio', 'Variedade de categorias por dia garantida'],
          ['📊', 'Popularidade', 'Pratos com maior aceitação têm prioridade'],
        ].map(([icon, titulo, desc], i) => (
          <div key={i} className="card">
            <div style={{ fontSize: '1.5rem', marginBottom: 8 }}>{icon}</div>
            <div className="card-title">{titulo}</div>
            <div style={{ fontSize: '0.8rem', color: '#888' }}>{desc}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

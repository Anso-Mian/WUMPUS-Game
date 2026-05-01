import { useState } from 'react'
import Controls from './components/Controls'
import Grid from './components/Grid'
import Metrics from './components/Metrics'

const API = 'https://wumpus-backend.onrender.com' 

export default function App() {
  const [rows, setRows] = useState(4)
  const [cols, setCols] = useState(4)
  const [gameStarted, setGameStarted] = useState(false)
  const [gameId, setGameId] = useState(null)
  const [agentPos, setAgentPos] = useState({ row: 0, col: 0 })
  const [goldPos, setGoldPos] = useState(null)
  const [percepts, setPercepts] = useState([])
  const [safeCells, setSafeCells] = useState(new Set(['0,0']))
  const [visitedCells, setVisitedCells] = useState(new Set(['0,0']))
  const [pitCells, setPitCells] = useState(new Set())
  const [wumpusCells, setWumpusCells] = useState(new Set())
  const [inferenceSteps, setInferenceSteps] = useState(0)
  const [kbSize, setKbSize] = useState(0)
  const [totalMoves, setTotalMoves] = useState(0)
  const [gameOver, setGameOver] = useState(false)
  const [won, setWon] = useState(false)
  const [deathReason, setDeathReason] = useState(null)
  const [revealed, setRevealed] = useState(false)
  const [loading, setLoading] = useState(false)

  const updateState = (data) => {
    setAgentPos(data.agent_pos)
    setPercepts(data.percepts)
    setSafeCells(new Set(data.safe_cells))
    setVisitedCells(new Set(data.visited_cells))
    setPitCells(new Set(data.pit_cells))
    setWumpusCells(new Set(data.wumpus_cells))
    setInferenceSteps(data.inference_steps)
    setKbSize(data.kb_size)
    setTotalMoves(data.total_moves)
    setGameOver(data.game_over)
    setWon(data.won || false)
    setDeathReason(data.death_reason || null)
    setRevealed(data.revealed || false)
  }

  const startGame = async () => {
    setLoading(true)
    try {
      const res = await fetch(`${API}/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ rows, cols }),
      })
      const data = await res.json()
      setGameId(data.game_id)
      setGoldPos(data.gold_pos)
      updateState(data)
      setGameStarted(true)
    } catch (err) {
      console.error('Failed to start game:', err)
    }
    setLoading(false)
  }

  const moveAgent = async (direction) => {
    if (!gameId || gameOver || loading) return
    setLoading(true)
    try {
      const res = await fetch(`${API}/move`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ game_id: gameId, direction }),
      })
      const data = await res.json()
      if (!data.error) updateState(data)
    } catch (err) {
      console.error('Failed to move:', err)
    }
    setLoading(false)
  }

  const autoStep = async () => {
    if (!gameId || gameOver || loading) return
    setLoading(true)
    try {
      const res = await fetch(`${API}/auto-step`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ game_id: gameId }),
      })
      const data = await res.json()
      if (!data.error) updateState(data)
    } catch (err) {
      console.error('Failed to auto step:', err)
    }
    setLoading(false)
  }

  const resetGame = () => {
    setGameStarted(false)
    setGameId(null)
    setGameOver(false)
    setWon(false)
    setDeathReason(null)
    setRevealed(false)
    startGame()
  }

  const gameState = gameOver
    ? won
      ? { type: 'win', message: 'Agent found the gold and won!' }
      : { type: 'death', message: `Agent died! Killed by ${deathReason}.` }
    : null

  return (
    <main className="main">
      <h1 className="title">Wumpus World Logic Agent</h1>
      <p className="subtitle">Knowledge-Based Agent with Propositional Logic & Resolution Refutation</p>

      <div className="app-container">
        <div className="left-panel">
          <Controls
            rows={rows}
            cols={cols}
            onRowsChange={setRows}
            onColsChange={setCols}
            onStartGame={startGame}
            onMoveAgent={moveAgent}
            onAutoStep={autoStep}
            onReset={resetGame}
            gameStarted={gameStarted}
            gameOver={gameOver}
            loading={loading}
          />

          {gameStarted && (
            <Metrics
              percepts={percepts}
              inferenceSteps={inferenceSteps}
              kbSize={kbSize}
              totalMoves={totalMoves}
              safeCount={safeCells.size}
              dangerCount={pitCells.size + wumpusCells.size}
              gameState={gameState}
            />
          )}
        </div>

        <div className="right-panel">
          {gameStarted ? (
            <Grid
              gridRows={rows}
              gridCols={cols}
              agentPos={agentPos}
              goldPos={goldPos}
              safeCells={safeCells}
              visitedCells={visitedCells}
              pitCells={pitCells}
              wumpusCells={wumpusCells}
              revealed={revealed}
            />
          ) : (
            <div className="placeholder">
              Configure grid dimensions and click &quot;Start New Game&quot; to begin.
            </div>
          )}
        </div>
      </div>

      <div className="legend">
        <h3>Legend</h3>
        <div className="legend-items">
          <div className="legend-item"><span className="legend-color agent"></span> Agent</div>
          <div className="legend-item"><span className="legend-color safe"></span> Inferred Safe</div>
          <div className="legend-item"><span className="legend-color visited"></span> Visited</div>
          <div className="legend-item"><span className="legend-color unknown"></span> Unknown</div>
          <div className="legend-item"><span className="legend-color pit"></span> Pit (revealed)</div>
          <div className="legend-item"><span className="legend-color wumpus"></span> Wumpus (revealed)</div>
        </div>
      </div>
    </main>
  )
}

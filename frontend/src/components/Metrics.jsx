import React from 'react'

export default function Metrics({
  percepts,
  inferenceSteps,
  kbSize,
  totalMoves,
  safeCount,
  dangerCount,
  gameState,
}) {
  return (
    <div className="metrics-panel">
      <h3>Inference Metrics</h3>
      <div className="metrics-grid">
        <div className="metric-card">
          <span className="metric-label">Current Percepts</span>
          <span className="metric-value">
            {percepts.length > 0 ? percepts.join(', ') : 'None'}
          </span>
        </div>
        <div className="metric-card">
          <span className="metric-label">Inference Steps</span>
          <span className="metric-value">{inferenceSteps}</span>
        </div>
        <div className="metric-card">
          <span className="metric-label">KB Clauses</span>
          <span className="metric-value">{kbSize}</span>
        </div>
        <div className="metric-card">
          <span className="metric-label">Total Moves</span>
          <span className="metric-value">{totalMoves}</span>
        </div>
        <div className="metric-card">
          <span className="metric-label">Safe Cells Found</span>
          <span className="metric-value">{safeCount}</span>
        </div>
        <div className="metric-card">
          <span className="metric-label">Dangers Identified</span>
          <span className="metric-value">{dangerCount}</span>
        </div>
      </div>
      {gameState && (
        <div className={`game-status ${gameState.type}`}>
          {gameState.message}
        </div>
      )}
    </div>
  )
}

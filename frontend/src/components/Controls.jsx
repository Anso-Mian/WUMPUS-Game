import React from 'react'

export default function Controls({
  rows,
  cols,
  onRowsChange,
  onColsChange,
  onStartGame,
  onMoveAgent,
  onAutoStep,
  onReset,
  gameStarted,
  gameOver,
  loading,
}) {
  return (
    <div className="controls-panel">
      <h3>Game Controls</h3>

      {!gameStarted ? (
        <div className="setup-controls">
          <div className="input-group">
            <label>Rows:</label>
            <input
              type="number"
              min="3"
              max="10"
              value={rows}
              onChange={(e) => onRowsChange(parseInt(e.target.value))}
            />
          </div>
          <div className="input-group">
            <label>Columns:</label>
            <input
              type="number"
              min="3"
              max="10"
              value={cols}
              onChange={(e) => onColsChange(parseInt(e.target.value))}
            />
          </div>
          <button className="btn-primary" onClick={onStartGame} disabled={loading}>
            {loading ? 'Starting...' : 'Start New Game'}
          </button>
        </div>
      ) : (
        <div className="game-controls">
          <div className="move-buttons">
            <button className="btn-move" onClick={() => onMoveAgent('up')} disabled={gameOver || loading}>
              Move Up
            </button>
            <div className="move-row">
              <button className="btn-move" onClick={() => onMoveAgent('left')} disabled={gameOver || loading}>
                Move Left
              </button>
              <button className="btn-move" onClick={() => onMoveAgent('right')} disabled={gameOver || loading}>
                Move Right
              </button>
            </div>
            <button className="btn-move" onClick={() => onMoveAgent('down')} disabled={gameOver || loading}>
              Move Down
            </button>
          </div>

          <div className="auto-controls">
            <button className="btn-auto" onClick={onAutoStep} disabled={gameOver || loading}>
              {loading ? 'Processing...' : 'Auto Step'}
            </button>
          </div>

          <button className="btn-reset" onClick={onReset} disabled={loading}>
            New Game
          </button>
        </div>
      )}
    </div>
  )
}

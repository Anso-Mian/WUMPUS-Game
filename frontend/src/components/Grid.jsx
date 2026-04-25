import React from 'react'

function GridCell({ row, col, cellState }) {
  let cellClass = 'grid-cell unknown'

  if (cellState === 'agent') cellClass = 'grid-cell agent'
  else if (cellState === 'safe') cellClass = 'grid-cell safe'
  else if (cellState === 'visited') cellClass = 'grid-cell visited'
  else if (cellState === 'pit') cellClass = 'grid-cell pit'
  else if (cellState === 'wumpus') cellClass = 'grid-cell wumpus'

  return (
    <div className={cellClass}>
      <span className="cell-coord">{row},{col}</span>
      {cellState === 'agent' && <span className="cell-icon">A</span>}
      {cellState === 'pit' && <span className="cell-icon">P</span>}
      {cellState === 'wumpus' && <span className="cell-icon">W</span>}
    </div>
  )
}

export default function Grid({
  gridRows,
  gridCols,
  agentPos,
  goldPos,
  safeCells,
  visitedCells,
  pitCells,
  wumpusCells,
  revealed,
}) {
  const getCellState = (r, c) => {
    const key = `${r},${c}`
    if (agentPos?.row === r && agentPos?.col === c) return 'agent'
    if (pitCells.has(key) && revealed) return 'pit'
    if (wumpusCells.has(key) && revealed) return 'wumpus'
    if (visitedCells.has(key)) return 'visited'
    if (safeCells.has(key)) return 'safe'
    return 'unknown'
  }

  return (
    <div className="grid-container">
      <div className="grid" style={{ '--cols': gridCols }}>
        {Array.from({ length: gridRows }, (_, r) =>
          Array.from({ length: gridCols }, (_, c) => (
            <GridCell
              key={`${r}-${c}`}
              row={r}
              col={c}
              cellState={getCellState(r, c)}
            />
          ))
        )}
      </div>
      {goldPos && (
        <div className="gold-marker">Gold at ({goldPos.row}, {goldPos.col})</div>
      )}
    </div>
  )
}

import random
from resolution import ResolutionEngine, Clause


class WumpusWorld:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.grid = []
        self.wumpus_pos = None
        self.pit_positions = []
        self.agent_pos = None
        self.gold_pos = None
        self.game_over = False
        self.won = False
        self.death_reason = None
        self.percepts = []
        self.hazards_placed = False

    def initialize(self):
        self.grid = []
        for r in range(self.rows):
            row = []
            for c in range(self.cols):
                row.append({'hasWumpus': False, 'hasPit': False, 'hasGold': False})
            self.grid.append(row)

        safe_cells = {'0,0'}
        all_cells = [f'{r},{c}' for r in range(self.rows) for c in range(self.cols)]

        available = [cell for cell in all_cells if cell not in safe_cells]
        random.shuffle(available)

        wumpus_idx = random.randint(0, len(available) - 1)
        wr, wc = map(int, available[wumpus_idx].split(','))
        self.wumpus_pos = {'row': wr, 'col': wc}
        self.grid[wr][wc]['hasWumpus'] = True
        safe_cells.add(available[wumpus_idx])

        remaining = [cell for i, cell in enumerate(available) if i != wumpus_idx]
        random.shuffle(remaining)

        num_pits = max(2, int(self.rows * self.cols * 0.15))
        self.pit_positions = []

        for i in range(min(num_pits, len(remaining))):
            pr, pc = map(int, remaining[i].split(','))
            self.grid[pr][pc]['hasPit'] = True
            self.pit_positions.append({'row': pr, 'col': pc})
            safe_cells.add(remaining[i])

        gold_available = [cell for cell in all_cells if cell not in safe_cells]
        if gold_available:
            random.shuffle(gold_available)
            gr, gc = map(int, gold_available[0].split(','))
            self.gold_pos = {'row': gr, 'col': gc}
            self.grid[gr][gc]['hasGold'] = True

        self.agent_pos = {'row': 0, 'col': 0}
        self.game_over = False
        self.won = False
        self.death_reason = None
        self.hazards_placed = True

        return self.get_percepts()

    def get_adjacent_cells(self, row, col):
        adjacent = []
        if row > 0:
            adjacent.append({'row': row - 1, 'col': col})
        if row < self.rows - 1:
            adjacent.append({'row': row + 1, 'col': col})
        if col > 0:
            adjacent.append({'row': row, 'col': col - 1})
        if col < self.cols - 1:
            adjacent.append({'row': row, 'col': col + 1})
        return adjacent

    def get_percepts(self):
        percepts = []
        adjacent = self.get_adjacent_cells(self.agent_pos['row'], self.agent_pos['col'])

        for cell in adjacent:
            if self.grid[cell['row']][cell['col']]['hasWumpus']:
                percepts.append('Stench')
                break

        for cell in adjacent:
            if self.grid[cell['row']][cell['col']]['hasPit']:
                percepts.append('Breeze')
                break

        if self.grid[self.agent_pos['row']][self.agent_pos['col']]['hasGold']:
            percepts.append('Glitter')

        if self.agent_pos['row'] == 0 and self.agent_pos['col'] == 0:
            percepts.append('Bump')

        self.percepts = percepts
        return percepts

    def move_agent(self, direction):
        if self.game_over:
            return {'success': False, 'percepts': []}

        row, col = self.agent_pos['row'], self.agent_pos['col']

        if direction == 'up':
            row -= 1
        elif direction == 'down':
            row += 1
        elif direction == 'left':
            col -= 1
        elif direction == 'right':
            col += 1

        if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
            self.percepts = ['Bump']
            return {'success': False, 'percepts': self.percepts, 'bump': True}

        self.agent_pos = {'row': row, 'col': col}

        if self.grid[row][col]['hasWumpus']:
            self.game_over = True
            self.death_reason = 'Wumpus'
            percepts = self.get_percepts()
            return {'success': False, 'percepts': percepts, 'dead': True, 'deathReason': 'Wumpus'}

        if self.grid[row][col]['hasPit']:
            self.game_over = True
            self.death_reason = 'Pit'
            percepts = self.get_percepts()
            return {'success': False, 'percepts': percepts, 'dead': True, 'deathReason': 'Pit'}

        if self.grid[row][col]['hasGold']:
            self.game_over = True
            self.won = True
            percepts = self.get_percepts()
            return {'success': True, 'percepts': percepts, 'won': True}

        percepts = self.get_percepts()
        return {'success': True, 'percepts': percepts}


class WumpusAgent:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.resolution_engine = ResolutionEngine()
        self.kb = []
        self.visited = set()
        self.safe_cells = set()
        self.pit_cells = set()
        self.wumpus_cells = set()
        self.current_pos = {'row': 0, 'col': 0}
        self.total_steps = 0
        self.total_inference_steps = 0
        self.visited.add('0,0')
        self.safe_cells.add('0,0')

    def reset(self):
        self.kb = []
        self.visited = {'0,0'}
        self.safe_cells = {'0,0'}
        self.pit_cells = set()
        self.wumpus_cells = set()
        self.current_pos = {'row': 0, 'col': 0}
        self.total_steps = 0
        self.total_inference_steps = 0
        self.resolution_engine.reset_steps()

    def get_symbol(self, type_, row, col):
        return f'{type_}_{row}_{col}'

    def get_adjacent_cells(self, row, col):
        adjacent = []
        if row > 0:
            adjacent.append({'row': row - 1, 'col': col})
        if row < self.rows - 1:
            adjacent.append({'row': row + 1, 'col': col})
        if col > 0:
            adjacent.append({'row': row, 'col': col - 1})
        if col < self.cols - 1:
            adjacent.append({'row': row, 'col': col + 1})
        return adjacent

    def tell_kb(self, percepts):
        row, col = self.current_pos['row'], self.current_pos['col']
        clauses = []

        clauses.append(self.get_symbol('At', row, col))

        adjacent = self.get_adjacent_cells(row, col)

        if 'Stench' in percepts:
            wumpus_adjacent = [self.get_symbol('W', a['row'], a['col']) for a in adjacent]
            clauses.append(' v '.join(wumpus_adjacent))

            for a in adjacent:
                others = [x for x in adjacent if x['row'] != a['row'] or x['col'] != a['col']]
                others_w = [self.get_symbol('~W', o['row'], o['col']) for o in others]
                clauses.append(self.get_symbol('~W', a['row'], a['col']) + ' v ' + ' v '.join(others_w))
        else:
            for a in adjacent:
                clauses.append(self.get_symbol('~W', a['row'], a['col']))
                self.safe_cells.add(f"{a['row']},{a['col']}")

        if 'Breeze' in percepts:
            pit_adjacent = [self.get_symbol('P', a['row'], a['col']) for a in adjacent]
            clauses.append(' v '.join(pit_adjacent))

            for a in adjacent:
                others = [x for x in adjacent if x['row'] != a['row'] or x['col'] != a['col']]
                others_p = [self.get_symbol('~P', o['row'], o['col']) for o in others]
                clauses.append(self.get_symbol('~P', a['row'], a['col']) + ' v ' + ' v '.join(others_p))
        else:
            for a in adjacent:
                clauses.append(self.get_symbol('~P', a['row'], a['col']))
                self.safe_cells.add(f"{a['row']},{a['col']}")

        for clause in clauses:
            if clause not in self.kb:
                self.kb.append(clause)

    def run_inference(self):
        self.resolution_engine.reset_steps()
        kb_clauses = [self.resolution_engine.parse_clause(c) for c in self.kb]

        unvisited_neighbors = [
            a for a in self.get_adjacent_cells(self.current_pos['row'], self.current_pos['col'])
            if f"{a['row']},{a['col']}" not in self.visited
        ]

        for cell in unvisited_neighbors:
            key = f"{cell['row']},{cell['col']}"

            pit_proven = self.resolution_engine.resolution_refutation(
                kb_clauses, self.get_symbol('P', cell['row'], cell['col'])
            )
            no_pit_proven = self.resolution_engine.resolution_refutation(
                kb_clauses, self.get_symbol('~P', cell['row'], cell['col'])
            )
            wumpus_proven = self.resolution_engine.resolution_refutation(
                kb_clauses, self.get_symbol('W', cell['row'], cell['col'])
            )
            no_wumpus_proven = self.resolution_engine.resolution_refutation(
                kb_clauses, self.get_symbol('~W', cell['row'], cell['col'])
            )

            if pit_proven:
                self.pit_cells.add(key)
            elif no_pit_proven:
                self.safe_cells.add(key)

            if wumpus_proven:
                self.wumpus_cells.add(key)
            elif no_wumpus_proven:
                self.safe_cells.add(key)

        self.total_inference_steps += self.resolution_engine.inference_steps

    def decide_next_move(self):
        self.run_inference()

        unvisited_neighbors = [
            a for a in self.get_adjacent_cells(self.current_pos['row'], self.current_pos['col'])
            if f"{a['row']},{a['col']}" not in self.visited
            and f"{a['row']},{a['col']}" not in self.pit_cells
            and f"{a['row']},{a['col']}" not in self.wumpus_cells
        ]

        if unvisited_neighbors:
            return unvisited_neighbors[0]

        visited_neighbors = [
            a for a in self.get_adjacent_cells(self.current_pos['row'], self.current_pos['col'])
            if f"{a['row']},{a['col']}" in self.visited
        ]

        if visited_neighbors:
            return visited_neighbors[0]

        return None

    def get_direction(self, target):
        dr = target['row'] - self.current_pos['row']
        dc = target['col'] - self.current_pos['col']

        if dr == -1 and dc == 0:
            return 'up'
        if dr == 1 and dc == 0:
            return 'down'
        if dr == 0 and dc == -1:
            return 'left'
        if dr == 0 and dc == 1:
            return 'right'
        return 'unknown'

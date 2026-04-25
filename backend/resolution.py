class Clause:
    def __init__(self, literals=None):
        self.literals = set(literals or [])

    def add(self, literal):
        self.literals.add(literal)

    def has(self, literal):
        return literal in self.literals

    def has_negation(self, literal):
        negated = literal[1:] if literal.startswith('~') else '~' + literal
        return negated in self.literals

    def remove(self, literal):
        self.literals.discard(literal)

    def is_empty(self):
        return len(self.literals) == 0

    def is_tautology(self):
        for lit in self.literals:
            if self.has_negation(lit):
                return True
        return False

    def copy(self):
        return Clause(list(self.literals))

    def __repr__(self):
        if not self.literals:
            return '[]'
        return '{' + ', '.join(sorted(self.literals)) + '}'


class ResolutionEngine:
    def __init__(self):
        self.inference_steps = 0

    def reset_steps(self):
        self.inference_steps = 0

    @staticmethod
    def negate(literal):
        return literal[1:] if literal.startswith('~') else '~' + literal

    def parse_clause(self, clause_str):
        cleaned = clause_str.replace('(', '').replace(')', '').strip()
        if not cleaned:
            return Clause()
        literals = [l.strip() for l in cleaned.split(' v ') if l.strip()]
        return Clause(literals)

    def resolve(self, clause_a, clause_b):
        self.inference_steps += 1
        resolvents = []

        for lit_a in clause_a.literals:
            neg_a = self.negate(lit_a)
            if clause_b.has(neg_a):
                resolvent = clause_a.copy()
                resolvent.remove(lit_a)
                temp = clause_b.copy()
                temp.remove(neg_a)
                for lit in temp.literals:
                    resolvent.add(lit)
                if not resolvent.is_tautology():
                    resolvents.append(resolvent)

        return resolvents

    def resolution_refutation(self, kb_clauses, query_literal):
        self.reset_steps()

        clauses = []
        clause_strings = set()

        for clause in kb_clauses:
            key = '|'.join(sorted(clause.literals))
            if key not in clause_strings:
                clause_strings.add(key)
                clauses.append(clause)

        negated_query = Clause([self.negate(query_literal)])
        neg_key = '|'.join(sorted(negated_query.literals))
        if neg_key not in clause_strings:
            clause_strings.add(neg_key)
            clauses.append(negated_query)

        new_clauses = []
        max_iterations = 5000
        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            derived_new = False

            for i in range(len(clauses)):
                for j in range(i + 1, len(clauses)):
                    resolvents = self.resolve(clauses[i], clauses[j])

                    for resolvent in resolvents:
                        if resolvent.is_empty():
                            return True

                        key = '|'.join(sorted(resolvent.literals))
                        if key not in clause_strings:
                            clause_strings.add(key)
                            new_clauses.append(resolvent)
                            derived_new = True

            if not derived_new:
                break

            clauses.extend(new_clauses)
            new_clauses.clear()

        return False

    def query_kb(self, kb_clauses, query):
        return self.resolution_refutation(kb_clauses, query)

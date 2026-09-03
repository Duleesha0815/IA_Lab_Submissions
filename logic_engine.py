class KnowledgeBase:
    """
    A simple Knowledge Base (KB) for propositional logic.
    Stores facts (as strings) and rules (Horn Clauses).
    Uses Forward Chaining to deduce new facts.
    """

    def __init__(self):
        self.facts = set()          # Set of strings (e.g., "TargetVisible")
        self.rules = []             # List of tuples: ([premises], conclusion)

    def tell_fact(self, fact_string: str):
        """Add a fact to the KB."""
        self.facts.add(fact_string)

    def tell_rule(self, premise_list: list, conclusion_string: str):
        """Add a rule: IF all premises are true THEN conclusion."""
        self.rules.append((premise_list, conclusion_string))

    def clear_facts(self):
        """Clear all facts (useful when re-evaluating)."""
        self.facts.clear()

    # ========== PRACTICAL 05: Forward Chaining ==========
    def forward_chain(self):
        """
        Perform Forward Chaining:
        Repeatedly apply rules until no new facts are deduced.
        Uses Modus Ponens: IF all premises are in facts, add conclusion.
        """
        new_facts_added = True

        while new_facts_added:
            new_facts_added = False

            for premises, conclusion in self.rules:
                # Skip if conclusion already known
                if conclusion in self.facts:
                    continue

                # Check if all premises are in facts (Modus Ponens)
                if all(premise in self.facts for premise in premises):
                    self.facts.add(conclusion)
                    new_facts_added = True
# logic_engine.py
class KnowledgeBase:
    def __init__(self):
        self.facts = set()
        self.rules = []

    def tell_fact(self, fact_string: str):
        self.facts.add(fact_string)

    def tell_rule(self, premise_list: list, conclusion_string: str):
        self.rules.append((premise_list, conclusion_string))

    def clear_facts(self):
        self.facts.clear()

    def forward_chain(self):
        new_facts_added = True
        while new_facts_added:
            new_facts_added = False
            for premises, conclusion in self.rules:
                if conclusion in self.facts:
                    continue
                if all(premise in self.facts for premise in premises):
                    self.facts.add(conclusion)
                    new_facts_added = True

class Deck:
    def __init__(self, deck_name, language):
        self.deck_name = deck_name
        self.language = language
        self.verb_cards = list()

class Verb:
    def __init__(self, original_verb, infinitive, tenses : dict):
        self.verb_id : int
        self.original = original_verb
        self.infinitive = infinitive
        self.tenses = tenses

    def _on_create(self, db_manager):
        db_manager.insert_verb(self)
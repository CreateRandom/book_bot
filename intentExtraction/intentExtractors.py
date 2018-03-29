from intentExtraction.intents import intentWrapper, entityWrapper


class intentExtractor(object):

    def __init__(self, interpreter):
        super().__init__()
        self.interpreter = interpreter

    def parse_sentence(self, sentence):
        json = self.interpreter.parse(sentence)
        entities = json['entities']
        ranking = json['intent_ranking']
        parsed_entities = self.parse_entities(entities)

        intent = intentWrapper(sentence, json['intent']['name'], parsed_entities, ranking)

        return intent

    def parse_entities(self, entities):
        parsed_entities = []
        for entity in entities:
            entity_type = entity['entity']
            value = entity['value']
            start = entity['start']
            end = entity['end']
            parsed_entities.append(entityWrapper(entity_type, value, start,
                                                 end))
        return parsed_entities

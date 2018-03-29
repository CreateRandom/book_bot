class entityWrapper(object):
    def __init__(self, type, value, start, end):
        super().__init__()
        self.type = type
        self.start = start
        self.end = end
        self.value = value


class intentWrapper(object):
    def __init__(self, message, type, entities, ranking = None):
        super().__init__()
        self.message = message
        self.type = type
        # a list of contained entities
        self.entities = entities
        self.ranking = ranking

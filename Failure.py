class Failure:
    def __init__(self, filename, mutators, mutator_parameters, user_similarity=None, response_similarity=None):
        self.file_name = filename
        self.mutators = mutators
        self.mutator_parameters = mutator_parameters
        self.user_similarity = user_similarity
        self.response_similarity = response_similarity

    def getDescription(self):
        string = 'File {}\n Mutators: \n\t{}\n Parameters: \n\t{}'.format(self.file_name, self.mutators,\
            self.mutator_parameters)
        if self.user_similarity:
            string += '\nSimilarity between seed user interpretation and mutated interpretation: {}\n'.format(self.user_similarity)
        if self.response_similarity:
            string += '\nSimilarity between seed response and mutated response: {}\n'.format(self.response_similarity)
        return string

class Failure:
    def __init__(self, filename, mutators, mutator_parameters, response_similarity=0):
        self.file_name = filename
        self.mutators = mutators
        self.mutator_parameters = mutator_parameters
        self.response_similarity = response_similarity

    def getDescription(self):
        string = 'File {}\n Mutators: \n\t{}\n Parameters: \n\t{}\nSimilarity between\
            mutated response and response to seed: {}\n'.format(self.file_name,\
                self.mutators, self.mutator_parameters, self.response_similarity)
        return string

class Failure:
    def __init__(self, filename, mutators, mutator_parameters):
        self.file_name = filename
        self.mutators = mutators
        self.mutator_parameters = mutator_parameters

    def getDescription(self):
        string = 'File {}\n Mutators: \n\t{}\n Parameters: \n\t{}\n'\
            .format(self.file_name, self.mutators, self.mutator_parameters)
        return string

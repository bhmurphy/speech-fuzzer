from os.path import join
from os import environ
from datetime import datetime
from tensorflow_hub import load
from numpy import inner
from logging import getLogger, ERROR

class FailureAllocator:
    getLogger('tensorflow').setLevel(ERROR)
    environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    semantic_sim = load("https://tfhub.dev/google/universal-sentence-encoder/3")

    def __init__(self, output_file):
        self.failure_list = []
        self.mutator_counts = {}
        self.total_runs = 0
        self.fail_total = 0
        self.output_file = output_file

    def writeFailures(self):
        d = datetime.today()
        with open(join(self.output_file, 'run_log-{}.txt'.format(d)), 'w+') as output:
            #Write the counts
            string = "{} out of {} runs failed\n".format(self.fail_total, self.total_runs)
            for key in self.mutator_counts.keys():
                string += '\tMutator {} was part of {} failures\n'.format(key, self.mutator_counts[key])
            output.write(string)
            #Write the failure list
            for failure in self.failure_list:
                output.write(failure.getDescription())

    def addFailure(self, failure):
        self.failure_list.append(failure)
        self.increseCounts(failure.mutators)

    def increseCounts(self, mutators):
        for m in mutators:
            self.mutator_counts[m] = self.mutator_counts.get(m, 0) + 1
        self.fail_total+=1

    def getSemanticSim(self, initial, mutated):
        if not initial:
            initial = ''
        if not mutated:
            mutated = ''
        embeddings = self.semantic_sim([initial, mutated])['outputs']
        return inner(embeddings, embeddings)[0, 1]

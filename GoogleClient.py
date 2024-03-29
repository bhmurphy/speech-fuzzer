import subprocess
import re
from tensorflow_hub import load
from json import load as json_load
from numpy import inner
from logging import getLogger, ERROR
from os import environ
from inspect import signature

class GoogleClient:
    getLogger('tensorflow').setLevel(ERROR)
    environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

    def __init__(self):
        self.semantic_sim = load("https://tfhub.dev/google/universal-sentence-encoder/3")
        with open('google-config.json') as config:
            file_params = json_load(config)
        try:
            self.is_failure = getattr(self, file_params['failure'])
        except AttributeError:
            raise AttributeError("Google Client Failure Function {} doesn't exist".format(file_params['failure']))

        self.project_id = file_params['project-id']
        self.device_model_id = file_params['device-model-id']
        self.similarity_threshold = file_params.get('similarity-threshold', 0.5)

    def get_responses(self, filename):
        process = subprocess.Popen(['googlesamples-assistant-pushtotalk', 
                '--project-id', self.project_id,
                '--device-model-id', self.device_model_id,
                '-i', filename,
                '-o', 'tmp.wav', '-v'], stderr=subprocess.PIPE)
        output = process.communicate()[1].decode('utf-8')
        #print(output)
        user_matches = re.findall("Transcript of user request: \"(.*?)\"", str(output))
        google_match = re.findall("supplemental_display_text: \"(.*?)\"", str(output))
        user_final_match = None
        if len(user_matches) > 0:
            user_final_match = user_matches[-1]
        #print(user_matches, google_match)
        google_final_match = None
        if len(google_match) > 0:
            google_final_match = google_match[0]
        return user_final_match, google_final_match
    
    def get_similarity(self, initial, mutated):
        if not initial:
            initial = ''
        if not mutated:
            mutated = ''
        embeddings = self.semantic_sim([initial, mutated])['outputs']
        return inner(embeddings, embeddings)[0, 1]

    def user_input_failure(self, initial_user:str , mutated_user:str , initial_client:str , mutated_client:str) -> bool:
        return initial_user != mutated_user or initial_user is None or mutated_user is None
    
    def output_similarity_failure(self, initial_user:str, mutated_user:str, initial_client:str, mutated_client:str) -> bool:
        return self.get_similarity(initial_client, mutated_client) > self.similarity_threshold
import os
import torch
import logging
from transformers import BertForQuestionAnswering, BertTokenizer
import torch.nn.functional as F
import json

# Set up logging
logging.basicConfig(filename='debug.log', level=logging.DEBUG, format='%(asctime)s %(message)s')
from dotenv import load_dotenv
load_dotenv()

class Score:
    def __init__(self):
        self.scores = []
    
    def add_score(self, score: float):
        self.scores.append(score)
    
    def get_average(self) -> float:
        if not self.scores:
            return 0.0
        return sum(self.scores) / len(self.scores)

import os
import torch
import logging
from transformers import BertForQuestionAnswering, BertTokenizer, BertModel
import torch.nn.functional as F

# Set up logging
logging.basicConfig(filename='debug.log', level=logging.DEBUG, format='%(asctime)s %(message)s')

class Score:
    def __init__(self, model_cache_path='bert_large_qa_model.pth'):
        self.model_cache_path = model_cache_path
        self.tokenizer = BertTokenizer.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
        self.model = None
        self._setup()

    def _setup(self):
        """Sets up the BERT model by loading it from the cache or downloading it."""
        if os.path.exists(self.model_cache_path):
            logging.debug("Loading model from cache...")
            self.model = BertForQuestionAnswering.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
            self.model.load_state_dict(torch.load(self.model_cache_path))
        else:
            logging.debug("Model not found in cache. Downloading and saving...")
            self.model = BertForQuestionAnswering.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
            torch.save(self.model.state_dict(), self.model_cache_path)
            logging.debug("Model has been saved to cache.")

    def bert_inference(self, text):
        '''
        Performs BERT inference on a given text and returns the normalized embeddings.
        '''
        tokens = self.tokenizer(text, return_tensors='pt', max_length=512, truncation=True, padding=True)
        with torch.no_grad():
            embeddings = self.model.bert(**tokens).last_hidden_state
        normalized_embeddings = F.normalize(embeddings, p=2, dim=-1)
        return normalized_embeddings

    def context_embedding(self, context, question):
        '''
        Generates combined embeddings for context and question.
        '''
        combined_text = context + " " + question
        return self.bert_inference(combined_text)

    def compute_bert_score(self, reference_text, candidate_text):
        '''
        Computes the BERTScore between the reference and candidate text.
        '''
        # Get normalized embeddings using bert_inference
        reference_embeddings = self.bert_inference(reference_text)
        candidate_embeddings = self.bert_inference(candidate_text)

        # Compute the cosine similarity between each token in reference and candidate
        similarity_matrix = torch.einsum('bld,bmd->blm', candidate_embeddings, reference_embeddings)

        precision = similarity_matrix.max(dim=2)[0].mean()
        recall = similarity_matrix.max(dim=1)[0].mean()

        # Compute F1 score
        f1_score = 2 * (precision * recall) / (precision + recall)

        return {
            "precision": precision.item(),
            "recall": recall.item(),
            "f1_score": f1_score.item()
        }


    def relevance(self, question, answer_text, context):
        '''
        Takes a `question` string, an `answer_text` string (which contains the
        answer), and a `context` string. Computes a relevance score that includes 
        BERTScore and context relevance.
        '''
        # Use context and question as the reference for BERTScore
        reference_text = context + " " + question
        bert_score = self.compute_bert_score(reference_text, answer_text)
        
        # Calculate context-question embeddings using context_embedding
        context_question_embeddings = self.context_embedding(context, question)
        
        # Calculate answer embeddings
        answer_embeddings = self.bert_inference(answer_text)

        # Compute context similarity
        context_similarity = torch.einsum('bld,bmd->blm', context_question_embeddings, answer_embeddings).mean().item()

        # Final relevance score (adjust weights as needed)
        final_relevance_score = 0.5 * bert_score['f1_score'] + 0.5 * context_similarity

        return {
            "bert_score": bert_score,
            "context_similarity": context_similarity,
            "final_relevance_score": final_relevance_score
        }


# Example usage
if __name__ == "__main__":
    
    # test1
    scorer = Score()
    context = "BERT-large is a deep learning model introduced by Google. It has been widely adopted for natural language processing tasks."
    q = "How many parameters does BERT-large have?"
    a = "BERT-large is really big... it has 24-layers and an embedding size of 1,024, for a total of 340M parameters! Altogether it is 1.34GB, so expect it to take a couple minutes to download to your Colab instance."
    relevance = scorer.relevance(q, a, context)


    # test2
    context2 = "Developed a law application with online medical assistance."
    q2 = "How many parameters does BERT-large have?"
    a2 = "BERT-large is really big... it has 24-layers and an embedding size of 1,024, for a total of 340M parameters! Altogether it is 1.34GB, so expect it to take a couple minutes to download to your Colab instance."
    relevance2 =scorer.relevance(q,a,context2)



    print("Relevance BERTScore 1 : \n", relevance)
    print("Relevance BERTScore 2 : \n", relevance2)


    # Relevance BERTScore 1 : 
    #  {'bert_score': {'precision': 0.8856022357940674, 'recall': 0.8860691785812378, 'f1_score': 0.8858356475830078}, 'context_similarity': 0.7327883243560791, 'final_relevance_score': 0.8093119859695435}
    # Relevance BERTScore 2 : 
    #  {'bert_score': {'precision': 0.8581130504608154, 'recall': 0.841706395149231, 'f1_score': 0.8498305678367615}, 'context_similarity': 0.6727304458618164, 'final_relevance_score': 0.7612805068492889}

    


    
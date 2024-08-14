import os
import torch
import logging
from transformers import BertForQuestionAnswering, BertTokenizer
import torch.nn.functional as F
import json

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
        """
        Performs BERT inference on a given text and returns the normalized embeddings.
        """
        tokens = self.tokenizer(text, return_tensors='pt', max_length=512, truncation=True, padding=True)
        with torch.no_grad():
            embeddings = self.model.bert(**tokens).last_hidden_state
        normalized_embeddings = F.normalize(embeddings, p=2, dim=-1)
        logging.debug(f"Generated normalized embeddings for text: {text[:50]}...")  # Log a snippet of the text for reference
        return normalized_embeddings

    def compute_bert_score(self, reference_text, candidate_text):
        """
        Computes the BERTScore between the reference and candidate text.
        """
        reference_embeddings = self.bert_inference(reference_text)
        candidate_embeddings = self.bert_inference(candidate_text)

        similarity_matrix = torch.einsum('bld,bmd->blm', candidate_embeddings, reference_embeddings)

        precision = similarity_matrix.max(dim=2)[0].mean()
        recall = similarity_matrix.max(dim=1)[0].mean()

        f1_score = 2 * (precision * recall) / (precision + recall + 1e-8)  # Added epsilon to prevent division by zero

        logging.debug(f"Computed BERT score: Precision={precision.item()}, Recall={recall.item()}, F1 Score={f1_score.item()}")
        return {
            "precision": precision.item(),
            "recall": recall.item(),
            "f1_score": f1_score.item()
        }

    def relevance(self, question, answer_text, context):
        """
        Takes a `question` string, an `answer_text` string (which contains the
        answer), and a `context` string. Computes a relevance score that includes 
        BERTScore.
        """
        reference_text = context + " " + question
        bert_score = self.compute_bert_score(reference_text, answer_text)

        final_relevance_score = bert_score['f1_score']  # Only use BERTScore's F1 as the relevance score

        logging.debug(f"Final relevance score (BERTScore F1): {final_relevance_score}")

        return {
            "bert_score": bert_score,
            "final_relevance_score": final_relevance_score
        }


# Example usage
if __name__ == "__main__":
    
    scorer = Score()
    
    q =  "That’s interesting, Alex! Have you found any specific design patterns or architectural approaches particularly effective in enhancing compatibility between Java and ML frameworks during data preprocessing? I'm curious how you've adapted your strategies for different project needs."
    a = "Ive found that implementing the **Adapter Pattern** works wonders for bridging Java with ML frameworks. It allows me to wrap existing libraries and seamlessly integrate their APIs, which is especially helpful during data preprocessing. For instance, I often create custom adapters that handle data transformation from Java types to formats compatible with models built in Python. This not only enhances compatibility but also keeps the code organized. As AI continues to evolve, I’m eager to explore more innovative patterns to enhance efficiency in multi-language projects!"


    resume1 = "BERT-large is a deep learning model introduced by Google. It has been widely adopted for natural language processing tasks."
    relevance = scorer.relevance(q, a, resume1)
    logging.info(f"Relevance 1: {relevance}")

    resume2 = {
        "name": "Chong Chen",
        "contact": {
            "phone": "608-213-6312",
            "email": "cchen686@wisc.edu",
            "linkedin": "linkedin.com/in/chong-chen-857214292/",
            "github": "github.com/Sma1lboy"
        },
        "education": [
            {
                "degree": "Bachelor of Science",
                "major": "Computer Sciences",
                "university": "University of Wisconsin-Madison",
                "gpa": "4.00/4.00",
                "location": "Madison, WI",
                "dates": "Aug. 2023 – Dec. 2024"
            },
            {
                "degree": "Bachelor of Science",
                "major": "Computer Engineering",
                "university": "The Ohio State University",
                "gpa": "3.74/4.00",
                "location": "Columbus, OH",
                "dates": "Aug. 2021 – May 2023"
            }
        ],
        "experience": [
            {
                "title": "Software Developer Intern",
                "company": "Shanghai MaiMiao Internet Ltd.",
                "location": "Remote",
                "dates": "May 2024 - Present",
                "responsibilities": [
                    "Designed and developed a scalable, full-stack mobile app with React Native + Expo and Spring Boot + Java microservices, enhancing UX and business operations.",
                    "Implemented efficient RESTful APIs and a flexible message service interface, optimizing system performance by 30% and enabling integration with various backends.",
                    "Set up a CI/CD pipeline automating builds, tests, and deployments, reducing manual efforts by 80% and accelerating releases by 50%, ensuring code quality.",
                    "Conducted code reviews, maintained documentation, and mentored junior developers, promoting best practices and collaboration."
                ]
            },
            {
                "title": "Software Engineer Intern",
                "company": "Virtual Hybrid Inc",
                "location": "Los Angeles, CA",
                "dates": "May 2023 - Aug 2023",
                "responsibilities": [
                    "Developed a scalable distributed-microservice project using C# and ASP.NET, resulting in a 30% improvement in system scalability.",
                    "Implemented location-based recommendations using C# and NTS topology suite, reducing nearby feed retrieval time by 120%.",
                    "Designed and built a News-Feed server with the fan-out pattern, cutting image upload wait time by 95%.",
                    "Enhanced data interchange efficiency with Redis Pub/Sub, reducing server load by 70% and improving user experience by minimizing back-end processing delays for image uploads."
                ]
            }
        ],
        "projects": [
            {
                "name": "RegTool: The Source Registry Manager",
                "technologies": ["Go"],
                "dates": "May 2024 - Present",
                "description": [
                    "Developed an open-source Terminal User Interface (TUI) program in Go for unified management of multiple package registries (npm, Yarn, Homebrew, pip, RubyGems, etc).",
                    "Designed a modular architecture with well-defined interfaces, facilitating easy maintenance and community contributions for additional package managers.",
                    "Implemented centralized registry management and intuitive UI, reducing developer configuration time by up to 90% and streamlining workflows."
                ]
            },
            {
                "name": "MelodyBay",
                "technologies": ["Java", "Spring Boot", "React", "PostgreSQL", "Docker", "Kubernetes"],
                "dates": "Jun 2023 – Jan 2024",
                "description": [
                    "Developed a microservice-based platform for sharing 50,000+ songs, utilizing Java and Spring Boot.",
                    "Implemented CI/CD pipelines, improving development efficiency by 50% and streamlining deployment processes.",
                    "Enhanced user experience and SEO by building a server-side rendering web application with Next.js.",
                    "Improved search response time by 300% through implementing Distributed Elasticsearch, enhancing user satisfaction."
                ]
            }
        ],
        "skills": {
            "languages": ["Java", "C#", "C", "Python", "TypeScript", "HTML/CSS", "Rust"],
            "frameworks_libraries": ["Spring", "Node.js", "MyBatis", "React", "gRPC", "Hibernate", "Axios", "Nginx"],
            "developer_tools": ["Git", "Amazon Web Services", "Google Cloud Platform", "Maven", "Postman", "Docker", "Kubernetes", "Azure DevOps"]
        }
    }


    # resume2 = {
    #     "name": "Pai Eng",
    #     "education": {"degree": "Bachelor of Science", "major": "Computer Science", "university": "University of Barcelona"},
    #     "experience": "Software Engineer with 5 years of experience in AI and ML projects.",
    #     "skills": ["Python", "Machine Learning", "Deep Learning", "Data Science"],
    #     "projects": ["Developed an AI-based recommendation system for e-commerce platforms.", "Led a team in the creation of a machine learning model for predictive analytics in finance."],
    #     "others": ["Certified AI Professional", "Published research papers"]
    # }
    resume2_string = json.dumps(resume2, indent=4)
    relevance2 = scorer.relevance(q, a, resume2_string)
    logging.info(f"Relevance 2: {relevance2}")

    print("Relevance 1:", relevance)
    print("Relevance 2:", relevance2)

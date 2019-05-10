'''
This model extracts the most useful words from the question.
How most useful are defined?

Then it iterates through each sentence and compute the question-sentence relevance
The relevance is computed as the number of times the question-words appear in the sentence
'''
import os
import re
import numpy as np

from flair.data import Sentence
from flair.embeddings import WordEmbeddings

class Model():
    def __init__(self):
        self.name="fasttext weighted_avg"
        
        modelFilePath="flair_fasttext/en-fasttext-news-300d-1M"
        if(os.path.isfile(modelFilePath)):
            print('Loading file..')
            self.model = WordEmbeddings(modelFilePath)
        else:
            print('Creating model..')
            self.setup()
    
    def setup(self):
        self.model = WordEmbeddings('news')

    def questionPreprocessing(self, question):
        '''
        question: the question as a string

        Return:
            question_obj: a Sentence object tokenized containing the question
        '''
        q=question.lower()
        #substitute all the characters that are not letters, numbers, white space, %, or dots with a space
        q=re.sub(r'[^a-zA-Z0-9\s%\-]','',q)
        question_obj=Sentence(q)
        return question_obj
    
    def sentenceProcessing(self, sentence):
        '''
        sentence: a sentence as a string

        Return:
            sentence_obj: a Sentence object tokenized
        '''
        s=sentence.lower()
        s=re.sub(r'[^a-zA-Z0-9\s%\-]','',s)
        sentence_obj=Sentence(s)
        return sentence_obj

    def cosineSimilarity(self, vector1, vector2):
        return np.dot(vector1, vector2)/(np.linalg.norm(vector1)*np.linalg.norm(vector2))

    def computeSimilarity(self, sentence1, sentence2):
        #Convert words to vecs
        self.model.embed(sentence1)
        q_vecs=[]
        for token in sentence1:
            q_vecs.append(token.embedding.data.numpy())

        #average word vectors to create a "sentence" vector
        q_vec=np.mean(q_vecs, axis=0)

        #Convert words to vecs
        self.model.embed(sentence2)
        s_vecs=[]
        for idx, token in enumerate(sentence2):
            w=(len(sentence2)-idx)/len(sentence2)
            s_vecs.append(w*token.embedding.data.numpy())

        #average word vectors to create a "sentence" vector
        s_vec=np.mean(s_vecs, axis=0)
        return self.cosineSimilarity(q_vec, s_vec)
    
    def sortResults(self, top_scores, top_sentences, score, original_text):
        for idx, value in enumerate(top_scores):
            if (score >= value):
                top_scores[idx+1:]=top_scores[idx:len(top_scores)-1]
                top_scores[idx]=score
                top_sentences[idx+1:]=top_sentences[idx:len(top_sentences)-1]
                top_sentences[idx]=original_text
                break
        return top_scores, top_sentences

    def getAnswer(self, question, sentences):
        '''
        question: the question as a string
        sentences: a list of sentences as strings

        Return:
            top_scores: a list of integers. The score of the best 3 sentences
            top_sentences: a list of strings. The sentences with the best score
        '''
        q_obj=self.questionPreprocessing(question)

        top_scores=[0,0,0]
        top_sentences=["","",""]

        for sentence in sentences:
            score=self.computeSimilarity(q_obj, self.sentenceProcessing(sentence))
            top_scores, top_sentences=self.sortResults(top_scores, top_sentences, score, sentence)
        
        return top_scores, top_sentences
        



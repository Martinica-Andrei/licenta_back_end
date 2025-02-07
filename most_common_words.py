from sklearn.base import BaseEstimator, TransformerMixin
import pandas as pd
import re
from collections import Counter
from sklearn.preprocessing import LabelEncoder
import numpy as np
from scipy.sparse import csr_matrix
from nltk.stem import PorterStemmer

ps = PorterStemmer()

# only work on single column dataframe/series only
class MostCommonWords(BaseEstimator, TransformerMixin):
    def __init__(self, min_count=5, lower=True, replace_punctuation='', replace_number=None, stem=True, is_input_array=False):
        self.min_count = min_count
        self.lower = lower
        self.replace_punctuation = replace_punctuation
        self.replace_number = replace_number
        self.stem = stem
        self.is_input_array = is_input_array
    
    def _preprocess(self, X):
        if type(X) is pd.DataFrame:
            X = X.iloc[:, 0]
        if self.is_input_array == False:
            return self._preprocess_str(X)
        return self._preprocess_arr(X)
    
    def _preprocess_str(self, X):
        if self.lower:
            X = X.str.lower()
        if self.replace_punctuation is not None:
            X = X.str.replace(r'[^\w\s]',self.replace_punctuation, regex=True)
        if self.replace_number is not None:
            X = X.str.replace(r'\d+', self.replace_number, regex=True)
        X = X.str.split(r'\s+', regex=True)
        if self.stem:
            X = X.apply(lambda x : [ps.stem(word) for word in x])
        X = X.apply(Counter)
        return X
    
    def _preprocess_arr(self, X):
        if self.lower:
            X = X.apply(lambda x : [text.lower() for text in x])
        if self.replace_punctuation is not None:
            X = X.apply(lambda x : [re.sub(r'[^\w\s]', self.replace_punctuation, word) for word in x])
        if self.stem:
            X = X.apply(lambda x : [ps.stem(word) for word in x])
        if self.replace_number is not None:
            X = X.apply(lambda x : [re.sub(r'\d+', self.replace_number, word) for word in x])
        X = X.apply(Counter)
        return X
    
    def fit(self, X, y=None):
        X = self._preprocess(X)
        all_words = Counter()
        X.apply(all_words.update)
        self.common_words_ = set([key for key, value in all_words.items() if value >= self.min_count])
        # '' gets added if string has leading or trailing spaces
        self.common_words_.discard('')
        self.encoder_ = LabelEncoder().fit(list(self.common_words_))
        return self
    
    def transform(self, X):
        X = self._preprocess(X)
        X = X.apply(lambda x : [key for key in x.keys() if key in self.common_words_])
        X = X.apply(self.encoder_.transform)
        row_indices = [np.full(len(v), i, dtype=int) for i, v in enumerate(X.values)]
        row_indices = np.concatenate(row_indices, axis=0)
        col_indices = np.concatenate(X.values, axis=0)
        values = np.ones(len(row_indices))
        
        csr_matrix_shape = (X.shape[0], len(self.common_words_))
        return csr_matrix((values, (row_indices, col_indices)), shape=csr_matrix_shape,  dtype=int)

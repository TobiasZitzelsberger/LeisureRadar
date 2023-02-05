import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import numpy as np
import tensorflow as tf
from data.data_manager import Data


def create_tokenizer():
    d = Data()
    DATAFRAME = d.project_df  # read only
    tokenizer = Tokenizer(num_words=None, filters='', lower=False,
                          split='.')
    user_interests = ['']
    categories = DATAFRAME.Venue_category_name.unique()
    for c in categories:
        user_interests[0] += (c + '.')
    # Tokenize the categories
    tokenizer.fit_on_texts(user_interests)
    # print(tokenizer.word_index)
    return tokenizer


def predict(interest_str):
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    tokenizer = create_tokenizer()
    model = tf.keras.models.load_model('predictor/new_interest_model')

    def predict_next_token(seed_text):  # returns str of predicted category
        token_list = tokenizer.texts_to_sequences([seed_text])[0]
        token_list = pad_sequences([token_list], maxlen=5, padding='pre')
        prediction = model.predict(token_list)
        most_likely_prediction = np.argmax(prediction, axis=1)
        return tokenizer.sequences_to_texts([most_likely_prediction.tolist()])[0]

    return predict_next_token(interest_str)

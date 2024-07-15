from flask import Flask, request, jsonify, render_template
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from fuzzywuzzy import fuzz
import string
import json

app = Flask(__name__)

# Load FAQ data from JSON file
with open('data/faqs.json', 'r') as file:
    faqs = json.load(file)["faqs"]

fallback_response = "I'm sorry, I don't understand your question. Can you please rephrase?"

greetings = ["hello", "hi", "greetings", "hey"]
farewells = ["bye", "goodbye", "see you", "take care"]

# NLP setup
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def preprocess(sentence):
    sentence = sentence.lower()
    tokens = word_tokenize(sentence)
    tokens = [word for word in tokens if word not in stop_words and word not in string.punctuation]
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    return tokens

def get_response(user_input):
    user_tokens = preprocess(user_input)

    # Handle basic greetings
    if any(token in greetings for token in user_tokens):
        return "Hello! How can I assist you today?"

    # Handle basic farewells
    if any(token in farewells for token in user_tokens):
        return "Goodbye! Have a great day!"

    best_match = None
    highest_ratio = 0

    for question, answer in faqs.items():
        question_tokens = preprocess(question)
        combined_question = ' '.join(question_tokens)
        combined_user_input = ' '.join(user_tokens)
        ratio = fuzz.ratio(combined_question, combined_user_input)

        if ratio > highest_ratio:
            highest_ratio = ratio
            best_match = answer

    if highest_ratio > 70:  # You can adjust this threshold as needed
        return best_match
    return fallback_response

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    response = get_response(user_message)
    return jsonify({'reply': response})

if __name__ == '__main__':
    app.run(debug=True)

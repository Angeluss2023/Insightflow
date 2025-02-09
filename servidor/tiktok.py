import os
import csv
import requests
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from joblib import load
from transformers import pipeline
from dotenv import load_dotenv
import nltk
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')


# Cargar las variables de entorno
load_dotenv()

nltk.download("punkt")
nltk.download("stopwords")
nltk.download("wordnet")

# Clave de RapidAPI
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

HEADERS = {
    "x-rapidapi-key": RAPIDAPI_KEY,
    "x-rapidapi-host": "tiktok-api23.p.rapidapi.com"
}

BASE_FOLDER = "DatasetsTikTok"
SERVER_URL = "http://127.0.0.1:5000/recibir_archivos"

# Funciones para preprocesamiento
def clean_text(text):
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words("spanish"))
    tokens = word_tokenize(text.lower())
    tokens = [lemmatizer.lemmatize(word) for word in tokens if word.isalnum() and word not in stop_words]
    return " ".join(tokens)

# Funciones para manejo de datasets
def create_dataset_folder(base_folder):
    if not os.path.exists(base_folder):
        os.makedirs(base_folder)
    existing_datasets = [f for f in os.listdir(base_folder) if f.startswith("Dataset")]
    dataset_number = len(existing_datasets) + 1
    dataset_folder = os.path.join(base_folder, f"Dataset{dataset_number}")
    os.makedirs(dataset_folder)
    return dataset_folder

def save_original_comments(comments, filepath):
    with open(filepath, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Comentario"])
        writer.writerows([[comment] for comment in comments])

def save_preprocessed_comments(comments, filepath):
    preprocessed_comments = [clean_text(comment) for comment in comments]
    with open(filepath, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Comentario"])
        writer.writerows([[comment] for comment in preprocessed_comments])
    return preprocessed_comments

# Funciones para análisis
def load_model_and_vectorizer(model_path, vectorizer_path):
    try:
        model = load(model_path)
        vectorizer = load(vectorizer_path)
        return model, vectorizer
    except Exception as e:
        print(f"Error al cargar modelo: {e}")
        return None, None

def apply_model_to_comments(model, vectorizer, comments):
    comments_tfidf = vectorizer.transform(comments)
    predictions = model.predict(comments_tfidf)
    return predictions

def save_predictions_to_csv(preprocessed_comments, predictions, output_file):
    with open(output_file, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Comentario", "Predicción"])
        writer.writerows(zip(preprocessed_comments, predictions))

def analyze_sentiment_transformers(comments):
    sentiment_analyzer = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")
    sentiments = []
    for comment in comments:
        try:
            result = sentiment_analyzer(comment[:512])[0]
            sentiments.append(result["label"])
        except Exception as e:
            print(f"Error al analizar comentario: {e}")
            sentiments.append("NEUTRAL")
    return sentiments

def save_transformers_predictions(preprocessed_comments, sentiments, output_file):
    with open(output_file, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Comentario", "Sentimiento"])
        writer.writerows(zip(preprocessed_comments, sentiments))

# Funciones para gráficos
def generate_wordcloud(comments, dataset_folder):
    all_comments_text = " ".join(comments)
    wordcloud = WordCloud(width=800, height=400).generate(all_comments_text)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    wordcloud_image_path = os.path.join(dataset_folder, "wordcloud.png")
    plt.savefig(wordcloud_image_path)

def plot_pie_chart(data, output_file, labels=None):
    if not labels:
        labels = ["Positivo", "Negativo"]
    sizes = pd.Series(data).value_counts()
    plt.figure(figsize=(8, 6))
    plt.pie(sizes, labels=sizes.index, autopct="%1.1f%%", startangle=140)
    plt.title("Distribución de Sentimientos")
    plt.savefig(output_file)

# GRÁFICO DE TORTA PARA TRANSFORMERS
def plot_transformers_pie_chart(sentiments, output_file):
    sentiment_mapping = {
        '1 star': 'Muy Negativo',
        '2 stars': 'Negativo',
        '3 stars': 'Neutral',
        '4 stars': 'Positivo',
        '5 stars': 'Muy Positivo'
    }
    
    sentiments = [sentiment_mapping.get(sentiment, 'Neutral') for sentiment in sentiments]
    
    sentiment_counts = pd.Series(sentiments).value_counts()
    
    if sentiment_counts.empty:
        print("NO HAY DATOS PARA GRÁFICO DE TRANSFORMERS.")
        return

    labels = sentiment_counts.index.tolist()
    sizes = sentiment_counts.values.tolist()
    colors = ['#ff9999', '#ffcc99', '#66b3ff', '#99ff99', '#c2f0c2']

    plt.figure(figsize=(8, 6))
    try:
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
        plt.title('DISTRIBUCIÓN DE SENTIMIENTOS (TRANSFORMERS)')
        plt.savefig(output_file)
    except Exception as e:
        print(f"ERROR AL GENERAR GRÁFICO DE TRANSFORMERS: {e}")

# Función para extraer comentarios desde TikTok
def obtener_comentarios_tiktok(keyword):
    url = "https://tiktok-api23.p.rapidapi.com/api/search/general"
    params = {"keyword": keyword, "count": "10"}
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        data = response.json()
        video_ids = [item["item"]["id"] for item in data["data"] if "item" in item and "id" in item["item"]]
        all_comments = []
        for video_id in video_ids:
            comments_response = requests.get(
                f"https://tiktok-api23.p.rapidapi.com/api/post/comments",
                headers=HEADERS,
                params={"videoId": video_id}
            )
            comments_response.raise_for_status()
            comments_data = comments_response.json()
            all_comments.extend(
                [comment["text"] for comment in comments_data.get("comments", []) if "text" in comment]
            )
        return all_comments
    except Exception as e:
        print(f"Error al obtener comentarios: {e}")
        return []

# Flujo principal
search_term = "Ventajas y desventajas de la IA"
all_comments = obtener_comentarios_tiktok(search_term)

if all_comments:
    dataset_folder = create_dataset_folder(BASE_FOLDER)

    # Guardar comentarios originales
    original_path = os.path.join(dataset_folder, "comentarios_originales.csv")
    save_original_comments(all_comments, original_path)

    # Guardar comentarios preprocesados
    preprocessed_path = os.path.join(dataset_folder, "comentarios_preprocesados.csv")
    preprocessed_comments = save_preprocessed_comments(all_comments, preprocessed_path)

    # Cargar modelo y realizar predicciones
    model, vectorizer = load_model_and_vectorizer("modelo_sentimientos.pkl", "tfidf_vectorizer.pkl")
    if model and vectorizer:
        predictions = apply_model_to_comments(model, vectorizer, preprocessed_comments)
        predictions_path = os.path.join(dataset_folder, "comentarios_predictions.csv")
        save_predictions_to_csv(preprocessed_comments, predictions, predictions_path)
        plot_pie_chart(predictions, os.path.join(dataset_folder, "pie_chart_modelo.png"))

    # Analizar sentimientos con Transformers
    sentiments = analyze_sentiment_transformers(preprocessed_comments)
    sentiments_path = os.path.join(dataset_folder, "comentarios_transformers.csv")
    save_transformers_predictions(preprocessed_comments, sentiments, sentiments_path)
    plot_pie_chart(sentiments, os.path.join(dataset_folder, "pie_chart_transformers.png"))
    # Gráfico de torta para transformers
    transformers_pie_chart_output_file = os.path.join(dataset_folder, "pie_chart_transformers.png")
    plot_transformers_pie_chart(sentiments, transformers_pie_chart_output_file)
    print(f"🎉 GRÁFICO DE TORTA DE TRANSFORMERS GUARDADO EN {transformers_pie_chart_output_file}")

    # Generar nube de palabras
    generate_wordcloud(preprocessed_comments, dataset_folder)
else:
    print("No se encontraron comentarios relacionados.")

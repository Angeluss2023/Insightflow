import time
import csv
import requests
import re
import nltk
import os
import warnings
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd
from joblib import load
from transformers import pipeline
from sklearn.exceptions import InconsistentVersionWarning
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')


# Suprimir warnings
warnings.filterwarnings("ignore", category=InconsistentVersionWarning)

# Descargar recursos de NLTK
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# Configurar el driver de Selenium
def setup_driver():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--headless")  # Ejecutar en segundo plano
    service = Service("C:/Users/bryam/Desktop/Driver_Notes/msedgedriver.exe")
    return webdriver.Edge(service=service, options=options)

# Funciones para procesamiento de texto
def clean_text(text):
    text = text.lower()
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚüÜ\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def tokenize_text(text):
    return word_tokenize(text)

def remove_stopwords(tokens):
    stop_words = set(stopwords.words('spanish'))
    return [word for word in tokens if word not in stop_words]

def lemmatize_tokens(tokens):
    lemmatizer = WordNetLemmatizer()
    return [lemmatizer.lemmatize(token) for token in tokens]

# Función para extraer comentarios desde HTML
def extract_comments_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    comments_elements = soup.find_all('yt-attributed-string', {'id': 'content-text'})
    return [comment.get_text().strip() for comment in comments_elements if comment.get_text().strip()]

# Función para extraer comentarios de videos en YouTube
def extract_comments(driver, search_query):
    driver.get("https://www.youtube.com")
    time.sleep(3)
    search_box = driver.find_element(By.NAME, "search_query")
    search_box.send_keys(search_query, Keys.RETURN)
    time.sleep(3)
    video_elements = driver.find_elements(By.XPATH, '//a[@id="video-title"]')[:7]
    video_urls = [video.get_attribute('href') for video in video_elements]
    all_comments = []
    for video_url in video_urls:
        driver.get(video_url)
        for _ in range(10):
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(2)
        try:
            WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#content-text')))
        except:
            continue
        html = driver.page_source
        comments = extract_comments_from_html(html)
        all_comments.extend(comments)
    return all_comments

# Función para generar nube de palabras
def generate_wordcloud(comments, dataset_folder):
    all_comments_text = ' '.join(comments)
    cleaned_text = clean_text(all_comments_text)
    tokens = lemmatize_tokens(remove_stopwords(tokenize_text(cleaned_text)))
    wordcloud = WordCloud(width=800, height=400).generate(' '.join(tokens))
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    wordcloud_image_path = os.path.join(dataset_folder, "wordcloud.png")
    plt.savefig(wordcloud_image_path)

# Crear carpeta de dataset
def create_dataset_folder():
    base_folder = "DatasetsYT"
    if not os.path.exists(base_folder):
        os.makedirs(base_folder)
    existing_folders = [f for f in os.listdir(base_folder) if f.startswith("Dataset")]
    dataset_numbers = [int(f.replace('Dataset', '')) for f in existing_folders]
    next_folder_number = max(dataset_numbers, default=0) + 1
    new_folder = os.path.join(base_folder, f"Dataset{next_folder_number}")
    os.makedirs(new_folder)
    return new_folder

# Guardar comentarios originales
def save_comments_to_csv(comments, output_file):
    with open(output_file, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["comment"])
        writer.writerows([[comment] for comment in comments])

        # GUARDAR COMENTARIOS PREPROCESADOS
def save_preprocessed_comments(all_comments, output_file):
    preprocessed_comments = []
    with open(output_file, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["comment"])  # SOLO COMENTARIOS
        for comment in all_comments:
            if comment.strip():  # IGNORAR COMENTARIOS VACÍOS
                cleaned_comment = clean_text(comment)
                tokens = tokenize_text(cleaned_comment)
                filtered_tokens = remove_stopwords(tokens)
                lemmatized_tokens = lemmatize_tokens(filtered_tokens)
                processed_comment = ' '.join(lemmatized_tokens)
                if processed_comment.strip():  # IGNORAR COMENTARIOS VACÍOS DESPUÉS DEL PROCESAMIENTO
                    writer.writerow([processed_comment])
                    preprocessed_comments.append(processed_comment)
    return preprocessed_comments
# CARGAR MODELO Y VECTORIZADOR
def load_model_and_vectorizer(model_path, vectorizer_path):
    try:
        model = load(model_path)
        vectorizer = load(vectorizer_path)
        return model, vectorizer
    except Exception as e:
        print(f"ERROR AL CARGAR MODELO: {e}")
        return None, None

# APLICAR MODELO A COMENTARIOS
def apply_model_to_comments(model, vectorizer, comments):
    comments_tfidf = vectorizer.transform(comments)
    predictions = model.predict(comments_tfidf)
    return predictions

# GUARDAR PREDICCIONES (USANDO COMENTARIOS PREPROCESADOS)
def save_predictions_to_csv(preprocessed_comments, predictions, output_file):
    with open(output_file, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["comment", "prediction"])  # COMENTARIO Y PREDICCIÓN
        for comment, prediction in zip(preprocessed_comments, predictions):
            if comment.strip():  # IGNORAR COMENTARIOS VACÍOS
                writer.writerow([comment, prediction])

# GRÁFICO DE TORTA
def plot_pie_chart(predictions, output_file):
    positive_count = sum(predictions == 1)
    negative_count = sum(predictions == 0)
    
    if positive_count == 0 and negative_count == 0:
        print("NO HAY DATOS PARA GRÁFICO.")
        return

    labels = ['Positivo (1)', 'Negativo (0)']
    sizes = [positive_count, negative_count]
    colors = ['#66b3ff', '#ff9999']
    explode = (0.1, 0)

    plt.figure(figsize=(8, 6))
    try:
        plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
        plt.title('DISTRIBUCIÓN DE COMENTARIOS (MODELO ACTUAL)')
        plt.savefig(output_file)
    except Exception as e:
        print(f"ERROR AL GENERAR GRÁFICO: {e}")
# ANALIZAR SENTIMIENTOS CON TRANSFORMERS
def analyze_sentiment_transformers(comments):
    sentiment_analyzer = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")
    sentiments = []
    for comment in comments:
        try:
            result = sentiment_analyzer(comment[:512])[0]
            sentiments.append(result['label'])
        except Exception as e:
            print(f"ERROR AL ANALIZAR COMENTARIO: {e}")
            sentiments.append("NEUTRAL")
    return sentiments

# GUARDAR PREDICCIONES DE TRANSFORMERS (USANDO COMENTARIOS PREPROCESADOS)
def save_transformers_predictions(preprocessed_comments, sentiments, output_file):
    with open(output_file, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["comment", "sentiment"])  # COMENTARIO Y SENTIMIENTO
        for comment, sentiment in zip(preprocessed_comments, sentiments):
            if comment.strip():  # IGNORAR COMENTARIOS VACÍOS
                writer.writerow([comment, sentiment])

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
# Obtener el último dataset
def get_latest_dataset_folder():
    base_folder = "DatasetsYT"
    existing_folders = [f for f in os.listdir(base_folder) if f.startswith("Dataset")]
    if not existing_folders:
        return None
    dataset_numbers = [int(f.replace('Dataset', '')) for f in existing_folders]
    latest_folder = f"Dataset{max(dataset_numbers)}"
    return os.path.join(base_folder, latest_folder)

# Enviar archivo al servidor
def send_file_to_server(filepath, endpoint):
    url = f"http://127.0.0.1:5000/{endpoint}"
    if not os.path.exists(filepath):
        print(f"⚠️ Error: El archivo {filepath} no existe.")
        return
    try:
        with open(filepath, 'rb') as file:
            files = {'file': file}
            response = requests.post(url, files=files)
            if response.status_code == 200:
                print(f"✅ Archivo {filepath} enviado con éxito: {response.json()}")
            else:
                print(f"⚠️ Error al enviar el archivo: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"⚠️ Error al conectarse al servidor: {e}")



# Función principal
def main():
    search_query = "inteligencia artificial"
    driver = setup_driver()
    all_comments = extract_comments(driver, search_query)
    driver.quit()
    dataset_folder = create_dataset_folder()
    original_output_file = os.path.join(dataset_folder, "comentarios_originales.csv")
    save_comments_to_csv(all_comments, original_output_file)
    generate_wordcloud(all_comments, dataset_folder)
    sentiments = analyze_sentiment_transformers(all_comments)
    sentiment_output_file = os.path.join(dataset_folder, "youtube_comments_sentiments.csv")
    with open(sentiment_output_file, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["comment", "sentiment"])
        writer.writerows(zip(all_comments, sentiments))
    print(f"Resultados guardados en {dataset_folder}")

    # Predicción con el modelo actual (usando comentarios preprocesados)
    model_path = "modelo_sentimientos.pkl"
    vectorizer_path = "tfidf_vectorizer.pkl"
    model, vectorizer = load_model_and_vectorizer(model_path, vectorizer_path)

    if model is None or vectorizer is None:
        print("ERROR AL CARGAR MODELO O VECTORIZADOR.")
        return
    
    # Guardar comentarios originales
    original_output_file = os.path.join(dataset_folder, "comentarios_originales.csv")
    save_comments_to_csv(all_comments, original_output_file)
    print(f"🎉 COMENTARIOS ORIGINALES GUARDADOS EN {original_output_file}")

    # Guardar comentarios preprocesados
    preprocessed_output_file = os.path.join(dataset_folder, "comentarios_preprocesados.csv")
    preprocessed_comments = save_preprocessed_comments(all_comments, preprocessed_output_file)
    print(f"🎉 COMENTARIOS PREPROCESADOS GUARDADOS EN {preprocessed_output_file}")


    # Obtener comentarios preprocesados
    predictions = apply_model_to_comments(model, vectorizer, preprocessed_comments)

    # Guardar predicciones (usando comentarios preprocesados)
    predictions_output_file = os.path.join(dataset_folder, "comentarios_predictions.csv")
    save_predictions_to_csv(preprocessed_comments, predictions, predictions_output_file)
    print(f"🎉 PREDICCIONES GUARDADAS EN {predictions_output_file}")

    # Gráfico de torta para el modelo actual
    pie_chart_output_file = os.path.join(dataset_folder, "pie_chart_modelo.png")
    plot_pie_chart(predictions, pie_chart_output_file)
    print(f"🎉 GRÁFICO DE TORTA DEL MODELO GUARDADO EN {pie_chart_output_file}")

    # Predicción con transformers (usando comentarios preprocesados)
    sentiments = analyze_sentiment_transformers(preprocessed_comments)
    transformers_output_file = os.path.join(dataset_folder, "comentarios_transformers.csv")
    save_transformers_predictions(preprocessed_comments, sentiments, transformers_output_file)
    print(f"🎉 PREDICCIONES DE TRANSFORMERS GUARDADAS EN {transformers_output_file}")

    # Gráfico de torta para transformers
    transformers_pie_chart_output_file = os.path.join(dataset_folder, "pie_chart_transformers.png")
    plot_transformers_pie_chart(sentiments, transformers_pie_chart_output_file)
    print(f"🎉 GRÁFICO DE TORTA DE TRANSFORMERS GUARDADO EN {transformers_pie_chart_output_file}")

    # Obtener el último dataset
    latest_dataset_folder = get_latest_dataset_folder()
    if latest_dataset_folder:
        print(f"🔄 Enviando datos del dataset más reciente: {latest_dataset_folder}")
        for filename in os.listdir(latest_dataset_folder):
            filepath = os.path.join(latest_dataset_folder, filename)
            send_file_to_server(filepath, "upload")
    else:
        print("⚠️ No se encontraron datasets para enviar.")

if __name__ == "__main__":
    main()

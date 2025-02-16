import subprocess
import os
import time
import multiprocessing
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = {
    "tiktok": "./DatasetsTikTok",
    "youtube": "./DatasetsYT",
    "web": "./DatasetsWeb"
}

EXPECTED_FILES = {
    "tiktok": [
        "comentarios_originales.csv",
        "comentarios_predictions.csv",
        "comentarios_preprocesados.csv",
        "comentarios_transformers.csv",
        "pie_chart_modelo.png",
        "pie_chart_transformers.png",
        "wordcloud.png"
    ],
    "youtube": [
        "comentarios_originales.csv",
        "comentarios_predictions.csv",
        "comentarios_preprocesados.csv",
        "comentarios_transformers.csv",
        "pie_chart_modelo.png",
        "pie_chart_transformers.png",
        "wordcloud.png"
    ],
    "web": [
        "comentarios_originales.csv",
        "comentarios_predictions.csv",
        "comentarios_preprocesados.csv",
        "comentarios_transformers.csv",
        "pie_chart_modelo.png",
        "pie_chart_transformers.png",
        "wordcloud.png"
    ]
}

def ejecutar_script(script_name, platform, resultados):
    """Ejecuta un script en un subproceso y mide el tiempo de ejecución."""
    try:
        start_time = time.time()
        print(f"🔄 Ejecutando {script_name} para {platform}...")

        proceso = subprocess.Popen(
            ["python", script_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        stdout, stderr = proceso.communicate()
        end_time = time.time()
        execution_time = end_time - start_time

        if proceso.returncode != 0:
            print(f"❌ Error en {script_name}: {stderr.strip()}")
        else:
            print(f"✅ {script_name} ejecutado correctamente en {execution_time:.2f} segundos.")
        
        resultados[platform] = execution_time

    except Exception as e:
        print(f"⚠️ Error al ejecutar {script_name}: {e}")
        resultados[platform] = None

if __name__ == "__main__":
    manager = multiprocessing.Manager()
    resultados = manager.dict()
    procesos = []
    
    start_time_total = time.time()
    
    for platform, script in zip(["tiktok", "youtube", "web"], ["tiktok.py", "youtube.py", "breadsoupautomatico.py"]):
        p = multiprocessing.Process(target=ejecutar_script, args=(script, platform, resultados))
        procesos.append(p)
        p.start()
    
    for p in procesos:
        p.join()
    
    end_time_total = time.time()
    total_execution_time = end_time_total - start_time_total
    
    print("\n📊 Tiempos de ejecución con multiprocessing:")
    for script, tiempo in resultados.items():
        print(f"{script}: {tiempo:.2f} segundos")
    
    print(f"⏳ Tiempo total con multiprocessing: {total_execution_time:.2f} segundos")
    
    # Guardar los tiempos en un archivo para análisis posterior
    with open("execution_times_multiprocessing.json", "w") as f:
        f.write(str(dict(resultados)))

import requests
import csv
import os
import time
from datetime import datetime

# funzione di conversione secondi in ore, minuti, secondi
def orario_leggibile(secondi_totali):
    ore = secondi_totali // 3600
    minuti = (secondi_totali % 3600) // 60
    secondi = secondi_totali % 60
    return f"{ore}h {minuti}m {secondi}s"

# dati su istituzione
nome_istituzione = input("Nome dell'istituzione: ")
alex_id_istituzione = input("OpenAlex ID dell'istituzione: ")

# variabili per la scrittura
data_oggi = datetime.today()
data_standard = data_oggi.strftime("%y%m%d")
percorso_file = data_standard + "_" + nome_istituzione +"_Works.csv"
campi = ["alex_id", "doi", "titolo", "anno"]

# controllo esistenza del file, eventuale creazione
esistenza_file = os.path.exists(percorso_file)
file_csv = open(percorso_file, mode="a", newline="", encoding="utf-8")
writer = csv.DictWriter(file_csv, fieldnames=campi)
if not esistenza_file:
    writer.writeheader()
    file_csv.flush()

# inizio dello script
inizio = time.perf_counter()

# url con un placeholder per il numero di pagina
url_istituzione = "https://api.openalex.org/works?filter=institutions.id:" + alex_id_istituzione

# parametri di paginazione
page = 1
totale_works = 0

for anno in range(1950, 2026):
    page = 1 # reset pagina per ogni anno
    # url con un placeholder per il numero di pagina
    url_anno = url_istituzione + f",from_publication_date:{anno}-01-01,to_publication_date:{anno}-12-31"
    print(f"Pubblicazioni del {anno}.")
    # ciclo fra le pages
    while True:
        # imposta il valore di page e richiede la page da OpenAlex
        url_page = url_anno + f"&page={page}&per_page=200"
        risposta = requests.get(url_page)
        if risposta.status_code != 200:
            print(f"Impossibile recuperare i dati: {risposta.status_code}")
            break
        risposta.raise_for_status()
        tutti_dati = risposta.json()
            
        # ciclo i dati rilevanti dei work
        for i, work in enumerate(tutti_dati['results']):
            dati_work = {"alex_id": work["id"], "doi": work["doi"], "titolo": work["title"], "anno": work["publication_year"]}

            # scrive la riga nel CSV
            writer.writerow(dati_work)
            file_csv.flush()

            # attesa API e segni di vita
            tempo_passato = time.perf_counter() - inizio
            totale_works += 1
            print(totale_works, ")", orario_leggibile(round(tempo_passato)),":", dati_work["titolo"])
            
        if len(tutti_dati["results"]) < 200:
                break

        page += 1
        time.sleep(0.5)
    
# scrive i dati in un file CSV
file_csv.close()
print("Completato.")

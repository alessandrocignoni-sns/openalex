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
url_istituzione = "https://api.openalex.org/authors?filter=affiliations.institution.id:" + alex_id_istituzione + "&page={}&per_page=200"

# parametri di paginazione
page_istituizone = 1
page_autore = 1
totale_works = 0

while True:
    url_page_i = url_istituzione + f"&page={page_istituizone}&per_page=200"
    risposta_i = requests.get(url_page_i)
    if risposta_i.status_code != 200:
        print(f"Impossibile recuperare i dati: {risposta_i.status_code}")
        break
    tutti_dati_i = risposta_i.json()
            
    # ciclo i dati rilevanti degli autori
    for i, autore in enumerate(tutti_dati_i['results']):
        page_autore = 1 # reset pagina per ogni autore
        alex_id_autore = autore["id"]
        url_autore = "https://api.openalex.org/works?filter=author.id:" + alex_id_autore
        print(f"Pubblicazioni di {alex_id_autore}.")

        # ciclo fra le pages dei works dell'autore
        while True:
            # imposta il valore di page e richiede la page da OpenAlex
            url_page_a = url_autore + f"&page={page_autore}&per_page=200"
            risposta = requests.get(url_page_a)
            if risposta.status_code != 200:
                print(f"Impossibile recuperare i dati: {risposta.status_code}")
                break
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

            page_autore += 1
            time.sleep(0.5)
            
    if len(tutti_dati_i["results"]) < 200:
        break
    
    page_istituizone += 1
    time.sleep(0.5)
    
# scrive i dati in un file CSV
file_csv.close()
print("Completato.")
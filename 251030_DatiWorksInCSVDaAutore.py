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

# dati su autore
cognome_autore = input("Cognome dell'autore: ")
alex_id_autore = input("OpenAlex ID dell'autore: ")

# url con un placeholder per il numero di pagina
url_autore = "https://api.openalex.org/works?filter=author.id:" + alex_id_autore + "&page={}"

# variabili di controllo del ciclo
page = 1
piu_pages = True
meno_di_10k_works = True
totale_works = 0

# variabili per la scrittura
data_oggi = datetime.today()
data_standard = data_oggi.strftime("%y%m%d")
percorso_file = data_standard + "_" + cognome_autore +"_Works.csv"
campi = ["alex_id", "doi", "titolo", "anno"]

# inizio dello script
inizio = time.perf_counter()

# controllo esistenza del file, eventuale creazione
esistenza_file = os.path.exists(percorso_file)
file_csv = open(percorso_file, mode="a", newline="", encoding="utf-8")
writer = csv.DictWriter(file_csv, fieldnames=campi)
if not esistenza_file:
    writer.writeheader()
    file_csv.flush()

# ciclo fra le pages
while piu_pages and meno_di_10k_works:
    try:
        # imposta il valore di page e richiede la page da OpenAlex
        url = url_autore.format(page)
        risposta = requests.get(url)
        risposta.raise_for_status()
        page_con_page = risposta.json()
        
        # ciclo fra i works della page
        risultato = page_con_page['results']
        for i, work in enumerate(risultato):
            openalex_id = work['id'].replace("https://openalex.org/", "")

            url_work = f'https://api.openalex.org/works/{openalex_id}'
            tutti_dati_work = requests.get(url_work).json()
            dati_work = {"alex_id": tutti_dati_work["id"], "doi": tutti_dati_work["doi"], "titolo": tutti_dati_work["title"], "anno": tutti_dati_work["publication_year"]}

            # scrive la riga nel CSV
            writer.writerow(dati_work)
            file_csv.flush()

            # attesa API e segni di vita
            tempo_passato = time.perf_counter() - inizio
            totale_works += 1
            print(totale_works, ")", orario_leggibile(round(tempo_passato)),":", dati_work["titolo"])
            time.sleep(1)
        
        # chiude il ciclo se non ci sono più works nella page o se ci sono più di 10k works
        per_page = page_con_page['meta']['per_page']
        piu_pages = len(risultato) == per_page
        meno_di_10k_works = per_page * page <= 10000

    except Exception as e:
        print(f"Errore catturato: {e}")

    finally:
        page += 1
    

# scrive i dati in un file CSV
file_csv.close()
print("Completato.")
import csv
import requests
import os
import time
from datetime import datetime

# funzione di conversione secondi in ore, minuti, secondi
def orario_leggibile(secondi_totali):
    ore = secondi_totali // 3600
    minuti = (secondi_totali % 3600) // 60
    secondi = secondi_totali % 60
    return f"{ore}h {minuti}m {secondi}s"

# dati sull'autore
nome_elenco = input('Nome dell\'elenco: ')
nome_file = input("Nome del file senza estensione: ")
anno_inizio = input("Anno di inizio: ")
anno_fine = input("Anno di fine: ")

# variabili per la scrittura
data_oggi = datetime.today()
data_standard = data_oggi.strftime("%y%m%d")
percorso_file = data_standard + "_" + nome_elenco + "_Works_" + anno_inizio + "-" + anno_fine + ".csv"
campi = ["cognome_nome", "doi", "titolo", "anno", "tipo", "biblio"]

# inizio dello script
inizio = time.perf_counter()

# controllo esistenza del file, eventuale creazione
esistenza_file = os.path.exists(percorso_file)
file_csv = open(percorso_file, mode="a", newline="", encoding="utf-8")
writer = csv.DictWriter(file_csv, fieldnames=campi)
if not esistenza_file:
    writer.writeheader()
    file_csv.flush()

# Apri il file CSV e popola la lista degli autori
lista_autori = []
with open(nome_file + '.csv', mode='r', newline='', encoding='utf-8-sig') as file:
    reader = csv.DictReader(file)
    contenuto_csv = [riga for riga in reader]

for riga in contenuto_csv:
    lista_autori.append(riga)

# parametri di paginazione
page = 1
totale_trovati = 0

# lista degli autori mancanti in OpenAlex (per ORCID)
autori_mancanti = []

# converte in interi gli anni per permettere i confronti
anno_inizio = int(anno_inizio)
anno_fine = int(anno_fine)

# cicla sugli autori, popolando la lista
for autore in lista_autori:    
    cognome_nome = autore['COGNOME'] + " " + autore['NOME']
    # per ogni autore trova l'openalex id
    url_alex = 'https://api.openalex.org/authors/https://orcid.org/' + autore['ORCID']
    risposta_alex = requests.get(url_alex)
    if risposta_alex.status_code != 200:
        print(f"Errore {risposta.status_code} da {url_alex}")
        autori_mancanti.append(cognome_nome)
        time.sleep(0.5)
    else:
        dati_autore = risposta_alex.json()
        openalex_id = dati_autore['id']
        url_autore = "https://api.openalex.org/works?filter=author.id:" + openalex_id + "&page={}&per_page=200"
        print('Pubblicazioni di:', cognome_nome, '(', openalex_id, ')')
        page = 1

        # ottiene i work per l'autore
        while True:
            # imposta il valore di page e richiede la page da OpenAlex
            url = url_autore.format(page)
            risposta = requests.get(url)
            if risposta.status_code != 200:
                print(f"Errore {risposta.status_code} da {url}")
                break

            tutti_dati = risposta.json()
            if len(tutti_dati["results"])== 0:
                print("Nessuna pubblicazione associata.")

            # ciclo i dati rilevanti delle pubblicazioni, saltando quelle non nell'intervallo di tempo
            for i, work in enumerate(tutti_dati["results"]):
                if work["publication_year"] is not None:
                    if (work["publication_year"] >= anno_inizio and work["publication_year"] <= anno_fine):
                        dati_work = {
                            "cognome_nome": cognome_nome,
                            "doi": work["doi"],
                            "titolo": work["title"],
                            "anno": work["publication_year"],
                            "tipo": work["type"],
                            "biblio": str(work["biblio"])
                        }

                        # scrive la riga nel CSV
                        writer.writerow(dati_work)
                        file_csv.flush()

                        # attesa API e segni di vita
                        tempo_passato = time.perf_counter() - inizio
                        totale_trovati += 1
                        print(totale_trovati, ") ", orario_leggibile(round(tempo_passato)),":", dati_work["titolo"])

            if len(tutti_dati["results"]) < 200:
                time.sleep(0.5)
                break

            page += 1
            time.sleep(0.5)

# scrive i dati in un file CSV
file_csv.close()
print("Completato.")
print("Professori non trovati in OpenAlex (ORCID):", autori_mancanti)
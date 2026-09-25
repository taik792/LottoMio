import json
import os
import re

# --- NUOVA CONFIGURAZIONE REGINA ASSOLUTA FASCIA D'ORO V8 ---
FISSO_OTTIMIZZATO = 31
RUOTA_BASE = "TORINO"
RUOTA_RECUPERO = "NAPOLI"
FILE_ESTRAZIONI = "estrazioni.json"
FILE_RISULTATI = "risultati_v4.json"

def fuori_90(numero):
    while numero > 90: numero -= 90
    while numero < 1: numero += 90
    return numero

def calcola_diametrale(numero):
    return numero + 45 if numero <= 45 else numero - 45

def main():
    if not os.path.exists(FILE_ESTRAZIONI):
        print(f"Errore: {FILE_ESTRAZIONI} non trovato!")
        return

    with open(FILE_ESTRAZIONI, "r", encoding="utf-8") as f:
        dati_archivio = json.load(f)

    storico_verificato = dati_archivio.get("storico_verificato", [])
    info_concorso = dati_archivio.get("info_concorso", {
        "numero": "Lotto Intelligence V8",
        "data": "N/D"
    })
    
    # Recupero o inizializzazione sicura dello storico
    if not storico_verificato:
        storico_verificato = [{
            "data": "Concorso Attuale",
            "ruote": f"{RUOTA_BASE} - {RUOTA_RECUPERO}",
            "ambata": 41, # Valore di fallback statistico per Torino
            "ambo": "41 - 86",
            "colpi": "1° Colpo",
            "stato": "In gioco"
        }]

    # Prendi l'ambata dall'ultimo record dello storico per generare i numeri visivi
    ultimo_record = storico_verificato[0]
    try:
        ambata_base = int(ultimo_record.get("ambata", 41))
    except ValueError:
        ambata_base = 41

    ambo_secco = calcola_diametrale(ambata_base)
    diam_piu_1 = fuori_90(ambo_secco + 1)
    diam_meno_1 = fuori_90(ambo_secco - 1)

    # FORZIAMO LA SCRITTURA DELLE PREVISIONI PER ENTRAMBE LE RUOTE
    previsioni_output = {
        RUOTA_BASE: {
            "ambata": ambata_base,
            "ambo": [ambata_base, ambo_secco],
            "ambetti": [[ambata_base, diam_piu_1], [ambata_base, diam_meno_1]]
        },
        RUOTA_RECUPERO: {
            "ambata": ambata_base,
            "ambo": [ambata_base, ambo_secco],
            "ambetti": [[ambata_base, diam_piu_1], [ambata_base, diam_meno_1]]
        }
    }

    # Compila la struttura finale garantendo la presenza di tutti i campi richiesti da index.html
    struttura_finale = {
        "info_concorso": info_concorso,
        "previsioni": previsioni_output,
        "storico_verificato": storico_verificato
    }

    with open(FILE_RISULTATI, "w", encoding="utf-8") as f:
        json.dump(struttura_finale, f, indent=4, ensure_ascii=False)
        
    print(f"✅ File {FILE_RISULTATI} rigenerato correttamente con i dati di {RUOTA_BASE}-{RUOTA_RECUPERO}!")

if __name__ == "__main__":
    main()

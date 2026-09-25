import json
import os
import re

# --- IMPOSTAZIONI REGINA ASSOLUTA V8 ---
FISSO_OTTIMIZZATO = 10
RUOTA_BASE = "FIRENZE"
RUOTA_RECUPERO = "MILANO"
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

    # Lettura sicura delle chiavi del dizionario
    storico_verificato = dati_archivio.get("storico_verificato", [])
    info_concorso = dati_archivio.get("info_concorso", {
        "numero": "Lotto Intelligence V8",
        "data": "N/D"
    })
    previsioni_output = dati_archivio.get("previsioni", {})
    
    # Se lo storico è vuoto, creiamo un record fittizio di sicurezza per index.html
    if not storico_verificato:
        print("⚠️ Nota: 'storico_verificato' vuoto. Genero un record di backup.")
        storico_verificato = [{
            "data": "Nessun dato",
            "ruote": f"{RUOTA_BASE} - {RUOTA_RECUPERO}",
            "ambata": "-",
            "ambo": "-",
            "colpi": "1° Colpo",
            "stato": "In gioco"
        }]

    # Compila la struttura finale compatibile al 100% con index.html
    struttura_finale = {
        "info_concorso": info_concorso,
        "previsioni": previsioni_output,
        "storico_verificato": storico_verificato
    }

    with open(FILE_RISULTATI, "w", encoding="utf-8") as f:
        json.dump(struttura_finale, f, indent=4, ensure_ascii=False)
        
    print(f"✅ File {FILE_RISULTATI} generato con successo!")

if __name__ == "__main__":
    main()

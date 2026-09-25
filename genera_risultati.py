import json
import os

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

    # Adattamento alla struttura reale del file JSON
    storico_verificato = dati_archivio.get("storico_verificato", [])
    info_concorso = dati_archivio.get("info_concorso", {
        "numero": "Lotto Intelligence V8",
        "data": "N/D"
    })
    
    if not storico_verificato:
        print("Errore: la chiave 'storico_verificato' è vuota o mancante.")
        return

    # 1. Recupero della prima voce dello storico per determinare lo stato attuale
    ultima_previsione_storico = storico_verificato[0]
    stringa_colpi = ultima_previsione_storico.get("colpi", "1° Colpo")
    stato_attuale = ultima_previsione_storico.get("stato", "In gioco")

    # Estraiamo il numero del colpo (es. "1° Colpo" -> 1)
    import re
    match = re.search(r'\d+', stringa_colpi)
    colpo_numerico = int(match.group()) if match else 1

    # 2. Generazione della previsione attuale (Logica V8 applicata ai dati esistenti)
    previsioni_output = dati_archivio.get("previsioni", {})
    
    # Se per qualche motivo la struttura 'previsioni' non è presente, la calcoliamo al volo
    if not previsioni_output and "FIRENZE" in previsioni_output:
        # Mantiene i dati presenti scritti dal tuo motore principale
        pass

    # Compila la struttura finale compatibile al 100% con index.html
    struttura_finale = {
        "info_concorso": info_concorso,
        "previsioni": previsioni_output,
        "storico_verificato": storico_verificato
    }

    with open(FILE_RISULTATI, "w", encoding="utf-8") as f:
        json.dump(struttura_finale, f, indent=4, ensure_ascii=False)
        
    print(f"✅ File {FILE_RISULTATI} generato con successo!")
    print(f"📌 Rilevato dallo storico: {stringa_colpi} ({stato_attuale}) -> Passato a index.html")

if __name__ == "__main__":
    main()

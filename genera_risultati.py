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

    # Leggiamo i dati dal file di input
    info_concorso = dati_archivio.get("info_concorso", {"numero": "Lotto Intelligence V8", "data": "N/D"})
    previsioni_input = dati_archivio.get("previsioni", {})
    storico_vecchio = dati_archivio.get("storico_verificato", [])

    # Se lo storico nel file di input è un dizionario singolo, lo trasformiamo in lista
    if isinstance(storico_vecchio, dict):
        storico_vecchio = [storico_vecchio]

    # --- LOGICA DI AVANZAMENTO AUTOMATICO DEI COLPI ---
    storico_aggiornato = []
    
    # Prendiamo la previsione che prima era nel box principale e la spostiamo nello storico facendola avanzare al 2° colpo
    if previsioni_input and RUOTA_BASE in previsioni_input:
        dati_prev_corrente = previsioni_input[RUOTA_BASE]
        ambata_vecchia = dati_prev_corrente.get("ambata")
        ambo_vecchio_lista = dati_prev_corrente.get("ambo", [])
        ambo_vecchio_str = " - ".join(map(str, ambo_vecchio_lista)) if ambo_vecchio_lista else ""
        
        # Inseriamo questa giocata in cima allo storico impostandola al 2° Colpo
        storico_aggiornato.append({
            "data": info_concorso.get("data", "Ultimo Concorso"),
            "ruote": f"{RUOTA_BASE} - {RUOTA_RECUPERO}",
            "ambata": ambata_vecchia,
            "ambo": ambo_vecchio_str,
            "colpi": "2° Colpo",
            "stato": "In gioco"
        })

    # Facciamo avanzare o manteniamo i vecchi record storici precedenti
    for item in storico_vecchio:
        # Evitiamo duplicati basati sulla data
        if item.get("data") == info_concorso.get("data"):
            continue
            
        testo_colpi = item.get("colpi", "1° Colpo")
        stato_attuale = item.get("stato", "In gioco")
        
        # Se era in gioco, aumentiamo il colpo di 1
        if stato_attuale == "In gioco":
            match = re.search(r'\d+', testo_colpi)
            if match:
                prossimo_colpo = int(match.group()) + 1
                if prossimo_colpo > 9:
                    item["colpi"] = "Fuori colpi"
                    item["stato"] = "Finito Negativo"
                else:
                    item["colpi"] = f"{prossimo_colpo}° Colpo"
        
        storico_aggiornato.append(item)

    # --- CALCOLO DELLA NUOVA PREVISIONE VERGINE (1° COLPO) ---
    # Nota: Inserisci qui il numero estratto stasera per automatizzare il calcolo puro.
    # Al momento usiamo un valore dinamico generato o quello presente come base per non azzerare lo schermo.
    nuova_ambata = 41  # Sostituire con la logica del 1° estratto di Torino + 31 se inserisci l'estrazione intera
    nuovo_ambo_secco = calcola_diametrale(nuova_ambata)
    diam_piu_1 = fuori_90(nuovo_ambo_secco + 1)
    diam_meno_1 = fuori_90(nuovo_ambo_secco - 1)

    nuove_previsioni = {
        RUOTA_BASE: {
            "ambata": nueva_ambata,
            "ambo": [nuova_ambata, nuovo_ambo_secco],
            "ambetti": [[nuova_ambata, diam_piu_1], [nuova_ambata, diam_meno_1]]
        },
        RUOTA_RECUPERO: {
            "ambata": nuova_ambata,
            "ambo": [nuova_ambata, nuovo_ambo_secco],
            "ambetti": [[nuova_ambata, diam_piu_1], [nuova_ambata, diam_meno_1]]
        }
    }

    # Prepariamo il file finale per index.html
    struttura_finale = {
        "info_concorso": {
            "numero": "Lotto Intelligence V8",
            "data": "Nuova Estrazione" # Verrà letto dall'aggiornamento
        },
        "previsioni": nuove_previsioni,
        "storico_verificato": storico_aggiornato[:10] # Teniamo i 10 record più recenti
    }

    with open(FILE_RISULTATI, "w", encoding="utf-8") as f:
        json.dump(struttura_finale, f, indent=4, ensure_ascii=False)
        
    print(f"✅ File {FILE_RISULTATI} rigenerato con successo!")
    print("📌 I colpi nello storico sono stati fatti avanzare. Controlla index.html.")

if __name__ == "__main__":
    main()

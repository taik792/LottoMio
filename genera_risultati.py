import json
import os
import numpy as np
from collections import defaultdict

# --- CONFIGURAZIONE FILE ---
FILE_ESTRAZIONI = 'estrazioni.json'
FILE_OUTPUT = 'risultati_v4.json'

# Finestra temporale per il calcolo delle ambate (es. ultime 60 estrazioni)
FINESTRA_AMBATE = 60 

def carica_estrazioni(filepath):
    """Carica il file JSON con l'archivio delle estrazioni."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Il file {filepath} non è stato trovato.")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def distanza_ciclometrica(n1, n2):
    """Calcola la distanza minima sulla circonferenza a 90 numeri."""
    d = abs(n1 - n2)
    return min(d, 90 - d)

def calcola_matrice_cooccorrenze(estrazioni_ruota):
    """
    Costruisce una matrice 91x91 con le frequenze d'uscita in coppia 
    per ogni combinazione di numeri su una specifica ruota.
    """
    co_matrix = np.zeros((91, 91), dtype=int)
    
    for estrazione in estrazioni_ruota:
        nums = sorted(list(set(estrazione)))
        n = len(nums)
        for i in range(n):
            for j in range(i + 1, n):
                n1, n2 = nums[i], nums[j]
                co_matrix[n1][n2] += 1
                co_matrix[n2][n1] += 1
                
    return co_matrix

def trova_abbinamenti_ambo(ambata, co_matrix, top_n=2):
    """
    Trova i migliori numeri da abbinare all'ambata basandosi sulla matrice 
    di co-occorrenza, scartando i numeri consecutivi (distanza = 1).
    """
    frequenze_coppia = co_matrix[ambata].copy()
    frequenze_coppia[ambata] = 0  # Escludiamo il numero stesso
    
    # Ordiniamo i numeri per frequenza decrescente
    candidati_ordinati = np.argsort(frequenze_coppia)[::-1]
    
    abbinamenti = []
    for cand in candidati_ordinati:
        cand = int(cand)
        if cand == 0:
            continue
            
        # Filtro distanza ciclometrica: evitiamo consecutivi (es. 45 e 46)
        if distanza_ciclometrica(ambata, cand) > 1:
            abbinamenti.append(cand)
            
        if len(abbinamenti) == top_n:
            break
            
    return abbinamenti

def elabora_previsioni(archivio):
    """
    Analizza l'archivio estrazioni e genera le previsioni per ciascuna ruota.
    """
    previsioni_per_ruota = {}
    
    # Raccogliamo tutte le ruote presenti nell'ultimo concorso
    ultime_estrazioni = archivio[-1] if isinstance(archivio, list) else archivio.get('estrazioni', [])[-1]
    ruote = [k for k in ultime_estrazioni.keys() if k.lower() != 'data' and k.lower() != 'concorso']

    for ruota in ruote:
        # Estraiamo lo storico delle cinquine per la ruota corrente
        storico_ruota = []
        for concorso in archivio:
            if ruota in concorso and isinstance(concorso[ruota], list):
                storico_ruota.append(concorso[ruota])
        
        if not storico_ruota:
            continue

        # 1. Calcolo Ambata Capogioco (basata sulla frequenza recente)
        storico_recente = storico_ruota[-FINESTRA_AMBATE:]
        conteggio_numeri = defaultdict(int)
        for cinquina in storico_recente:
            for num in cinquina:
                conteggio_numeri[num] += 1
                
        # Prendiamo il numero più frequente nel periodo recente
        ambata_principale = max(conteggio_numeri, key=conteggio_numeri.get)

        # 2. Calcolo Matrice di Co-occorrenza sull'intero storico ruota
        co_matrix = calcola_matrice_cooccorrenze(storico_ruota)

        # 3. Trova i migliori abbinamenti per formare gli Ambi
        abbinamenti = trova_abbinamenti_ambo(ambata_principale, co_matrix, top_n=2)

        # 4. Formattazione Previsioni
        ambi_generati = [[ambata_principale, abb] for abb in abbinamenti]
        lunghetta = [ambata_principale] + abbinamenti

        previsioni_per_ruota[ruota] = {
            "ambata": ambata_principale,
            "abbinamenti": abbinamenti,
            "ambi_consigliati": ambi_generati,
            "terzina_copertura": lunghetta,
            "statistiche": {
                "frequenza_ambata_recente": conteggio_numeri[ambata_principale],
                "co_occorrenze_ambo_1": int(co_matrix[ambata_principale][abbinamenti[0]]) if len(abbinamenti) > 0 else 0,
                "co_occorrenze_ambo_2": int(co_matrix[ambata_principale][abbinamenti[1]]) if len(abbinamenti) > 1 else 0
            }
        }

    return previsioni_per_ruota

def salvataggio_risultati(risultati, filepath):
    """Salva l'output finale in formato JSON."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(risultati, f, indent=4, ensure_ascii=False)
    print(f"✅ Previsioni salvate con successo in '{filepath}'")

def main():
    try:
        print("📂 Caricamento archivio estrazioni...")
        data = carica_estrazioni(FILE_ESTRAZIONI)
        
        # Gestisce sia il caso in cui il JSON sia una lista o un dizionario con chiave 'estrazioni'
        archivio = data.get('estrazioni', data) if isinstance(data, dict) else data

        print("🔮 Calcolo ambate e matrici di co-occorrenza per ambo...")
        risultati = {
            "ultimo_aggiornamento": archivio[-1].get("data", "N/D") if isinstance(archivio[-1], dict) else "N/D",
            "previsioni": elabora_previsioni(archivio)
        }

        print("💾 Salvataggio risultati...")
        salvataggio_risultati(risultati, FILE_OUTPUT)

    except Exception as e:
        print(f"❌ Errore durante l'esecuzione dello script: {e}")

if __name__ == "__main__":
    main()

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

def calcola_previsione_estrazione(estrazione, fisso):
    """Calcola Ambata, Ambo e Ambetti basandosi su un'estrazione specifica."""
    numeri_base = estrazione["ruote"].get(RUOTA_BASE, [])
    if not numeri_base:
        return None
    
    primo_estratto = numeri_base[0]
    ambata = fuori_90(primo_estratto + fisso)
    ambo_secco = calcola_diametrale(ambata)
    
    # Ambetti
    diam_piu_1 = fuori_90(ambo_secco + 1)
    diam_meno_1 = fuori_90(ambo_secco - 1)
    
    return {
        "ambata": ambata,
        "ambo": [ambata, ambo_secco],
        "ambetti": [[ambata, diam_piu_1], [ambata, diam_meno_1]],
        "tipo_calcolo": f"Sommativo da 1° {RUOTA_BASE.capitalize()} ({primo_estratto}) +{fisso}"
    }

def main():
    if not os.path.exists(FILE_ESTRAZIONI):
        print(f"Errore: {FILE_ESTRAZIONI} non trovato!")
        return

    with open(FILE_ESTRAZIONI, "r", encoding="utf-8") as f:
        estrazioni = json.load(f)

    tot_estrazioni = len(estrazioni)
    if tot_estrazioni == 0:
        return

    # 1. Calcola la previsione valida per l'ultimo concorso inserito
    ultima_estrazione = estrazioni[-1]
    info_concorso = {
        "numero": "Lotto Intelligence V8",
        "data": ultima_estrazione.get("data", "N/D")
    }
    
    previsione_attuale_base = calcola_previsione_estrazione(ultima_estrazione, FISSO_OTTIMIZZATO)
    
    previsioni_output = {}
    if previsione_attuale_base:
        previsioni_output[RUOTA_BASE] = previsione_attuale_base
        previsioni_output[RUOTA_RECUPERO] = previsione_attuale_base

    # 2. Generazione Automatica dello Storico Verificato (Avanzamento Colpi)
    storico_verificato = []
    
    # Analizziamo le ultime 10 estrazioni passate (esclusa l'ultima appena calcolata)
    # per vedere a che colpo sono arrivate rispetto alla fine dell'archivio attuale
    for indietro in range(1, 11):
        indice_calcolo = tot_estrazioni - 1 - indietro
        if indice_calcolo < 0:
            continue
            
        estrazione_calcolo = estrazioni[indice_calcolo]
        prev_passata = calcola_previsione_estrazione(estrazione_calcolo, FISSO_OTTIMIZZATO)
        if not prev_passata:
            continue
            
        ambata_target = prev_passata["ambata"]
        ambo_target = prev_passata["ambo"]
        
        colpo_corrente = 0
        stato = "In gioco"
        esito_colpo = ""
        
        # Verifichiamo i colpi successivi fino all'ultima estrazione disponibile nell'archivio
        massimi_colpi_disponibili = min(9, tot_estrazioni - 1 - indice_calcolo)
        
        for colpo in range(1, massimi_colpi_disponibles + 1):
            estrazione_verifica = estrazioni[indice_calcolo + colpo]
            num_b = estrazione_verifica["ruote"].get(RUOTA_BASE, [])
            num_r = estrazione_verifica["ruote"].get(RUOTA_RECUPERO, [])
            
            # Controllo Vincite
            ambo_b = ambo_target[0] in num_b and ambo_target[1] in num_b
            ambo_r = ambo_target[0] in num_r and ambo_target[1] in num_r
            
            ambata_b = ambata_target in num_b
            ambata_r = ambata_target in num_r
            
            if ambo_b or ambo_r:
                stato = "Ambo Vincente"
                esito_colpo = f"Esito al {colpo}° colpo"
                break
            elif ambata_b or ambata_r:
                stato = "Ambata Vincente"
                esito_colpo = f"Esito al {colpo}° colpo"
                break
                
        # Se dopo aver controllato le estrazioni successive non è uscito nulla ed è ancora nel ciclo di 9 colpi
        if stato == "In gioco":
            if massimi_colpi_disponibili < 9:
                colpo_corrente = massimi_colpi_disponibili + 1
                esito_colpo = f"{colpo_corrente}° Colpo"
            else:
                stato = "Finito Negativo"
                esito_colpo = "Fuori colpi"

        storico_verificato.append({
            "data": f"Conc. Arretrato -{indietro}",
            "ruote": f"{RUOTA_BASE} - {RUOTA_RECUPERO}",
            "ambata": ambata_target,
            "ambo": f"{ambo_target[0]} - {ambo_target[1]}",
            "colpi": esito_colpo,
            "stato": stato
        })

    # Compila la struttura finale compatibile con index.html
    struttura_finale = {
        "info_concorso": info_concorso,
        "previsioni": previsioni_output,
        "storico_verificato": storico_verificato
    }

    with open(FILE_RISULTATI, "w", encoding="utf-8") as f:
        json.dump(struttura_finale, f, indent=4, ensure_ascii=False)
        
    print(f"✅ File {FILE_RISULTATI} aggiornato con avanzamento automatico dei colpi!")

if __name__ == "__main__":
    main()

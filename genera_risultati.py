import json
import os
import re

# --- CONFIGURAZIONE REGINA ASSOLUTA V8 ---
FISSO_OTTIMIZZATO = 31
RUOTA_BASE_SIGLA = "TO"      
RUOTA_RECUPERO_SIGLA = "NA"   
RUOTA_BASE_NOME = "TORINO"
RUOTA_RECUPERO_NOME = "NAPOLI"

FILE_ESTRAZIONI = "estrazioni.json"
FILE_RISULTATI = "risultati_v4.json"

def fuori_90(numero):
    while numero > 90: numero -= 90
    while numero < 1: numero += 90
    return numero

def calcola_diametrale(numero):
    return numero + 45 if numero <= 45 else numero - 45

def analizza_file_estrazioni():
    """Legge l'archivio tabellare e organizza le estrazioni cronologicamente."""
    if not os.path.exists(FILE_ESTRAZIONI):
        print(f"❌ ERRORE: File {FILE_ESTRAZIONI} non trovato!")
        return []
        
    cronologia = {}
    with open(FILE_ESTRAZIONI, "r", encoding="utf-8") as f:
        for riga in f:
            riga = riga.strip()
            if not riga:
                continue
            parti = re.split(r'\t+|\s+', riga)
            if len(parti) < 7:
                continue
                
            data = parti[0]
            ruota = parti[1].upper()
            try:
                numeri = [int(x) for x in parti[2:7]]
            except ValueError:
                continue
                
            if data not in cronologia:
                cronologia[data] = {}
            cronologia[data][ruota] = numeri
            
    return [{"data": d, "ruote": cronologia[d]} for d in sorted(list(cronologia.keys()))]

def main():
    estrazioni = analizza_file_estrazioni()
    if not estrazioni or len(estrazioni) < 2:
        print("❌ Impossibile procedere: Dati insufficienti in estrazioni.json")
        return

    tot_estrazioni = len(estrazioni)
    ultima_estrazione = estrazioni[-1]
    data_attuale = ultima_estrazione["data"]
    
    # 1. CALCOLO MATEMATICO DINAMICO PREVISIONE NUOVA (1° COLPO)
    numeri_to_attuali = ultima_estrazione["ruote"].get(RUOTA_BASE_SIGLA, [])
    if not numeri_to_attuali:
        print(f"⚠️ Ruota {RUOTA_BASE_NOME} mancante nell'ultimo concorso. Prendo fallback grafico.")
        primo_estratto = 10
    else:
        primo_estratto = numeri_to_attuali[0]

    ambata_att = fuori_90(primo_estratto + FISSO_OTTIMIZZATO)
    ambo_att = calcola_diametrale(ambata_att)
    d_p1_att = fuori_90(ambo_att + 1)
    d_m1_att = fuori_90(ambo_att - 1)

    previsioni_output = {
        RUOTA_BASE_NOME: {
            "ambata": ambata_att,
            "ambo": [ambata_att, ambo_att],
            "ambetti": [[ambata_att, d_p1_att], [ambata_att, d_m1_att]]
        },
        RUOTA_RECUPERO_NOME: {
            "ambata": ambata_att,
            "ambo": [ambata_att, ambo_att],
            "ambetti": [[ambata_att, d_p1_att], [ambata_att, d_m1_att]]
        }
    }

    # 2. TRACKING AUTOMATICO DEI COLPI ARRETRATI (FASCIA D'ORO IN BASSO)
    storico_verificato = []
    
    # Scansioniamo a ritroso gli ultimi 10 concorsi per monitorare le vecchie previsioni
    for indietro in range(1, min(11, tot_estrazioni)):
        idx = tot_estrazioni - 1 - indietro
        if idx < 0:
            continue
            
        est_passata = estrazioni[idx]
        num_to_p = est_passata["ruote"].get(RUOTA_BASE_SIGLA, [])
        if not num_to_p:
            continue
            
        # Ricalcolo geometrico della vecchia previsione generata in quel concorso
        ambata_p = fuori_90(num_to_p[0] + FISSO_OTTIMIZZATO)
        ambo_p = calcola_diametrale(ambata_p)
        
        stato = "In gioco"
        esito_colpo = ""
        colpi_passati = tot_estrazioni - 1 - idx
        colpi_limite = min(9, colpi_passati)
        
        for colpo in range(1, colpi_limite + 1):
            est_v = estrazioni[idx + colpo]
            n_to = est_v["ruote"].get(RUOTA_BASE_SIGLA, [])
            n_na = est_v["ruote"].get(RUOTA_RECUPERO_SIGLA, [])
            
            if (ambata_p in n_to and ambo_p in n_to) or (ambata_p in n_na and ambo_p in n_na):
                stato = "Ambo Vincente"
                esito_colpo = f"Esito al {colpo}° colpo"
                break
            elif ambata_p in n_to or ambata_p in n_na:
                stato = "Ambata Vincente"
                esito_colpo = f"Esito al {colpo}° colpo"
                break
                
        if stato == "In gioco":
            if colpi_passati < 9:
                esito_colpo = f"{colpi_passati + 1}° Colpo"
            else:
                stato = "Finito Negativo"
                esito_colpo = "Fuori colpi"

        storico_verificato.append({
            "data": est_passata["data"],
            "ruote": f"{RUOTA_BASE_NOME} - {RUOTA_RECUPERO_NOME}",
            "ambata": ambata_p,
            "ambo": f"{ambata_p} - {ambo_p}",
            "colpi": esito_colpo,
            "stato": stato
        })

    # Generazione struttura finale pulita
    struttura_finale = {
        "info_concorso": {
            "numero": "Lotto Intelligence V8",
            "data": data_attuale
        },
        "previsioni": previsioni_output,
        "storico_verificato": storico_verificato
    }

    with open(FILE_RISULTATI, "w", encoding="utf-8") as f:
        json.dump(struttura_finale, f, indent=4, ensure_ascii=False)
        
    print(f"✅ Successo! Generato {FILE_RISULTATI} calcolando {tot_estrazioni} estrazioni.")

if __name__ == "__main__":
    main()

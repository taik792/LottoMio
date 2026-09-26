import json
import os

# --- CONFIGURAZIONE REGINA FASCIA D'ORO V8 ---
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
    """Legge il file tabellare e organizza le estrazioni in ordine cronologico."""
    if not os.path.exists(FILE_ESTRAZIONI):
        return []
        
    cronologia = {}
    with open(FILE_ESTRAZIONI, "r", encoding="utf-8") as f:
        for riga in f:
            riga = riga.strip()
            if not riga:
                continue
            parti = riga.split("\t")
            if len(parti) < 7:
                continue
                
            data = parti[0]
            ruota = parti[1]
            try:
                numeri = [int(x) for x in parti[2:7]]
            except ValueError:
                continue
                
            if data not in cronologia:
                cronologia[data] = {}
            cronologia[data][ruota] = numeri
            
    date_ordinate = sorted(list(cronologia.keys()))
    return [ {"data": d, "ruote": cronologia[d]} for d in date_ordinate ]

def main():
    estrazioni = analizza_file_estrazioni()
    if not estrazioni:
        print(f"Errore: Nessun dato valido trovato in {FILE_ESTRAZIONI}")
        return

    tot_estrazioni = len(estrazioni)
    print(f"Archivio caricato con successo. Concorsi totali: {tot_estrazioni}")

    # ======================================================================
    # 1. CALCOLO PREVISIONE ATTUALE (Valida dal concorso dell'ultima riga)
    # ======================================================================
    ultima_estrazione = estrazioni[-1]
    data_attuale = ultima_estrazione["data"]
    
    numeri_torino_attuali = ultima_estrazione["ruote"].get(RUOTA_BASE_SIGLA, [])
    if not numeri_torino_attuali:
        print(f"Errore critico: Dati {RUOTA_BASE_NOME} mancanti nell'ultimo concorso.")
        return
        
    primo_estratto_attuale = numeri_torino_attuali[0]
    ambata_attuale = fuori_90(primo_estratto_attuale + FISSO_OTTIMIZZATO)
    ambo_attuale = calcola_diametrale(ambata_attuale)
    diam_piu_1_att = fuori_90(ambo_attuale + 1)
    diam_meno_1_att = fuori_90(ambo_attuale - 1)

    previsioni_output = {
        RUOTA_BASE_NOME: {
            "ambata": ambata_attuale,
            "ambo": [ambata_attuale, ambo_attuale],
            "ambetti": [[ambata_attuale, diam_piu_1_att], [ambata_attuale, diam_meno_1_att]]
        },
        RUOTA_RECUPERO_NOME: {
            "ambata": ambata_attuale,
            "ambo": [ambata_attuale, ambo_attuale],
            "ambetti": [[ambata_attuale, diam_piu_1_att], [ambata_attuale, diam_meno_1_att]]
        }
    }

    # ======================================================================
    # 2. CALCOLO AUTOMATICO DELLO STORICO (Avanzamento Colpi Reale)
    # ======================================================================
    storico_verificato = []
    
    # Scansioniamo a ritroso le estrazioni passate partendo dalla penultima (indietro = 1)
    for indietro in range(1, 11):
        indice_calcolo = tot_estrazioni - 1 - indietro
        if indice_calcolo < 0:
            continue
            
        estrazione_calcolo = estrazioni[indice_calcolo]
        data_calcolo = estrazione_calcolo["data"]
        
        num_to_passato = estrazione_calcolo["ruote"].get(RUOTA_BASE_SIGLA, [])
        if not num_to_passato:
            continue
            
        # Ricalcoliamo matematicamente cosa era stato previsto in quel concorso passato
        ambata_passata = fuori_90(num_to_passato[0] + FISSO_OTTIMIZZATO)
        ambo_passato = calcola_diametrale(ambata_passata)
        
        stato = "In gioco"
        esito_colpo = ""
        
        # Quante estrazioni ci sono state tra il momento del calcolo e la fine dell'archivio?
        colpi_esaminabili = tot_estrazioni - 1 - indice_calcolo
        colpi_effettivi = min(9, colpi_esaminabili)
        
        # Controlliamo gli esiti concorso per concorso nei colpi successivi
        for colpo in range(1, colpi_effettivi + 1):
            estrazione_verifica = estrazioni[indice_calcolo + colpo]
            n_to = estrazione_verifica["ruote"].get(RUOTA_BASE_SIGLA, [])
            n_na = estrazione_verifica["ruote"].get(RUOTA_RECUPERO_SIGLA, [])
            
            # Controllo Vincita Ambo Secco
            ambo_vinto_to = (ambata_passata in n_to) and (ambo_passato in n_to)
            ambo_vinto_na = (ambata_passata in n_na) and (ambo_passato in n_na)
            
            # Controllo Vincita Ambata
            ambata_vinta_to = ambata_passata in n_to
            ambata_vinta_na = ambata_passata in n_na
            
            if ambo_vinto_to or ambo_vinto_na:
                stato = "Ambo Vincente"
                esito_colpo = f"Esito al {colpo}° colpo"
                break
            elif ambata_vinta_to or ambata_vinta_na:
                stato = "Ambata Vincente"
                esito_colpo = f"Esito al {colpo}° colpo"
                break
                
        if stato == "In gioco":
            if colpi_esaminabili < 9:
                # Il calcolo del colpo corrente ora dipende SOLO da quanti concorsi veri sono passati
                esito_colpo = f"{colpi_esaminabili + 1}° Colpo"
            else:
                stato = "Finito Negativo"
                esito_colpo = "Fuori colpi"

        storico_verificato.append({
            "data": data_calcolo,
            "ruote": f"{RUOTA_BASE_NOME} - {RUOTA_RECUPERO_NOME}",
            "ambata": ambata_passata,
            "ambo": f"{ambata_passata} - {ambo_passato}",
            "colpi": esito_colpo,
            "stato": stato
        })

    # Compilazione finale
    struttura_finale = {
        "info_concorso": {
            "numero": "Lotto Intelligence V8",
            "data": data_attuale
        },
        "previsioni": invece_se_vuoi_isolare_le_ruote_dinamicamente(previsioni_output),
        "storico_verificato": storico_verificato
    }

    def invece_se_vuoi_isolare_le_ruote_dinamicamente(p):
        return p

    with open(FILE_RISULTATI, "w", encoding="utf-8") as f:
        json.dump(struttura_finale, f, indent=4, ensure_ascii=False)
        
    print(f"✅ File {FILE_RISULTATI} ricostruito integralmente basandosi sull'archivio storico!")

if __name__ == "__main__":
    main()

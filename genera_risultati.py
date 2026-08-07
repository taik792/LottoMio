import json
import os
from datetime import datetime

def fuori_90(numero):
    while numero > 90: numero -= 90
    while numero <= 0: numero += 90
    return numero

def calcola_diametrale(numero):
    if numero <= 45: return numero + 45
    return numero - 45

def elabora_motore_sommativo():
    if not os.path.exists('estrazioni.json'): return

    FISSO_OTTIMIZZATO = 25 

    with open('estrazioni.json', 'r', encoding='utf-8') as f:
        archivio = json.load(f)

    # Standardizzazione delle ruote in maiuscolo
    archivio_pulito = {k.upper(): v for k, v in archivio.items() if isinstance(v, list)}

    # Controllo presenza della ruota base Cagliari
    if "CAGLIARI" not in archivio_pulito or len(archivio_pulito["CAGLIARI"]) == 0: return
    
    lista_cagliari = archivio_pulito["CAGLIARI"]
    lista_palermo = archivio_pulito.get("PALERMO", [])
    tot_estrazioni = len(lista_cagliari)

    # Identifica la data dell'ultimo concorso inserito
    data_reale = datetime.now().strftime("%d/%m/%Y")
    if "info_concorso" in archivio and "data" in archivio["info_concorso"]:
        data_reale = archivio["info_concorso"]["data"]
    elif "data" in archivio:
        data_reale = archivio["data"]

    risultati_finali = {
        "info_concorso": {"numero": "Lotto Intelligence V8", "data": data_reale},
        "previsioni": {},
        "storico_verificato": []
    }

    # 1. Elaborazione della PREVISIONE CORRENTE (Ultima estrazione) da 1° CAGLIARI
    ultima_estrazione_cagliari = lista_cagliari[-1]
    if isinstance(ultima_estrazione_cagliari, list) and len(ultima_estrazione_cagliari) >= 1:
        try:
            primo_cagliari = int(ultima_estrazione_cagliari[0])
            ambata = fuori_90(primo_cagliari + FISSO_OTTIMIZZATO)
            abbinamento = calcola_diametrale(ambata)
            ambo_secco = [ambata, abbinamento]
            ambetti = [
                [ambata, fuori_90(abbinamento + 1)],
                [ambata, fuori_90(abbinamento - 1)]
            ]
            
            for ruota_chiave in ["CAGLIARI", "PALERMO"]:
                if ruota_chiave in archivio_pulito and len(archivio_pulito[ruota_chiave]) > 0:
                    risultati_finali["previsioni"][ruota_chiave] = {
                        "numeri_estrazione": [int(n) for n in archivio_pulito[ruota_chiave][-1][:5]],
                        "tipo_calcolo": f"Sommativo da 1° Cagliari ({primo_cagliari}) +{FISSO_OTTIMIZZATO}",
                        "ambata": ambata,
                        "ambo": ambo_secco,
                        "ambetti": ambetti
                    }
        except (ValueError, IndexError):
            pass

    # 2. RICOSTRUZIONE AUTOMATICA DELLO STORICO (Verifica su Cagliari e Palermo)
    limite_storico = max(0, tot_estrazioni - 11)
    
    for i in range(tot_estrazioni - 2, limite_storico - 1, -1):
        if i < 0: break
        
        estrazione_ca = lista_cagliari[i]
        if not isinstance(estrazione_ca, list) or len(estrazione_ca) < 1: continue
        
        try:
            p_cagliari = int(estrazione_ca[0])
            ambata_p = fuori_90(p_cagliari + FISSO_OTTIMIZZATO)
            abbinamento_p = calcola_diametrale(ambata_p)
            ambo_p = [ambata_p, abbinamento_p]
            
            colpi_passati = (tot_estrazioni - 1) - i
            
            esito = "In gioco"
            colpo_vincita = None
            
            # Scansione dei colpi successivi su Cagliari e Palermo
            for c in range(1, colpi_passati + 1):
                curr_idx = i + c
                if curr_idx >= tot_estrazioni: break
                
                ca_nums = [int(n) for n in lista_cagliari[curr_idx][:5]]
                pa_nums = [int(n) for n in lista_palermo[curr_idx][:5]] if curr_idx < len(lista_palermo) else []
                
                if (ambata_p in ca_nums and abbinamento_p in ca_nums) or (ambata_p in pa_nums and abbinamento_p in pa_nums):
                    esito = "AMBO SECCO VINCENTE!"
                    colpo_vincita = c
                    break
                elif (ambata_p in ca_nums) or (ambata_p in pa_nums):
                    if esito == "In gioco":
                        esito = "Ambata Vincente"
                        colpo_vincita = c
            
            if esito == "In gioco" and colpi_passati > 9:
                esito = "Ciclo concluso (No esito)"
            
            data_label = f"Concorso Arretrat. -{colpi_passati}"
            
            risultati_finali["storico_verificato"].append({
                "data": data_label,
                "ambata": ambata_p,
                "ambo": f"{ambata_p} - {abbinamento_p}",
                "colpi": f"{colpi_passati}° Colpo" if esito == "In gioco" else f"Esito al {colpo_vincita}° colpo" if colpo_vincita else "Chiuso",
                "stato": esito
            })
        except (ValueError, IndexError):
            pass

    with open('risultati_v4.json', 'w', encoding='utf-8') as f:
        json.dump(risultati_finali, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    elabora_motore_sommativo()

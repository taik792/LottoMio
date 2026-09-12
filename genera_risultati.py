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

    # 🎯 CONFIGURAZIONE MOTORE ATTUALE
    FISSO_OTTIMIZZATO = 10 
    RUOTA_BASE = "FIRENZE"
    RUOTA_RECUPERO = "MILANO"

    with open('estrazioni.json', 'r', encoding='utf-8') as f:
        archivio = json.load(f)

    data_reale = None
    if "info_concorso" in archivio and "data" in archivio["info_concorso"]:
        data_reale = archivio["info_concorso"]["data"]
    elif "data" in archivio:
        data_reale = archivio["data"]
        
    if not data_reale:
        data_reale = datetime.now().strftime("%d/%m/%Y")

    storico_previsioni = []
    file_storico = 'storico_cronologico_mi_ve.json'
    if os.path.exists(file_storico):
        with open(file_storico, 'r', encoding='utf-8') as sf:
            try: storico_previsioni = json.load(sf)
            except: storico_previsioni = []

    risultati_finali = {
        "info_concorso": {"numero": "Lotto Intelligence V8", "data": data_reale},
        "previsioni": {},
        "storico_verificato": []
    }

    archivio_pulito = {k.upper(): v for k, v in archivio.items() if isinstance(v, list)}

    if RUOTA_BASE in archivio_pulito and len(archivio_pulito[RUOTA_BASE]) > 0:
        lista_base = archivio_pulito[RUOTA_BASE]
        lista_recupero = archivio_pulito.get(RUOTA_RECUPERO, [])
        ultima_estrazione_base = lista_base[-1]
        
        if isinstance(ultima_estrazione_base, list) and len(ultima_estrazione_base) >= 1:
            try:
                primo_base = int(ultima_estrazione_base[0])
                ambata = fuori_90(primo_base + FISSO_OTTIMIZZATO)
                abbinamento = calcola_diametrale(ambata)
                ambo_secco = [ambata, abbinamento]
                ambetti = [
                    [ambata, fuori_90(abbinamento + 1)],
                    [ambata, fuori_90(abbinamento - 1)]
                ]
                
                if not any(x['data'] == data_reale for x in storico_previsioni):
                    storico_previsioni.append({
                        "data": data_reale,
                        "primo_base": primo_base,
                        "ambata": ambata,
                        "ambo": ambo_secco,
                        "ambetti": ambetti,
                        "indice_archivio": len(lista_base) - 1
                    })
                    with open(file_storico, 'w', encoding='utf-8') as sf:
                        json.dump(storico_previsioni, sf, indent=4, ensure_ascii=False)

                for ruota_chiave in [RUOTA_BASE, RUOTA_RECUPERO]:
                    if ruota_chiave in archivio_pulito and len(archivio_pulito[ruota_chiave]) > 0:
                        risultati_finali["previsioni"][ruota_chiave] = {
                            "numeri_estrazione": [int(n) for n in archivio_pulito[ruota_chiave][-1][:5]],
                            "tipo_calcolo": f"Sommativo da 1° {RUOTA_BASE.capitalize()} ({primo_base}) +{FISSO_OTTIMIZZATO}",
                            "ambata": ambata,
                            "ambo": ambo_secco,
                            "ambetti": ambetti
                        }

                tot_estrazioni = len(lista_base)
                limite_storico = max(0, tot_estrazioni - 11)
                
                for i in range(tot_estrazioni - 2, limite_storico - 1, -1):
                    if i < 0: break
                    estrazione_b = lista_base[i]
                    if not isinstance(estrazione_b, list) or len(estrazione_b) < 1: continue
                    
                    try:
                        p_base = int(estrazione_b[0])
                        ambata_p = fuori_90(p_base + FISSO_OTTIMIZZATO)
                        abbinamento_p = calcola_diametrale(ambata_p)
                        ambo_p = [ambata_p, abbinamento_p]
                        
                        colpi_passati = (tot_estrazioni - 1) - i
                        esito = "In gioco"
                        colpo_vincita = None
                        
                        for c in range(1, colpi_passati + 1):
                            curr_idx = i + c
                            if curr_idx >= tot_estrazioni: break
                            
                            ba_nums = [int(n) for n in lista_base[curr_idx][:5]]
                            mi_nums = [int(n) for n in lista_recupero[curr_idx][:5]] if curr_idx < len(lista_recupero) else []
                            
                            if (ambata_p in ba_nums and abbinamento_p in ba_nums) or (ambata_p in mi_nums and abbinamento_p in mi_nums):
                                esito = "AMBO SECCO VINCENTE!"
                                colpo_vincita = c
                                break
                            elif (ambata_p in ba_nums) or (ambata_p in mi_nums):
                                if esito == "In gioco":
                                    esito = "Ambata Vincente"
                                    colpo_vincita = c

                        if esito == "In gioco" and colpi_passati > 9:
                            esito = "Ciclo concluso (No esito)"
                        
                        data_label = f"Concorso Arretrat. -{colpi_passati}"
                        
                        risultati_finali["storico_verificato"].append({
                            "data": data_label,
                            "ruote": f"{RUOTA_BASE} - {RUOTA_RECUPERO}",
                            "ambata": ambata_p,
                            "ambo": f"{ambata_p} - {abbinamento_p}",
                            "colpi": f"{colpi_passati}° Colpo" if esito == "In gioco" else f"Esito al {colpo_vincita}° colpo" if colpo_vincita else "Chiuso",
                            "stato": esito
                        })
                    except:
                        continue

            except (ValueError, IndexError):
                pass

    with open('risultati_v4.json', 'w', encoding='utf-8') as f:
        json.dump(risultati_finali, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    elabora_motore_sommativo()

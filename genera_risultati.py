import json
import os
from datetime import datetime

RUOTE = ["BARI", "CAGLIARI", "FIRENZE", "GENOVA", "MILANO", "NAPOLI", "PALERMO", "ROMA", "TORINO", "VENEZIA"]

def fuori_90(n):
    while n > 90: n -= 90
    while n <= 0: n += 90
    return n

def trova_miglior_setup(archivio_pulito, limite_estrazioni=40, max_colpi=6):
    tot_estrazioni = len(archivio_pulito.get("BARI", []))
    if tot_estrazioni < limite_estrazioni + max_colpi:
        limite_estrazioni = tot_estrazioni - max_colpi

    start_idx = tot_estrazioni - max_colpi - limite_estrazioni
    end_idx = tot_estrazioni - max_colpi

    miglior_score = -1
    miglior_setup = None

    # Scansione automatica Ruota Spia e Ruote di Giocata
    for r_spia in RUOTE:
        if r_spia not in archivio_pulito: continue
        dati_spia = archivio_pulito[r_spia]

        for i_r1 in range(len(RUOTE)):
            for i_r2 in range(i_r1 + 1, len(RUOTE)):
                r1, r2 = RUOTE[i_r1], RUOTE[i_r2]
                if r1 not in archivio_pulito or r2 not in archivio_pulito: continue
                
                dati_r1, dati_r2 = archivio_pulito[r1], archivio_pulito[r2]

                # Scansione completa di tutti i fissi da 1 a 90
                for f_amb in range(1, 91):
                    for f_abb in range(1, 91):
                        if f_amb == f_abb: continue

                        ambi_vinti = 0
                        for i in range(start_idx, end_idx):
                            try:
                                primo_spia = int(dati_spia[i][0])
                                n_amb = fuori_90(primo_spia + f_amb)
                                n_abb = fuori_90(primo_spia + f_abb)

                                for colpo in range(1, max_colpi + 1):
                                    idx_c = i + colpo
                                    nums_r1 = [int(x) for x in dati_r1[idx_c][:5]]
                                    nums_r2 = [int(x) for x in dati_r2[idx_c][:5]]

                                    if (n_amb in nums_r1 and n_abb in nums_r1) or (n_amb in nums_r2 and n_abb in nums_r2):
                                        ambi_vinti += 1
                                        break
                            except (ValueError, IndexError):
                                continue

                        if ambi_vinti > miglior_score:
                            miglior_score = ambi_vinti
                            miglior_setup = {
                                "ruota_spia": r_spia, "ruota_1": r1, "ruota_2": r2,
                                "fisso_ambata": f_amb, "fisso_abbinamento": f_abb,
                                "ambi": ambi_vinti
                            }
    return miglior_setup

def elabora_motore_dinamico():
    if not os.path.exists('estrazioni.json'): return

    with open('estrazioni.json', 'r', encoding='utf-8') as f:
        archivio = json.load(f)

    archivio_pulito = {k.upper(): v for k, v in archivio.items() if isinstance(v, list)}
    
    # 1. Trova il miglior setup attuale
    setup = trova_miglior_setup(archivio_pulito)
    if not setup: return
    
    r_spia = setup["ruota_spia"]
    r1, r2 = setup["ruota_1"], setup["ruota_2"]
    f_amb, f_abb = setup["fisso_ambata"], setup["fisso_abbinamento"]
    
    lista_spia = archivio_pulito[r_spia]
    lista_r1 = archivio_pulito[r1]
    lista_r2 = archivio_pulito[r2]
    tot_estrazioni = len(lista_spia)

    data_reale = datetime.now().strftime("%d/%m/%Y")
    if "info_concorso" in archivio and "data" in archivio["info_concorso"]:
        data_reale = archivio["info_concorso"]["data"]

    risultati_finali = {
        "info_concorso": {"numero": "Lotto Intelligence V9.0 (Dinamico)", "data": data_reale},
        "previsioni": {},
        "storico_verificato": []
    }

    # 2. Calcolo Previsione Corrente
    ultima_spia = lista_spia[-1]
    if isinstance(ultima_spia, list) and len(ultima_spia) >= 1:
        try:
            primo_spia = int(ultima_spia[0])
            ambata = fuori_90(primo_spia + f_amb)
            abbinamento = fuori_90(primo_spia + f_abb)
            ambo_secco = [ambata, abbinamento]
            ambetti = [[ambata, fuori_90(abbinamento + 1)], [ambata, fuori_90(abbinamento - 1)]]
            
            for r_target in [r1, r2]:
                risultati_finali["previsioni"][r_target] = {
                    "numeri_estrazione": [int(n) for n in archivio_pulito[r_target][-1][:5]],
                    "tipo_calcolo": f"Dinamico: 1° {r_spia} ({primo_spia}) +{f_amb} / +{f_abb}",
                    "ambata": ambata,
                    "ambo": ambo_secco,
                    "ambetti": ambetti
                }
        except (ValueError, IndexError): pass

    # 3. Verifica Storico Retrospezione
    limite_storico = max(0, tot_estrazioni - 11)
    for i in range(tot_estrazioni - 2, limite_storico - 1, -1):
        if i < 0: break
        try:
            p_spia = int(lista_spia[i][0])
            amb_p = fuori_90(p_spia + f_amb)
            abb_p = fuori_90(p_spia + f_abb)
            colpi_passati = (tot_estrazioni - 1) - i
            
            esito = "In gioco"
            colpo_vincita = None
            
            for c in range(1, colpi_passati + 1):
                curr_idx = i + c
                if curr_idx >= tot_estrazioni: break
                
                nums1 = [int(n) for n in lista_r1[curr_idx][:5]]
                nums2 = [int(n) for n in lista_r2[curr_idx][:5]]
                
                if (amb_p in nums1 and abb_p in nums1) or (amb_p in nums2 and abb_p in nums2):
                    esito = "AMBO SECCO VINCENTE!"
                    colpo_vincita = c
                    break
                elif (amb_p in nums1) or (amb_p in nums2):
                    if esito == "In gioco":
                        esito = "Ambata Vincente"
                        colpo_vincita = c
            
            if esito == "In gioco" and colpi_passati > 6: esito = "Ciclo concluso (No esito)"
            
            risultati_finali["storico_verificato"].append({
                "data": f"Concorso Arretrat. -{colpi_passati}",
                "ambata": amb_p,
                "ambo": f"{amb_p} - {abb_p}",
                "colpi": f"{colpi_passati}° Colpo" if esito == "In gioco" else f"Esito al {colpo_vincita}° colpo" if colpo_vincita else "Chiuso",
                "stato": esito
            })
        except (ValueError, IndexError): pass

    with open('risultati_v4.json', 'w', encoding='utf-8') as f:
        json.dump(risultati_finali, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    elabora_motore_dinamico()

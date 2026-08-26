import json
import os
from datetime import datetime

RUOTE = ["BARI", "CAGLIARI", "FIRENZE", "GENOVA", "MILANO", "NAPOLI", "PALERMO", "ROMA", "TORINO", "VENEZIA"]

def fuori_90(n):
    while n > 90: n -= 90
    while n <= 0: n += 90
    return n

def trova_miglior_setup(archivio_pulito, limite_estrazioni=25, max_colpi=6):
    tot_estrazioni = len(archivio_pulito.get("BARI", []))
    if tot_estrazioni < limite_estrazioni + max_colpi:
        limite_estrazioni = tot_estrazioni - max_colpi

    start_idx = tot_estrazioni - max_colpi - limite_estrazioni
    end_idx = tot_estrazioni - max_colpi

    miglior_score = -1
    miglior_setup = None

    for r_spia in RUOTE:
        if r_spia not in archivio_pulito: continue
        dati_spia = archivio_pulito[r_spia]

        for i_r1 in range(len(RUOTE)):
            for i_r2 in range(i_r1 + 1, len(RUOTE)):
                r1, r2 = RUOTE[i_r1], RUOTE[i_r2]
                if r1 not in archivio_pulito or r2 not in archivio_pulito: continue
                
                dati_r1, dati_r2 = archivio_pulito[r1], archivio_pulito[r2]

                for f_amb in range(1, 91, 2):
                    for f_abb in range(1, 91, 1):
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
    tot_estrazioni = len(archivio_pulito.get("BARI", []))

    # Controllo se c'è una giocata attiva salvata nel file della memoria
    setup_attivo = None
    if os.path.exists('giocata_attiva.json'):
        try:
            with open('giocata_attiva.json', 'r', encoding='utf-8') as f:
                dati_attivi = json.load(f)
                estrazione_inizio = dati_attivi.get("estrazione_inizio", 0)
                colpi_trascorsi = tot_estrazioni - estrazione_inizio
                
                # Se la giocata ha meno di 6 colpi ed è valida, la manteniamo attiva!
                if 0 <= colpi_trascorsi <= 6 and not dati_attivi.get("chiusa", False):
                    setup_attivo = dati_attivi.get("setup")
        except Exception:
            setup_attivo = None

    # Se non c'è una giocata attiva (o la precedente si è chiusa), calcola un nuovo setup ottimale
    if not setup_attivo:
        setup_attivo = trova_miglior_setup(archivio_pulito)
        if setup_attivo:
            with open('giocata_attiva.json', 'w', encoding='utf-8') as f:
                json.dump({"estrazione_inizio": tot_estrazioni - 1, "setup": setup_attivo, "chiusa": False}, f, indent=4)

    if not setup_attivo: return
    
    r_spia = setup_attivo["ruota_spia"]
    r1, r2 = setup_attivo["ruota_1"], setup_attivo["ruota_2"]
    f_amb, f_abb = setup_attivo["fisso_ambata"], setup_attivo["fisso_abbinamento"]
    
    lista_spia = archivio_pulito[r_spia]
    lista_r1 = archivio_pulito[r1]
    lista_r2 = archivio_pulito[r2]

    data_reale = datetime.now().strftime("%d/%m/%Y")
    if "info_concorso" in archivio and "data" in archivio["info_concorso"]:
        data_reale = archivio["info_concorso"]["data"]

    risultati_finali = {
        "info_concorso": {"numero": "Lotto Intelligence V9.0 (Dinamico)", "data": data_reale},
        "previsioni": {},
        "storico_verificato": []
    }

    # 2. Previsione Corrente
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
            
            # Se la giocata attiva ha vinto o ha finito i 6 colpi, segna come da resettare al prossimo giro
            if i == tot_estrazioni - 2 and (esito != "In gioco" or colpi_passati >= 6):
                if os.path.exists('giocata_attiva.json'):
                    try:
                        with open('giocata_attiva.json', 'w', encoding='utf-8') as f:
                            json.dump({"estrazione_inizio": 0, "setup": None, "chiusa": True}, f)
                    except Exception: pass

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

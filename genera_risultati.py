import json
import os
from datetime import datetime

def fuori_90(numero):
    while numero > 90: numero -= 90
    while numero <= 0: numero += 90
    return numero

def calcola_abbinamento_91(numero):
    # Opzione B: Complemento a 91 (Simmetrico)
    return fuori_90(91 - numero)

def calcola_vertibile(numero):
    # Calcolo matematico del vertibile con fuori 90 automatico
    if numero % 10 == 0: 
        res = numero // 10
    else:
        str_num = str(numero).zfill(2)
        if str_num[0] == str_num[1]: 
            res = numero + 9  # Gemelli (es. 77 -> 86)
        else:
            res = int(str_num[1] + str_num[0])
            
    return fuori_90(res) # Garantisce che il risultato sia SEMPRE tra 1 e 90

def elabora_motore_sommativo():
    if not os.path.exists('estrazioni.json'): 
        return

    FISSO_OTTIMIZZATO = 25 

    with open('estrazioni.json', 'r', encoding='utf-8') as f:
        archivio = json.load(f)

    archivio_pulito = {k.upper(): v for k, v in archivio.items() if isinstance(v, list)}

    if "BARI" not in archivio_pulito or len(archivio_pulito["BARI"]) == 0: 
        return
    
    lista_bari = archivio_pulito["BARI"]
    lista_napoli = archivio_pulito.get("NAPOLI", []) # Passati a NAPOLI
    tot_estrazioni = len(lista_bari)

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

    # 1. PREVISIONE CORRENTE (BARI - NAPOLI)
    ultima_estrazione_bari = lista_bari[-1]
    if isinstance(ultima_estrazione_bari, list) and len(ultima_estrazione_bari) >= 1:
        try:
            primo_bari = int(ultima_estrazione_bari[0])
            ambata = fuori_90(primo_bari + FISSO_OTTIMIZZATO)
            
            abb_91 = calcola_abbinamento_91(ambata)
            vert_ambata = calcola_vertibile(ambata)
            
            ambo_secco_principale = [ambata, abb_91]
            ambi_secondari = [
                [ambata, vert_ambata],
                [abb_91, vert_ambata]
            ]
            
            # Generazione previsione sia per BARI che per NAPOLI
            for ruota_chiave in ["BARI", "NAPOLI"]:
                if ruota_chiave in archivio_pulito and len(archivio_pulito[ruota_chiave]) > 0:
                    risultati_finali["previsioni"][ruota_chiave] = {
                        "numeri_estrazione": [int(n) for n in archivio_pulito[ruota_chiave][-1][:5]],
                        "tipo_calcolo": f"Sommativo da 1° Bari ({primo_bari}) +{FISSO_OTTIMIZZATO}",
                        "ambata": ambata,
                        "ambo": ambo_secco_principale,
                        "ambetti": ambi_secondari
                    }
        except (ValueError, IndexError):
            pass

    # 2. RICOSTRUZIONE STORICO (VERIFICA SU BARI E NAPOLI)
    limite_storico = max(0, tot_estrazioni - 11)
    
    for i in range(tot_estrazioni - 2, limite_storico - 1, -1):
        if i < 0: break
        
        estrazione_b = lista_bari[i]
        if not isinstance(estrazione_b, list) or len(estrazione_b) < 1: 
            continue
        
        try:
            p_bari = int(estrazione_b[0])
            ambata_p = fuori_90(p_bari + FISSO_OTTIMIZZATO)
            abb_91_p = calcola_abbinamento_91(ambata_p)
            vert_p = calcola_vertibile(ambata_p)
            
            colpi_passati = (tot_estrazioni - 1) - i
            esito = "In gioco"
            colpo_vincita = None
            
            for c in range(1, colpi_passati + 1):
                curr_idx = i + c
                if curr_idx >= tot_estrazioni: 
                    break
                
                ba_nums = [int(n) for n in lista_bari[curr_idx][:5]]
                # Controllo sulla ruota di NAPOLI
                na_nums = [int(n) for n in lista_napoli[curr_idx][:5]] if curr_idx < len(lista_napoli) else []
                
                # Controllo vincite su BARI o NAPOLI
                if (ambata_p in ba_nums and abb_91_p in ba_nums) or (ambata_p in na_nums and abb_91_p in na_nums):
                    esito = "AMBO SECCO VINCENTE! (Base 91)"
                    colpo_vincita = c
                    break
                elif (ambata_p in ba_nums and vert_p in ba_nums) or (ambata_p in na_nums and vert_p in na_nums):
                    esito = "AMBO VINCENTE! (Vertibile)"
                    colpo_vincita = c
                    break
                elif (abb_91_p in ba_nums and vert_p in ba_nums) or (abb_91_p in na_nums and vert_p in na_nums):
                    esito = "AMBO VINCENTE! (Simmetrico/Vert)"
                    colpo_vincita = c
                    break
                elif (ambata_p in ba_nums) or (ambata_p in na_nums):
                    if esito == "In gioco":
                        esito = "Ambata Vincente"
                        colpo_vincita = c
            
            if esito == "In gioco" and colpi_passati > 9:
                esito = "Ciclo concluso (No esito)"
            
            data_label = f"Concorso Arretrat. -{colpi_passati}"
            
            # Etichetta corretta: BARI - NAPOLI
            risultati_finali["storico_verificato"].append({
                "data": data_label,
                "ambata": ambata_p,
                "ambo": f"{ambata_p} - {abb_91_p} | Vert: {vert_p}",
                "colpi": f"{colpi_passati}° Colpo" if esito == "In gioco" else f"Esito al {colpo_vincita}° colpo" if colpo_vincita else "Chiuso",
                "stato": esito
            })
        except (ValueError, IndexError):
            pass

    with open('risultati_v4.json', 'w', encoding='utf-8') as f:
        json.dump(risultati_finali, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    elabora_motore_sommativo()

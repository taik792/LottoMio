import json
import os
from itertools import permutations

FISSO = 31

def fuori_90(numero):
    while numero > 90: numero -= 90
    while numero <= 0: numero += 90
    return numero

def esegui_backtest():
    if not os.path.exists('estrazioni.json'):
        print("Errore: estrazioni.json non trovato nella cartella corrente!")
        return

    with open('estrazioni.json', 'r', encoding='utf-8') as f:
        archivio = json.load(f)

    # Prendiamo tutte le ruote disponibili nel tuo file
    elenco_ruote = list(archivio.keys())
    print(f"Analisi avviata su {len(elenco_ruote)} ruote trovate nell'archivio...")
    
    classifica_coppie = []

    # Generiamo tutte le combinazioni possibili di Coppie (Ruota Base + Ruota Recupero)
    tutte_le_coppie = list(permutations(elenco_ruote, 2))

    for r_base, r_recupero in tutte_le_coppie:
        estrazioni_base = archivio[r_base]
        estrazioni_recupero = archivio[r_recupero]
        
        # Troviamo la lunghezza minima per evitare errori di disallineamento
        totale_concorsi = min(len(estrazioni_base), len(estrazioni_recupero))
        
        vincite_fascia_oro = 0  # Vincite dal 2° al 5° colpo
        vincite_primo_colpo = 0 # Vincite al 1° colpo (fase studio)
        fallimenti = 0          # Non esce entro il 5° colpo
        totale_giocate = 0

        # Analizziamo la storia lasciando un margine finale di 5 concorsi per l'esito
        for i in range(0, totale_concorsi - 5):
            totale_giocate += 1
            
            # Calcolo Ambata sul primo estratto della ruota base di quel concorso passato
            try:
                cinquina_passata = estrazioni_base[i]
                primo_estratto = cinquina_passata[0] if isinstance(cinquina_passata, list) else int(cinquina_passata)
            except:
                continue

            ambata = fuori_90(primo_estratto + FISSO)
            
            # Verifichiamo l'esito nei 5 concorsi successivi
            sfaldato = False
            for colpo in range(1, 6): # Colpi da 1 a 5
                indice_controllo = i + colpo
                
                cinquina_c_base = estrazioni_base[indice_controllo]
                cinquina_c_rec = estrazioni_recupero[indice_controllo]
                
                # Estraiamo i numeri estratti in quel colpo di controllo
                numeri_base = cinquina_c_base if isinstance(cinquina_c_base, list) else [cinquina_c_base]
                numeri_rec = cinquina_c_rec if isinstance(cinquina_c_rec, list) else [cinquina_c_rec]

                if ambata in numeri_base or ambata in numeri_rec:
                    sfaldato = True
                    if colpo == 1:
                        vincite_primo_colpo += 1
                    elif colpo >= 2 and colpo <= 5:
                        vincite_fascia_oro += 1
                    break
            
            if not sfaldato:
                fallimenti += 1

        if totale_giocate > 0:
            percentuale_oro = (vincite_fascia_oro / totale_giocate) * 100
            classifica_coppie.append({
                "coppia": f"{r_base.upper()} (Base) + {r_recupero.upper()} (Recupero)",
                "vincite_oro": vincite_fascia_oro,
                "percentuale_oro": percentuale_oro,
                "vincite_1_colpo": vincite_primo_colpo,
                "fallimenti": fallimenti,
                "totale_casi": totale_giocate
            })

    # Ordiniamo la classifica per maggior numero di vincite nella Fascia d'Oro (2°-5° colpo)
    classifica_coppie.sort(key=lambda x: x['vincite_oro'], reverse=True)

    print("\n=======================================================================")
    print(" 🔥 CLASSIFICA TOP 5 COPPIE DI RUOTE - FASCIA D'ORO (2°-5° COLPO) 🔥")
    print("=======================================================================")
    for idx, pos in enumerate(classifica_coppie[:5], 1):
        print(f"{idx}° Posto: {pos['coppia']}")
        print(f"    ⭐ Vincite in Fascia d'Oro (2°-5° colpo): {pos['vincite_oro']} su {pos['totale_casi']} casi ({pos['percentuale_oro']:.2f}%)")
        print(f"    💤 Uscite al 1° Colpo (Fase Studio): {pos['vincite_1_colpo']}")
        print(f"    ❌ Esiti Negativi oltre il 5° colpo: {pos['fallimenti']}")
        print("-" * 71)

if __name__ == "__main__":
    esegui_backtest()

import json
import os

FISSO = 31
RUOTA_BASE = "Bari"
RUOTA_RECUPERO = "Genova"

def fuori_90(numero):
    while numero > 90: numero -= 90
    while numero <= 0: numero += 90
    return numero

def esegui_analisi_dettagliata():
    if not os.path.exists('estrazioni.json'):
        print("Errore: estrazioni.json non trovato!")
        return

    with open('estrazioni.json', 'r', encoding='utf-8') as f:
        archivio = json.load(f)

    estrazioni_base = archivio[RUOTA_BASE]
    estrazioni_recupero = archivio[RUOTA_RECUPERO]
    totale_concorsi = min(len(estrazioni_base), len(estrazioni_recupero))

    # Tracciamento vincite colpo per colpo
    distribuzione_colpi = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    fallimenti = 0
    totale_casi = 0

    for i in range(0, totale_concorsi - 5):
        totale_casi += 1
        try:
            cinquina_passata = estrazioni_base[i]
            primo_estratto = cinquina_passata[0] if isinstance(cinquina_passata, list) else int(cinquina_passata)
        except:
            continue

        ambata = fuori_90(primo_estratto + FISSO)
        sfaldato = False

        for colpo in range(1, 6):
            idx = i + colpo
            c_base = estrazioni_base[idx]
            c_rec = estrazioni_recupero[idx]

            num_base = c_base if isinstance(c_base, list) else [c_base]
            num_rec = c_rec if isinstance(c_rec, list) else [c_rec]

            if ambata in num_base or ambata in num_rec:
                distribuzione_colpi[colpo] += 1
                sfaldato = True
                break
        
        if not sfaldato:
            fallimenti += 1

    print("\n=======================================================")
    print(f" 📊 DISTRIBUZIONE VINCITE PER {RUOTA_BASE.upper()} - {RUOTA_RECUPERO.upper()} 📊")
    print("=======================================================")
    print(f"Totale casi analizzati: {totale_casi}")
    print("-" * 55)
    for colpo, vincite in distribuzione_colpi.items():
        perc = (vincite / totale_casi) * 100
        nota = ""
        if colpo == 1: nota = " (Fase Studio - Non si gioca)"
        if colpo == 2: nota = " (Ingresso Fascia d'Oro ⭐)"
        if colpo == 5: nota = " (Ultima Spiaggia ⚠️)"
        print(f"🎯 {colpo}° Colpo: {vincite} vincite ({perc:.2f}%){nota}")
    
    perc_fall = (fallimenti / totale_casi) * 100
    print(f"❌ Negativi oltre il 5°: {fallimenti} casi ({perc_fall:.2f}%)")
    print("=======================================================")

if __name__ == '__main__':
    esegui_analisi_dettagliata()

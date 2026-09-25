import json
import os

def fuori_90(numero):
    while numero > 90: numero -= 90
    while numero < 1: numero += 90
    return numero

def calcola_diametrale(numero):
    return numero + 45 if numero <= 45 else numero - 45

def esegui_backtest(estrazioni, ruota_base, ruota_recupero, fisso):
    totale_previsioni = 0
    ambi_totali = 0
    ambi_fascia_oro = 0
    
    for i in range(len(estrazioni) - 9):
        estrazione_calcolo = estrazioni[i]
        
        if ruota_base not in estrazione_calcolo["ruote"]: continue
        numeri_base = estrazione_calcolo["ruote"][ruota_base]
        if not numeri_base: continue
            
        primo_estratto = numeri_base[0]
        ambata = fuori_90(primo_estratto + fisso)
        ambo_secco_base = calcola_diametrale(ambata)
        
        totale_previsioni += 1
        
        for colpo in range(1, 10):
            estrazione_futura = estrazioni[i + colpo]
            numeri_ruota_b = estrazione_futura["ruote"].get(ruota_base, [])
            numeri_ruota_r = estrazione_futura["ruote"].get(ruota_recupero, [])
            
            ambo_vinto_b = (ambata in numeri_ruota_b) and (ambo_secco_base in numeri_ruota_b)
            ambo_vinto_r = (ambata in numeri_ruota_r) and (ambo_secco_base in numeri_ruota_r)
            
            if ambo_vinto_b or ambo_vinto_r:
                ambi_totali += 1
                if 2 <= colpo <= 5:
                    ambi_fascia_oro += 1
                break 
                
    pct_ambo_totale = (ambi_totali / totale_previsioni * 100) if totale_previsioni > 0 else 0
    pct_ambo_oro = (ambi_fascia_oro / totale_previsioni * 100) if totale_previsioni > 0 else 0
    
    return {
        "previsioni_elaborate": totale_previsioni,
        "ambi_totali_vinti": ambi_totali,
        "percentuale_totale": round(pct_ambo_totale, 2),
        "ambi_oro_vinti": ambi_fascia_oro,
        "percentuale_oro": round(pct_ambo_oro, 2)
    }

def main():
    elenco_ruote = ["BARI", "CAGLIARI", "FIRENZE", "GENOVA", "MILANO", 
                    "NAPOLI", "PALERMO", "ROMA", "TORINO", "VENEZIA"]
    file_archivio = 'estrazioni.json'
    
    if not os.path.exists(file_archivio):
        print(f"Errore: Il file {file_archivio} non esiste.")
        return

    print("Caricamento archivio estrazioni...")
    with open(file_archivio, 'r', encoding='utf-8') as f:
        estrazioni = json.load(f)
        
    print(f"Archivio caricato. Record totali: {len(estrazioni)}")
    print("Elaborazione di 9.000 combinazioni in corso... Attendere...")
    
    classifica_combinazioni = []
    
    for fisso in range(1, 91):
        for rb in elenco_ruote:
            for rr in elenco_ruote:
                if rb == rr: continue
                    
                res = esegui_backtest(estrazioni, rb, rr, fisso)
                if res["previsioni_elaborate"] > 0:
                    classifica_combinazioni.append({
                        "ruota_base": rb,
                        "ruota_recupero": rr,
                        "fisso_ottimizzato": fisso,
                        "previsioni_totali": res["previsioni_elaborate"],
                        "ambi_totali": res["ambi_totali_vinti"],
                        "pct_totale": res["percentuale_totale"],
                        "ambi_oro": res["ambi_oro_vinti"],
                        "pct_oro": res["percentuale_oro"]
                    })
                    
    # Ordina per la percentuale della FASCIA D'ORO (colpi 2-5)
    classifica_combinazioni.sort(key=lambda x: x["pct_oro"], reverse=True)
    
    # Salva il file JSON per usi futuri
    with open('classifica_super_ottimizzatore.json', 'w', encoding='utf-8') as f:
        json.dump(classifica_combinazioni[:100], f, indent=4, ensure_ascii=False)
        
    # --- VISUALIZZAZIONE DELLA TOP 5 RICHIESTA ---
    print("\n" + "="*65)
    print("🏆 CLASSIFICA TOP 5 CONFIGURAZIONI: FASCIA D'ORO (COLPI 2-5) 🏆")
    print("="*65)
    for i, config in enumerate(classifica_combinazioni[:5], 1):
        print(f"🏅 {i}° POSTO: Ruota Base [{config['ruota_base']}] + Ruota Recupero [{config['ruota_recupero']}]")
        print(f"   👉 Fisso Sommativo V8: +{config['fisso_ottimizzato']}")
        print(f"   📊 Performance Fascia d'Oro (2°-5° Colpo): {config['pct_oro']}% ({config['ambi_oro']} Ambi)")
        print(f"   📈 Performance Ciclo Totale (1°-9° Colpo): {config['pct_totale']}% ({config['ambi_totali']} Ambi)")
        print("-" * 65)

if __name__ == "__main__":
    main()

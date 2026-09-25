import json
import os

def fuori_90(numero):
    while numero > 90: numero -= 90
    while numero < 1: numero += 90
    return numero

def calcola_diametrale(numero):
    return numero + 45 if numero <= 45 else numero - 45

def esegui_backtest(lista_storico, ruota_base, ruota_recupero, fisso):
    totale_previsioni = 0
    ambi_totali = 0
    ambi_fascia_oro = 0
    
    # Scansiona gli elementi presenti nello storico caricato
    for item in lista_storico:
        # Estraiamo l'ambata base salvata nello storico per la simulazione
        ambata_storica = item.get("ambata")
        if not isinstance(ambata_storica, int):
            continue
            
        ambata = fuori_90(ambata_storica + fisso)
        ambo_secco_base = calcola_diametrale(ambata)
        
        totale_previsioni += 1
        
        # Analisi simulata sui colpi registrati nella stringa
        testo_colpi = item.get("colpi", "")
        stato_esito = item.get("stato", "")
        
        if "Vincente" in stato_esito:
            import re
            match = re.search(r'\d+', testo_colpi)
            if match:
                colpo = int(match.group())
                ambi_totali += 1
                if 2 <= colpo <= 5:
                    ambi_fascia_oro += 1
                    
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
        dati_json = json.load(f)
        
    # Estrae la lista corretta dal dizionario
    lista_storico = dati_json.get("storico_verificato", [])
    
    print(f"Archivio caricato. Record utilizzabili nello storico: {len(lista_storico)}")
    
    if len(lista_storico) == 0:
        print("Errore: La lista 'storico_verificato' è vuota. Impossibile ottimizzare.")
        return
        
    print("Elaborazione delle combinazioni in corso...")
    classifica_combinazioni = []
    
    for fisso in range(1, 91):
        for rb in elenco_ruote:
            for rr in elenco_ruote:
                if rb == rr: continue
                    
                res = esegui_backtest(lista_storico, rb, rr, fisso)
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
                    
    classifica_combinazioni.sort(key=lambda x: x["pct_oro"], reverse=True)
    
    print("\n" + "="*65)
    print("🏆 CLASSIFICA TOP 5 CONFIGURAZIONI: FASCIA D'ORO (COLPI 2-5) 🏆")
    print("="*65)
    
    if not classifica_combinazioni:
        print("Nessuna combinazione rilevata con i dati attuali.")
        return
        
    for i, config in enumerate(classifica_combinazioni[:5], 1):
        print(f"🏅 {i}° POSTO: Ruota Base [{config['ruota_base']}] + Ruota Recupero [{config['ruota_recupero']}]")
        print(f"   👉 Fisso Sommativo V8: +{config['fisso_ottimizzato']}")
        print(f"   📊 Performance Fascia d'Oro (2°-5° Colpo): {config['pct_oro']}%")
        print(f"   📈 Performance Ciclo Totale (1°-9° Colpo): {config['pct_totale']}%")
        print("-" * 65)

if __name__ == "__main__":
    main()

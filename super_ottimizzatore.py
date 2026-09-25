import json
import os

# --- FUNZIONI UTILI ---
def fuori_90(numero):
    """Applica la regola del Fuori 90 del Lotto."""
    while numero > 90:
        numero -= 90
    while numero < 1:
        numero += 90
    return numero

def calcola_diametrale(numero):
    """Calcola il diametrale in somma/sottrazione 45."""
    if numero <= 45:
        return numero + 45
    else:
        return numero - 45

# --- MOTORE STATISTICO V8 ---
def esegui_backtest(estrazioni, ruota_base, ruota_recupero, fisso):
    """
    Esegue il backtest della strategia su tutto l'archivio.
    Analizza sia i 9 colpi totali che la Fascia d'Oro (2°-5° colpo).
    """
    totale_previsioni = 0
    ambi_totali = 0
    ambi_fascia_oro = 0
    
    # Ciclo sulle estrazioni lasciando spazio per gli ultimi 9 colpi di verifica
    for i in range(len(estrazioni) - 9):
        estrazione_calcolo = estrazioni[i]
        
        # 1. Verifica che la ruota base abbia i dati necessari
        if ruota_base not in estrazione_calcolo["ruote"]:
            continue
            
        numeri_base = estrazione_calcolo["ruote"][ruota_base]
        if not numeri_base:
            continue
            
        # 2. Logica Matematica V8
        primo_estratto = numeri_base[0]
        ambata = fuori_90(primo_estratto + fisso)
        ambo_secco_base = calcola_diametrale(ambata)
        
        totale_previsioni += 1
        
        # 3. Controllo dei 9 colpi successivi (Ciclo di Gioco)
        for colpo in range(1, 10):
            estrazione_futura = estrazioni[i + colpo]
            
            # Estraiamo i numeri usciti nelle due ruote nel colpo corrente
            numeri_ruota_b = estrazione_futura["ruote"].get(ruota_base, [])
            numeri_ruota_r = estrazione_futura["ruote"].get(ruota_recupero, [])
            
            # Verifichiamo se l'Ambo Secco è uscito su una delle due ruote
            ambo_vinto_b = (ambata in numeri_ruota_b) and (ambo_secco_base in numeri_ruota_b)
            ambo_vinto_r = (ambata in numeri_ruota_r) and (ambo_secco_base in numeri_ruota_r)
            
            if ambo_vinto_b or ambo_vinto_r:
                ambi_totali += 1
                
                # FILTRO FASCIA D'ORO: Il colpo corrente è tra il 2° e il 5°?
                if 2 <= colpo <= 5:
                    ambi_fascia_oro += 1
                    
                break # Si ferma al primo sfaldamento dell'ambo
                
    # Calcolo delle percentuali di rendimento
    pct_ambo_totale = (ambi_totali / totale_previsioni * 100) if totale_previsioni > 0 else 0
    pct_ambo_oro = (ambi_fascia_oro / totale_previsioni * 100) if totale_previsioni > 0 else 0
    
    return {
        "previsioni_elaborate": totale_previsioni,
        "ambi_totali_vinti": ambi_totali,
        "percentuale_totale": round(pct_ambo_totale, 2),
        "ambi_oro_vinti": ambi_fascia_oro,
        "percentuale_oro": round(pct_ambo_oro, 2)
    }

# --- MAIN SCRIPT ---
def main():
    # Elenco delle ruote ufficiali per la simulazione delle combinazioni
    elenco_ruote = ["BARI", "CAGLIARI", "FIRENZE", "GENOVA", "MILANO", 
                    "NAPOLI", "PALERMO", "ROMA", "TORINO", "VENEZIA"]
    
    file_archivio = 'estrazioni.json'
    
    if not os.path.exists(file_archivio):
        print(f"Errore: Il file {file_archivio} non esiste nella cartella corrente.")
        return

    print("Caricamento archivio estrazioni in corso...")
    with open(file_archivio, 'r', encoding='utf-8') as f:
        estrazioni = json.load(f)
        
    print(f"Archivio caricato con successo. Record totali: {len(estrazioni)}")
    print("Avvio della super ottimizzazione (Fascia d'Oro)... Spulciando le combinazioni...")
    
    classifica_combinazioni = []
    
    # Testiamo i fissi da 1 a 90 combinati su tutte le coppie di ruote
    for fisso in range(1, 91):
        for rb in elenco_ruote:
            for rr in elenco_ruote:
                if rb == rr:
                    continue # Escludiamo la stessa ruota come recupero
                    
                res = esegui_backtest(estrazioni, rb, rr, fisso)
                
                # Salviamo i dati rilevanti nel database temporaneo
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
                    
    # Ordiniamo la classifica mettendo in cima chi ha la percentuale più alta NELLA FASCIA D'ORO (2°-5° colpo)
    classifica_combinazioni.sort(key=lambda x: x["pct_oro"], reverse=True)
    
    # Salviamo i risultati in un file di report per index.html
    output_file = 'classifica_super_ottimizzatore.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(classifica_combinazioni[:100], f, indent=4, ensure_ascii=False) # Salva la Top 100
        
    print("\n=== TOP 5 CONFIGURAZIONI PER FASCIA D'ORO (2°-5° COLPO) ===")
    for i, config in enumerate(classifica_combinazioni[:5], 1):
        print(f"{i}. Ruote: {config['ruota_base']}-{config['ruota_recupero']} | Fisso: {config['fisso_ottimizzato']}")
        print(f"   Ambi Fascia Oro: {config['ambi_oro']} ({config['pct_oro']}%) | Ambi Totali 1-9 colpi: {config['ambi_totali']} ({config['pct_totale']}%)")
        print("-" * 60)
        
    print(f"\nOttimizzazione completata! La Top 100 è stata salvata in '{output_file}'.")

if __name__ == "__main__":
    main()

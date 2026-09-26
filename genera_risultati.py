import json
import os

# Configurazione Definitiva emersa dal Backtest
FISSO = 31
RUOTA_BASE = "Bari"       
RUOTA_RECUPERO = "Genova"

def fuori_90(numero):
    while numero > 90: numero -= 90
    while numero <= 0: numero += 90
    return numero

def calcola_diametrale(numero):
    if numero <= 45: return numero + 45
    else: return numero - 45

def analizza_archivio():
    if not os.path.exists('estrazioni.json'):
        print("Errore: estrazioni.json non trovato.")
        return

    with open('estrazioni.json', 'r', encoding='utf-8') as f:
        try:
            archivio = json.load(f)
        except json.JSONDecodeError:
            print("Errore: estrazioni.json non è un JSON valido.")
            return

    if RUOTA_BASE not in archivio or RUOTA_RECUPERO not in archivio:
        print(f"Errore: Ruote '{RUOTA_BASE}' o '{RUOTA_RECUPERO}' non trovate.")
        return

    estrazioni_base = archivio[RUOTA_BASE]
    estrazioni_recupero = archivio[RUOTA_RECUPERO]
    
    totale_concorsi = len(estrazioni_base)
    if totale_concorsi < 1:
        print("Errore: Archivio vuoto.")
        return

    cronologia_colpi = []
    
    # Scansione a ritroso mirata per catturare i colpi passati (dal 2° al 5° colpo)
    # Guardiamo i 5 concorsi precedenti a quello attuale
    start_index = max(0, totale_concorsi - 6)
    end_index = totale_concorsi - 1

    for i in range(start_index, end_index):
        # Il colpo avanza matematicamente in base a quanti concorsi separano la vecchia giocata dall'ultimo concorso inserito
        colpo_attuale = totale_concorsi - 1 - i + 1  
        
        # Filtriamo rigidamente solo la Fascia d'Oro (dal 2° al 5° colpo)
        if colpo_attuale < 2 or colpo_attuale > 5:
            continue

        try:
            cinquina_base_passata = estrazioni_base[i]
            primo_estratto_passato = cinquina_base_passata[0] if isinstance(cinquina_base_passata, list) else int(cinquina_base_passata)
        except:
            continue
        
        ambata_passata = fuori_90(primo_estratto_passato + FISSO)
        ambo_passato = calcola_diametrale(ambata_passata)
        
        sfaldato = False
        esito = "In corso"
        
        # Verifica se questa specifica previsione passata è già uscita nei concorsi successivi fino ad oggi
        for j in range(i + 1, totale_concorsi):
            if j >= len(estrazioni_base): break
            
            controllo_base = estrazioni_base[j]
            controllo_recupero = estrazioni_recupero[j] if j < len(estrazioni_recupero) else []

            in_base = (ambata_passata in controllo_base) if isinstance(controllo_base, list) else (ambata_passata == controllo_base)
            in_recupero = (ambata_passata in controllo_recupero) if isinstance(controllo_recupero, list) else (ambata_passata == controllo_recupero)

            if in_base or in_recupero:
                sfaldato = True
                esito = f"Sfaldato al {j - i + 1}° Colpo"
                break
                
        # Mantieni in basso nello storico SOLO quelle rimaste attive nella Fascia d'Oro!
        if not sfaldato:
            cronologia_colpi.append({
                "concorso": i + 1,  
                "ambata": ambata_passata,
                "ambo": f"{ambata_passata}-{ambo_passato}",
                "colpo": colpo_attuale,
                "stato": esito
            })

    # Previsione Attuale Nuova (1° Colpo - Fase di attesa generata dall'ultima estrazione)
    ultima_cinquina = estrazioni_base[-1]
    primo_estratto_attuale = ultima_cinquina[0] if isinstance(ultima_cinquina, list) else int(ultima_cinquina)
    
    ambata_attuale = fuori_90(primo_estratto_attuale + FISSO)
    ambo_attuale = calcola_diametrale(ambata_attuale)

    previsione_nuova = {
        "concorso": totale_concorsi,
        "ambata": ambata_attuale,
        "ambo": f"{ambata_attuale}-{ambo_attuale}",
        "colpo": 1,
        "nota": "Fase di attesa e studio. NON SI GIOCA."
    }

    output_finale = {
        "previsione_attuale": previsione_nuova,
        "storico_in_corso": cronologia_colpi
    }

    with open('risultati_v4.json', 'w', encoding='utf-8') as f:
        json.dump(output_finale, f, indent=4, ensure_ascii=False)
    print("risultati_v4.json generato correttamente per Bari e Genova.")

if __name__ == "__main__":
    analizza_archivio()

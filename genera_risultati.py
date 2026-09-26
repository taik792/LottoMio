import json
import os

# Configurazione Regina V8
FISSO = 31
RUOTA_BASE = "TO"
RUOTA_RECUPERO = "NA"

def fuori_90(numero):
    while numero > 90:
        numero -= 90
    while numero <= 0:
        numero += 90
    return numero

def calcola_diametrale(numero):
    if numero <= 45:
        return numero + 45
    else:
        return numero - 45

def analizza_archivio():
    if not os.path.exists('estrazioni.json'):
        print("Errore: estrazioni.json non trovato.")
        return

    # 1. Lettura pulita: esclude righe vuote e filtra solo quelle con abbastanza colonne
    linee_valide = []
    with open('estrazioni.json', 'r', encoding='utf-8') as f:
        for line in f:
            riga_pulita = line.strip().split()
            # Una riga valida deve avere almeno 12 colonne per raggiungere l'indice di TO (11)
            # Modifica il numero 12 se la tua struttura ha indici diversi
            if riga_pulita and len(riga_pulita) >= 12:
                # Verifica che i dati delle ruote siano effettivamente numeri
                try:
                    int(riga_pulita[11]) # Verifica TO
                    int(riga_pulita[6])  # Verifica NA
                    linee_valide.append(riga_pulita)
                except ValueError:
                    # Salta la riga se non contiene numeri (es. intestazioni, testi)
                    continue

    if len(linee_valide) < 1:
        print("Errore: Nessuna riga valida trovata nell'archivio.")
        return

    # Configurazione indici delle ruote
    ruote_indice = {"TO": 11, "NA": 6}
    cronologia_colpi = []
    
    # 2. Scansione a ritroso sicura sulle linee valide
    for i in range(len(linee_valide) - 5, len(linee_valide) - 1):
        if i < 0: continue
        
        riga_passata = linee_valide[i]
        primo_TO_passato = int(riga_passata[ruote_indice["TO"]]) 
        
        ambata_passata = fuori_90(primo_TO_passato + FISSO)
        ambo_passato = calcola_diametrale(ambata_passata)
        
        colpo_attuale = len(linee_valide) - 1 - i + 1
        
        sfaldato = False
        esito = "In corso"
        
        for j in range(i + 1, len(linee_valide)):
            estrazione_controllo = linee_valide[j]
            try:
                numeri_TO = [int(n) for n in estrazione_controllo[ruote_indice["TO"]:ruote_indice["TO"]+5]]
                numeri_NA = [int(n) for n in estrazione_controllo[ruote_indice["NA"]:ruote_indice["NA"]+5]]
                
                if ambata_passata in numeri_TO or ambata_passata in numeri_NA:
                    sfaldato = True
                    esito = f"Sfaldato al {j - i}° Colpo"
                    break
            except (ValueError, IndexError):
                continue
                
        if colpo_attuale >= 2 and colpo_attuale <= 5 and not sfaldato:
            cronologia_colpi.append({
                "concorso": riga_passata[0] if len(riga_passata) > 0 else "N/D",
                "data": riga_passata[1] if len(riga_passata) > 1 else "N/D",
                "ambata": ambata_passata,
                "ambo": f"{ambata_passata}-{ambo_passato}",
                "colpo": colpo_attuale,
                "stato": esito
            })

    # 3. Previsione Attuale (Ultima riga valida del file = 1° Colpo)
    ultima_riga = linee_valide[-1]
    primo_TO_attuale = int(ultima_riga[ruote_indice["TO"]])
    ambata_attuale = fuori_90(primo_TO_attuale + FISSO)
    ambo_attuale = calcola_diametrale(ambata_attuale)

    previsione_nuova = {
        "concorso": ultima_riga[0] if len(ultima_riga) > 0 else "N/D",
        "data": ultima_riga[1] if len(ultima_riga) > 1 else "N/D",
        "ambata": ambata_attuale,
        "ambo": f"{ambata_attuale}-{ambo_attuale}",
        "colpo": 1,
        "nota": "Fase di attesa e studio. NON SI GIOCA."
    }

    # 4. Scrittura output finale
    output_finale = {
        "previsione_attuale": previsione_nuova,
        "storico_in_corso": cronologia_colpi
    }

    with open('risultati_v4.json', 'w', encoding='utf-8') as f:
        json.dump(output_finale, f, indent=4, ensure_ascii=False)
    print("risultati_v4.json aggiornato con successo.")


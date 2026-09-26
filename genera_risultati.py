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
    # 1. Lettura del file tabellare
    if not os.path.exists('estrazioni.json'):
        print("Errore: estrazioni.json non trovato.")
        return

    with open('estrazioni.json', 'r', encoding='utf-8') as f:
        linee = [line.strip().split() for line in f.readlines() if line.strip()]

    if len(linee) < 1:
        print("Errore: Archivio vuoto.")
        return

    # Mappa delle posizioni delle ruote (adatta in base alla struttura reale del tuo file)
    # Assumiamo una struttura standard: Data, Concorso, BA, CA, ..., TO, NA...
    # Modifica gli indici di conseguenza se Torino e Napoli sono in posizioni diverse
    ruote_indice = {"TO": 11, "NA": 6} # Esempio indicativo

    cronologia_colpi = []
    
    # 2. Scansione a ritroso per calcolare lo storico dei colpi passati (dal concorso precedente a scendere)
    # Analizziamo gli ultimi concorsi per vedere lo stato delle previsioni passate
    for i in range(len(linee) - 5, len(linee) - 1):
        if i < 0: continue
        
        riga_passata = linee[i]
        # Calcolo previsione di quel concorso passato
        # Supponiamo che il 1° estratto di TO sia all'indice ruote_indice["TO"]
        primo_TO_passato = int(riga_passata[ruote_indice["TO"]]) 
        
        ambata_passata = fuori_90(primo_TO_passato + FISSO)
        ambo_passato = calcola_diametrale(ambata_passata)
        
        # Calcoliamo quanti concorsi sono passati da allora rispetto all'ultimo inserito
        colpo_attuale = len(linee) - 1 - i + 1 # +1 perché il concorso successivo alla generazione è il 2° colpo
        
        # Verifica se è uscito nei concorsi successivi (sfaldamento)
        sfaldato = False
        esito = "In corso"
        
        for j in range(i + 1, len(linee)):
            estrazione_controllo = linee[j]
            # Estrazione numeri di TO e NA al concorso J per controllo
            numeri_TO = [int(n) for n in estrazione_controllo[ruote_indice["TO"]:ruote_indice["TO"]+5]]
            numeri_NA = [int(n) for n in estrazione_controllo[ruote_indice["NA"]:ruote_indice["NA"]+5]]
            
            if ambata_passata in numeri_TO or ambata_passata in numeri_NA:
                sfaldato = True
                esito = f"Sfaldato al {j - i}° Colpo"
                break
                
        if colpo_attuale >= 2 and colpo_attuale <= 5 and not sfaldato:
            cronologia_colpi.append({
                "concorso": riga_passata[1], # ID Concorso
                "data": riga_passata[0],
                "ambata": ambata_passata,
                "ambo": f"{ambata_passata}-{ambo_passato}",
                "colpo": colpo_attuale,
                "stato": esito
            })

    # 3. Previsione Attuale (Ultima riga del file = 1° Colpo - Studio)
    ultima_riga = linee[-1]
    primo_TO_attuale = int(ultima_riga[ruote_indice["TO"]])
    ambata_attuale = fuori_90(primo_TO_attuale + FISSO)
    ambo_attuale = calcola_diametrale(ambata_attuale)

    previsione_nuova = {
        "concorso": ultima_riga[1],
        "data": ultima_riga[0],
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

if __name__ == "__main__":
    analizza_archivio()

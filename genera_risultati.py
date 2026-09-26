import json
import os

# Configurazione Regina V8
FISSO = 31
RUOTA_BASE = "Torino"       # NOTA: Nel tuo JSON le ruote hanno l'iniziale maiuscola
RUOTA_RECUPERO = "Napoli"

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
    # 1. Lettura nativa del file JSON
    if not os.path.exists('estrazioni.json'):
        print("Errore: estrazioni.json non trovato.")
        return

    with open('estrazioni.json', 'r', encoding='utf-8') as f:
        try:
            archivio = json.load(f)
        except json.JSONDecodeError:
            print("Errore: estrazioni.json non è un JSON valido.")
            return

    # Sincronizzazione ruote e controllo presenza dati
    if RUOTA_BASE not in archivio or RUOTA_RECUPERO not in archivio:
        print(f"Errore: Ruote '{RUOTA_BASE}' o '{RUOTA_RECUPERO}' non trovate nel file.")
        return

    estrazioni_base = archivio[RUOTA_BASE]
    estrazioni_recupero = archivio[RUOTA_RECUPERO]
    
    totale_concorsi = len(estrazioni_base)
    if totale_concorsi < 1:
        print("Errore: Archivio vuoto.")
        return

    cronologia_colpi = []
    
    # 2. Scansione a ritroso per calcolare l'avanzamento dei colpi passati (dal 2° al 5° colpo)
    # Range da totale_concorsi-5 (se esiste) fino al penultimo concorso (-2)
    start_index = max(0, totale_concorsi - 5)
    end_index = totale_concorsi - 1

    for i in range(start_index, end_index):
        # Calcoliamo quanti concorsi reali sono passati da QUELLA estrazione passata
        # rispetto all'ULTIMA estrazione inserita nell'archivio
        colpo_attuale = totale_concorsi - 1 - i + 1  # +1 perché il concorso subito dopo è il 2° colpo
        
        if colpo_attuale < 2 or colpo_attuale > 5:
            continue

        cinquina_base_passata = estrazioni_base[i]
        primo_estratto_passato = cinquina_base_passata[0] # 1° Estratto Ruota Base
        
        ambata_passata = fuori_90(primo_estratto_passato + FISSO)
        ambo_passato = calcola_diametrale(ambata_passata)
        
        # Verifica sfaldamento nei concorsi successivi a quello di generazione (fino all'ultimo attuale)
        sfaldato = False
        esito = "In corso"
        colpo_sfaldamento = 0
        
        for j in range(i + 1, totale_concorsi):
            controllo_base = estrazioni_base[j]
            controllo_recupero = estrazioni_recupero[j]
            
            # Un colpo avanza nel ciclo se non esce l'ambata su nessuna delle due ruote
            if ambata_passata in controllo_base or ambata_passata in controllo_recupero:
                sfaldato = True
                colpo_sfaldamento = j - i + 1
                esito = f"Sfaldato al {colpo_sfaldamento}° Colpo"
                break
                
        # Inseriamo nello storico visibile in basso solo le previsioni ancora attive (Fascia d'Oro)
        if not sfaldato:
            cronologia_colpi.append({
                "concorso": i + 1,  # Numero indicativo del concorso (indice + 1)
                "ambata": ambata_passata,
                "ambo": f"{ambata_passata}-{ambo_passato}",
                "colpo": colpo_attuale,
                "stato": esito
            })

    # 3. Previsione Attuale (Generata dall'ULTIMA riga assoluta dell'archivio = 1° Colpo)
    ultima_cinquina_base = estrazioni_base[-1]
    primo_estratto_attuale = ultima_cinquina_base[0]
    
    ambata_attuale = fuori_90(primo_estratto_attuale + FISSO)
    ambo_attuale = calcola_diametrale(ambata_attuale)

    previsione_nuova = {
        "concorso": totale_concorsi,
        "ambata": ambata_attuale,
        "ambo": f"{ambata_attuale}-{ambo_attuale}",
        "colpo": 1,
        "nota": "Fase di attesa e studio (1° Colpo). NON SI GIOCA."
    }

    # 4. Scrittura output finale in risultati_v4.json
    output_finale = {
        "previsione_attuale": previsione_nuova,
        "storico_in_corso": cronologia_colpi
    }

    with open('risultati_v4.json', 'w', encoding='utf-8') as f:
        json.dump(output_finale, f, indent=4, ensure_ascii=False)
    print("risultati_v4.json aggiornato con successo in formato nativo.")

if __name__ == "__main__":
    analizza_archivio()

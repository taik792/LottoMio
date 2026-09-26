import json
import os

# Configurazione Regina V8
FISSO = 31
RUOTA_BASE = "Torino"       
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
    
    # 2. Scansione a ritroso protetta per i colpi passati (dal 2° al 5° colpo)
    start_index = max(0, totale_concorsi - 5)
    end_index = totale_concorsi - 1

    for i in range(start_index, end_index):
        colpo_attuale = totale_concorsi - 1 - i + 1  
        
        if colpo_attuale < 2 or colpo_attuale > 5:
            continue

        try:
            cinquina_base_passata = estrazioni_base[i]
            # Gestione se l'elemento è una lista (cinquina) o un singolo numero numerico
            if isinstance(cinquina_base_passata, list):
                primo_estratto_passato = int(cinquina_base_passata[0])
            else:
                primo_estratto_passato = int(cinquina_base_passata)
        except (IndexError, ValueError, TypeError):
            continue # Salta se l'estrazione passata è malformata
        
        ambata_passata = fuori_90(primo_estratto_passato + FISSO)
        ambo_passato = calcola_diametrale(ambata_passata)
        
        sfaldato = False
        esito = "In corso"
        
        # Controllo sfaldamento protetto da squilibri di lunghezza tra ruote
        for j in range(i + 1, totale_concorsi):
            try:
                controllo_base = estrazioni_base[j]
                
                # Se la ruota di controllo recupero non ha ancora l'estrazione J, usa una lista vuota
                if j < len(estrazioni_recupero):
                    controllo_recupero = estrazioni_recupero[j]
                else:
                    controllo_recupero = []

                # Verifica presenza dell'ambata (gestisce sia se l'estrazione è una lista che un singolo valore)
                in_base = (ambata_passata in controllo_base) if isinstance(controllo_base, list) else (ambata_passata == controllo_base)
                in_recupero = (ambata_passata in controllo_recupero) if isinstance(controllo_recupero, list) else (ambata_passata == controllo_recupero)

                if in_base or in_recupero:
                    sfaldato = True
                    esito = f"Sfaldato al {j - i + 1}° Colpo"
                    break
            except IndexError:
                break # Interrompe la ricerca per questa previsione se gli indici si interrompono
                
        if not sfaldato:
            cronologia_colpi.append({
                "concorso": i + 1,  
                "ambata": ambata_passata,
                "ambo": f"{ambata_passata}-{ambo_passato}",
                "colpo": colpo_attuale,
                "stato": esito
            })

    # 3. Previsione Attuale sicura (Generata dall'ULTIMA riga assoluta di Ruota Base = 1° Colpo)
    ultima_cinquina_base = estrazioni_base[-1]
    if isinstance(ultima_cinquina_base, list):
        primo_estratto_attuale = int(ultima_cinquina_base[0])
    else:
        primo_estratto_attuale = int(ultima_cinquina_base)
    
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
    print("risultati_v4.json generato con successo e blindato contro IndexError.")

if __name__ == "__main__":
    analizza_archivio()

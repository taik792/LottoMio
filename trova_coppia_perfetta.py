import json
import os

def fuori_90(numero):
    while numero > 90: numero -= 90
    while numero <= 0: numero += 90
    return numero

def calcola_diametrale(numero):
    if numero <= 45: return numero + 45
    return numero - 45

def analizza_tutte_le_coppie():
    if not os.path.exists('estrazioni.json'):
        print("Errore: estrazioni.json non trovato.")
        return

    # Ruota di partenza impostata su ROMA
    RUOTA_PARTENZA = "ROMA" 

    with open('estrazioni.json', 'r', encoding='utf-8') as f:
        archivio = json.load(f)

    # CORREZIONE: Standardizziamo l'intero archivio in lettere MAIUSCOLE prima di lavorarlo
    archivio_pulito = {k.upper(): v for k, v in archivio.items() if isinstance(v, list) and len(v) > 0}
    
    if RUOTA_PARTENZA not in archivio_pulito:
        print(f"Errore: La ruota {RUOTA_PARTENZA} non è stata trovata nell'archivio. Ruote rilevate: {list(archivio_pulito.keys())}")
        return

    estrazioni_base = archivio_pulito[RUOTA_PARTENZA]
    tot_estrazioni = len(estrazioni_base)
    
    miglior_coppia_assoluta = None
    max_ambi_vinti = -1

    print(f"🔬 Analisi in corso... Cerco la migliore ruota da accoppiare a {RUOTA_PARTENZA} su {tot_estrazioni} estrazioni.")

    for ruota_recupero, estrazioni_recupero in archivio_pulito.items():
        if ruota_recupero == RUOTA_PARTENZA or ruota_recupero == "NAZIONALE": continue
        
        for fisso in range(1, 91):
            vincite_ambata = 0
            vincite_ambo = 0
            totale_previsioni = 0

            for i in range(tot_estrazioni - 9):
                if i >= len(estrazioni_recupero): break
                if not estrazioni_base[i] or len(estrazioni_base[i]) < 1: continue
                
                try:
                    primo_numero = int(estrazioni_base[i][0]) if isinstance(estrazioni_base[i], list) else int(estrazioni_base[i])
                    ambata = fuori_90(primo_numero + fisso)
                    abbinamento = calcola_diametrale(ambata)
                    
                    totale_previsioni += 1
                    vinta_ambata = False
                    vinto_ambo = False

                    for colpo in range(1, 10):
                        idx = i + colpo
                        if idx >= tot_estrazioni or idx >= len(estrazioni_recupero): break
                        
                        num_base_futuri = [int(n) for n in estrazioni_base[idx][:5]]
                        num_recu_futuri = [int(n) for n in estrazioni_recupero[idx][:5]]

                        if not vinta_ambata and ((ambata in num_base_futuri) or (ambata in num_recu_futuri)):
                            vincite_ambata += 1
                            vinta_ambata = True

                        if not vinto_ambo:
                            if (ambata in num_base_futuri and abbinamento in num_base_futuri) or (ambata in num_recu_futuri and abbinamento in num_recu_futuri):
                                vincite_ambo += 1
                                vinto_ambo = True
                except:
                    continue

            if vincite_ambo > max_ambi_vinti and totale_previsioni > 0:
                max_ambi_vinti = vincite_ambo
                miglior_coppia_assoluta = {
                    "ruota_2": ruota_recupero,
                    "fisso": fisso,
                    "perc_ambata": (vincite_ambata / totale_previsioni) * 100,
                    "perc_ambo": (vincite_ambo / totale_previsioni) * 100,
                    "ambi_totali": vincite_ambo,
                    "tot_prev": totale_previsioni
                }

    print("=" * 70)
    print(f"🏆 RISULTATO OTTIMIZZAZIONE RUOTE PER: {RUOTA_PARTENZA} 🏆")
    print("=" * 70)
    if miglior_coppia_assoluta:
        print(f"Abbinamento perfetto: {RUOTA_PARTENZA} - {miglior_coppia_assoluta['ruota_2']}")
        print(f"Fisso Sommativo da usare sul 1° di {RUOTA_PARTENZA}: +{miglior_coppia_assoluta['fisso']}")
        print(f"Frequenza Ambata: {miglior_coppia_assoluta['perc_ambata']:.2f}%")
        print(f"Ambi Secchi Vinti nello storico: {miglior_coppia_assoluta['ambi_totali']} ({miglior_coppia_assoluta['perc_ambo']:.2f}%)")
    else:
        print("Nessuna combinazione trovata.")

if __name__ == "__main__":
    analizza_tutte_le_coppie()

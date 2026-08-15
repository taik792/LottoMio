import json
import os

def fuori_90(numero):
    while numero > 90: numero -= 90
    while numero <= 0: numero += 90
    return numero

def esegui_backtest(limite_estrazioni=50, max_colpi=6):
    if not os.path.exists('estrazioni.json'):
        print("Errore: File estrazioni.json non trovato.")
        return

    with open('estrazioni.json', 'r', encoding='utf-8') as f:
        archivio = json.load(f)

    archivio_pulito = {k.upper(): v for k, v in archivio.items() if isinstance(v, list)}

    if "CAGLIARI" not in archivio_pulito or "PALERMO" not in archivio_pulito:
        print("Errore: Ruote di Cagliari o Palermo non presenti nell'archivio.")
        return

    ca = archivio_pulito["CAGLIARI"]
    pa = archivio_pulito["PALERMO"]
    tot_estrazioni = len(ca)

    if tot_estrazioni < limite_estrazioni + max_colpi:
        limite_estrazioni = tot_estrazioni - max_colpi

    start_idx = tot_estrazioni - max_colpi - limite_estrazioni
    end_idx = tot_estrazioni - max_colpi

    print(f"--- AVVIO BACKTEST SU CAGLIARI-PALERMO ---")
    print(f"Concorsi analizzati: {limite_estrazioni} | Finestra di gioco: {max_colpi} colpi\n")

    classifica_fissi = {}

    # Scansione di tutte le coppie di fissi possibili (Fisso Ambata, Fisso Abbinamento)
    for fisso_ambata in range(1, 91):
        for fisso_abbinamento in range(1, 91):
            if fisso_ambata == fisso_abbinamento: continue

            ambi_vinti = 0
            ambate_vinte = 0
            casi_totali = 0

            for i in range(start_idx, end_idx):
                if not isinstance(ca[i], list) or len(ca[i]) < 1: continue
                
                try:
                    primo_ca = int(ca[i][0])
                    num_ambata = fuori_90(primo_ca + fisso_ambata)
                    num_abbinamento = fuori_90(primo_ca + fisso_abbinamento)
                    casi_totali += 1

                    ambo_hit = False
                    ambata_hit = False

                    # Verifica nei colpi successivi
                    for colpo in range(1, max_colpi + 1):
                        idx_check = i + colpo
                        ca_nums = [int(n) for n in ca[idx_check][:5]]
                        pa_nums = [int(n) for n in pa[idx_check][:5]]

                        # Controllo Ambo Secco
                        if (num_ambata in ca_nums and num_abbinamento in ca_nums) or \
                           (num_ambata in pa_nums and num_abbinamento in pa_nums):
                            ambo_hit = True
                            break
                        
                        # Controllo Ambata
                        if (num_ambata in ca_nums) or (num_ambata in pa_nums):
                            ambata_hit = True

                    if ambo_hit:
                        ambi_vinti += 1
                    elif ambata_hit:
                        ambate_vinte += 1

                except (ValueError, IndexError):
                    continue

            if casi_totali > 0:
                percentuale_ambi = (ambi_vinti / casi_totali) * 100
                classifica_fissi[(fisso_ambata, fisso_abbinamento)] = {
                    "ambi": ambi_vinti,
                    "ambate": ambate_vinte,
                    "totale": casi_totali,
                    "perc_ambo": percentuale_ambi
                }

    # Ordinamento per maggior numero di Ambi Vinti
    top_risultati = sorted(classifica_fissi.items(), key=lambda x: (x[1]['ambi'], x[1]['ambate']), reverse=True)[:5]

    print("=== TOP 5 COPPIE DI FISSI PER AMBO SECCO ===")
    for rank, (coppia, stats) in enumerate(top_risultati, 1):
        f_amb, f_abb = coppia
        print(f"{rank}°) Formula: 1° CA +{f_amb} (Ambata) e 1° CA +{f_abb} (Abbinamento)")
        print(f"    -> Ambi Secchi Vinti: {stats['ambi']} su {stats['totale']} concorsi ({stats['perc_ambo']:.1f}%)")
        print(f"    -> Solo Ambata: {stats['ambate']} concorsi\n")

if __name__ == "__main__":
    esegui_backtest(limite_estrazioni=60, max_colpi=6)

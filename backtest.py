import json
import os

RUOTE = ["BARI", "CAGLIARI", "FIRENZE", "GENOVA", "MILANO", "NAPOLI", "PALERMO", "ROMA", "TORINO", "VENEZIA"]

def fuori_90(n):
    while n > 90: n -= 90
    while n <= 0: n += 90
    return n

def super_backtest(limite_estrazioni=50, max_colpi=6):
    if not os.path.exists('estrazioni.json'):
        print("Errore: estrazioni.json non trovato.")
        return

    with open('estrazioni.json', 'r', encoding='utf-8') as f:
        archivio = json.load(f)

    archivio_pulito = {k.upper(): v for k, v in archivio.items() if isinstance(v, list)}
    
    tot_estrazioni = len(archivio_pulito.get("BARI", []))
    if tot_estrazioni < limite_estrazioni + max_colpi:
        limite_estrazioni = tot_estrazioni - max_colpi

    start_idx = tot_estrazioni - max_colpi - limite_estrazioni
    end_idx = tot_estrazioni - max_colpi

    miglior_score = -1
    miglior_setup = None

    print("--- AVVIO SUPER-BACKTEST MULTI-RUOTA ---")

    # Scansione su tutte le ruote spia
    for r_spia in RUOTE:
        if r_spia not in archivio_pulito: continue
        dati_spia = archivio_pulito[r_spia]

        # Scansione coppie di ruote di gioco
        for i_r1 in range(len(RUOTE)):
            for i_r2 in range(i_r1 + 1, len(RUOTE)):
                r1, r2 = RUOTE[i_r1], RUOTE[i_r2]
                if r1 not in archivio_pulito or r2 not in archivio_pulito: continue
                
                dati_r1 = archivio_pulito[r1]
                dati_r2 = archivio_pulito[r2]

                # Test campionario dei fissi a passi di 3 per velocizzare l'esecuzione su GitHub
                for f_amb in range(1, 91, 2):
                    for f_abb in range(1, 91, 3):
                        if f_amb == f_abb: continue

                        ambi_vinti = 0
                        for i in range(start_idx, end_idx):
                            try:
                                primo_spia = int(dati_spia[i][0])
                                n_amb = fuori_90(primo_spia + f_amb)
                                n_abb = fuori_90(primo_spia + f_abb)

                                for colpo in range(1, max_colpi + 1):
                                    idx_c = i + colpo
                                    nums_r1 = [int(x) for x in dati_r1[idx_c][:5]]
                                    nums_r2 = [int(x) for x in dati_r2[idx_c][:5]]

                                    if (n_amb in nums_r1 and n_abb in nums_r1) or (n_amb in nums_r2 and n_abb in nums_r2):
                                        ambi_vinti += 1
                                        break
                            except (ValueError, IndexError):
                                continue

                        if ambi_vinti > miglior_score:
                            miglior_score = ambi_vinti
                            miglior_setup = {
                                "ruota_spia": r_spia,
                                "ruota_1": r1,
                                "ruota_2": r2,
                                "fisso_ambata": f_amb,
                                "fisso_abbinamento": f_abb,
                                "ambi": ambi_vinti
                            }

    print("\n=== MIGLIOR SETUP ABSOLUTO TROVATO ===")
    print(f"Ruota Spia: 1° di {miglior_setup['ruota_spia']}")
    print(f"Ruote di Gioco: {miglior_setup['ruota_1']} e {miglior_setup['ruota_2']}")
    print(f"Formula: Spia +{miglior_setup['fisso_ambata']} (Ambata) e Spia +{miglior_setup['fisso_abbinamento']} (Abbinamento)")
    print(f"Ambi vinti negli ultimi concorsi: {miglior_setup['ambi']}")

if __name__ == "__main__":
    super_backtest()

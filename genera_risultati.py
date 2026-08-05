import json
import os

MAX_COLPI = 6


def carica_json(filepath):
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ Errore durante la lettura di {filepath}: {e}")
        return None


def salva_json(filepath, data):
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"❌ Errore durante il salvataggio di {filepath}: {e}")


def trova_condizioni_isotope(dati):
    condizioni = []
    ultime_estrazioni = {}

    for ruota, lista_est in dati.items():
        if lista_est:
            ultime_estrazioni[ruota.upper().strip()] = lista_est[-1]

    ruote = sorted(list(ultime_estrazioni.keys()))

    for i in range(len(ruote)):
        for j in range(i + 1, len(ruote)):
            r1, r2 = ruote[i], ruote[j]
            est1, est2 = ultime_estrazioni[r1], ultime_estrazioni[r2]

            for pos in range(5):
                n1, n2 = est1[pos], est2[pos]
                cad1, cad2 = n1 % 10, n2 % 10

                if n1 == n2 or cad1 == cad2:
                    punti_forza = 2 if n1 == n2 else 1
                    condizioni.append(
                        {
                            "ruota1": r1,
                            "ruota2": r2,
                            "posizione": pos + 1,
                            "num1": n1,
                            "num2": n2,
                            "cadenza": cad1,
                            "forza": punti_forza,
                        }
                    )

    # Ordina le condizioni trovate per rilevanza
    condizioni.sort(key=lambda x: x["forza"], reverse=True)
    return condizioni


def calcola_pronostico(r1, r2, dati, cond):
    est1 = dati.get(r1, [])
    est2 = dati.get(r2, [])

    freq_combinata = {n: 0 for n in range(1, 91)}
    for est in est1[-20:] + est2[-20:]:
        for num in est:
            freq_combinata[num] += 1

    cadenza_target = cond["cadenza"]
    numeri_cadenza = [n for n in range(1, 91) if n % 10 == cadenza_target]
    numeri_cadenza_ordinati = sorted(
        numeri_cadenza, key=lambda n: freq_combinata[n], reverse=True
    )

    ambata = numeri_cadenza_ordinati[0]
    abbinamento1 = numeri_cadenza_ordinati[1]

    altro_frequente = next(
        n
        for n, f in sorted(
            freq_combinata.items(), key=lambda x: x[1], reverse=True
        )
        if n % 10 != cadenza_target
    )

    # ID UNICO FISSO: Impedisce al programma di azzerare i colpi ad ogni run
    id_unico = f"{r1}_{r2}_pos{cond['posizione']}"

    return {
        "id": id_unico,
        "ruota_principale": r1,
        "ruota_secondaria": r2,
        "motivo": f"Isotopia {cond['posizione']}ª pos (N. {cond['num1']}/{cond['num2']})",
        "ambata": ambata,
        "ambo": [ambata, abbinamento1],
        "quartina": [ambata, abbinamento1, altro_frequente],
        "colpo_attuale": 1,
    }


def main():
    file_estrazioni = "estrazioni.json"
    file_archivio = "archivio_previsioni.json"
    file_uscita = "risultati_v4.json"

    dati = carica_json(file_estrazioni)
    if not dati:
        print("❌ File estrazioni.json mancante o vuoto.")
        return

    # Normalizza i nomi delle ruote
    dati_clean = {k.upper().strip(): v for k, v in dati.items()}

    # 1. Carica l'archivio esistente
    previsioni_esistenti = carica_json(file_archivio) or []

    # 2. Fai avanzare di 1 colpo le previsioni già in corso
    previsioni_aggiornate = []
    id_attivi = set()

    for prev in previsioni_esistenti:
        prev["colpo_attuale"] += 1
        # Mantieni in corsa solo quelle che non hanno superato il limite di colpi
        if prev["colpo_attuale"] <= MAX_COLPI:
            previsioni_aggiornate.append(prev)
            id_attivi.add(prev["id"])

    # 3. Cerca nuove condizioni nell'ultima estrazione
    condizioni = trova_condizioni_isotope(dati_clean)

    for cond in condizioni:
        r1, r2 = cond["ruota1"], cond["ruota2"]
        id_temp = f"{r1}_{r2}_pos{cond['posizione']}"

        # Aggiungi la nuova previsione solo se la coppia su quella posizione non è già in corsa
        if id_temp not in id_attivi:
            nuova_prev = calcola_pronostico(r1, r2, dati_clean, cond)
            previsioni_aggiornate.append(nuova_prev)
            id_attivi.add(id_temp)

        if len(previsioni_aggiornate) >= 6:  # Limite max schede a schermo
            break

    # 4. Salva l'archivio per la prossima esecuzione
    salva_json(file_archivio, previsioni_aggiornate)

    # 5. Genera l'output per l'interfaccia Web
    output_web = {
        "tipo_analisi": "Isotopie e Cadenze Gemelle (Inseguimento 6 colpi)",
        "previsioni_top": previsioni_aggiornate,
    }
    salva_json(file_uscita, output_web)

    print(f"✅ Successo! Previsioni attive elaborate: {len(previsioni_aggiornate)}")


if __name__ == "__main__":
    main()

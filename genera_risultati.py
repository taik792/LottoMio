import json
import os

# Mappa delle ruote Diametrali / Gemelle storiche
RUOTE_GEMELLE = {
    "BARI": "NAPOLI",
    "CAGLIARI": "PALERMO",
    "FIRENZE": "ROMA",
    "GENOVA": "TORINO",
    "MILANO": "VENEZIA",
    "NAPOLI": "BARI",
    "PALERMO": "CAGLIARI",
    "ROMA": "FIRENZE",
    "TORINO": "GENOVA",
    "VENEZIA": "MILANO",
}


def carica_estrazioni(filepath):
    if not os.path.exists(filepath):
        print(f"❌ Errore: File '{filepath}' non trovato.")
        return None

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Errore lettura JSON: {e}")
        return None

    estrazioni_pulite = {}
    for ruota, estrazioni in data.items():
        # Pulizia nomi ruote
        ruota_clean = ruota.upper().strip()
        estrazioni_pulite[ruota_clean] = [
            [int(n) for n in est] for est in estrazioni
        ]

    return estrazioni_pulite


def trova_condizioni_isotope(dati):
    """Cerca numeri o cadenze identiche nella STESSA posizione tra due ruote."""
    condizioni = []

    # Prendiamo l'ultima estrazione disponibile per ogni ruota
    ultime_estrazioni = {}
    for ruota, lista_est in dati.items():
        if lista_est:
            ultime_estrazioni[ruota] = lista_est[-1]

    ruote = list(ultime_estrazioni.keys())

    for i in range(len(ruote)):
        for j in range(i + 1, len(ruote)):
            r1, r2 = ruote[i], ruote[j]
            est1, est2 = ultime_estrazioni[r1], ultime_estrazioni[r2]

            # Controlliamo posizione per posizione (0 to 4)
            for pos in range(5):
                n1, n2 = est1[pos], est2[pos]
                cad1, cad2 = n1 % 10, n2 % 10

                # Condizione 1: Numero Isotopo Perfetto (stesso numero stessa pos)
                # Condizione 2: Cadenza Isotopa (stessa cadenza stessa pos)
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

    # Ordina per forza (prima le isotopie di numero secco, poi di cadenza)
    condizioni.sort(key=lambda x: x["forza"], reverse=True)
    return condizioni


def calcola_pronostico_coppia(r1, r2, dati, cond):
    """Genera il pronostico mirato per la coppia di ruote rilevata."""
    est1 = dati.get(r1, [])
    est2 = dati.get(r2, [])

    # Calcolo frequenze combinate sulle due ruote (ultime 20 estrazioni)
    freq_combinata = {n: 0 for n in range(1, 91)}
    for est in est1[-20:] + est2[-20:]:
        for num in est:
            freq_combinata[num] += 1

    cadenza_target = cond["cadenza"]
    numeri_cadenza = [n for n in range(1, 91) if n % 10 == cadenza_target]

    # Ordina i numeri della cadenza per frequenza recente combinata
    numeri_cadenza_ordinati = sorted(
        numeri_cadenza, key=lambda n: freq_combinata[n], reverse=True
    )

    ambata = numeri_cadenza_ordinati[0]
    abbinamento1 = numeri_cadenza_ordinati[1]

    # Terzo numero: il più frequente in assoluto sulle due ruote non appartenente alla cadenza
    altro_frequente = next(
        n
        for n, f in sorted(
            freq_combinata.items(), key=lambda x: x[1], reverse=True
        )
        if n % 10 != cadenza_target
    )

    ambo = [ambata, abbinamento1]
    terno_quartina = [ambata, abbinamento1, altro_frequente]

    return {
        "ruota_principale": r1,
        "ruota_secondaria": r2,
        "motivo": f"Isotopia in {cond['posizione']}ª pos (N. {cond['num1']} / {cond['num2']} - Cad. {cadenza_target})",
        "ambata": ambata,
        "ambo": ambo,
        "quartina": terno_quartina,
    }


def main():
    file_ingresso = "estrazioni.json"
    file_uscita = "risultati_v4.json"

    dati = carica_estrazioni(file_ingresso)
    if not dati:
        return

    # 1. Trova le migliori condizioni Isotope
    condizioni = trova_condizioni_isotope(dati)

    pronostici_selezionati = []
    coppie_usate = set()

    # Prendiamo fino alle 3 migliori condizioni non sovrapposte
    for cond in condizioni:
        r1, r2 = cond["ruota1"], cond["ruota2"]
        coppia_key = tuple(sorted([r1, r2]))

        if coppia_key not in coppie_usate:
            pronostico = calcola_pronostico_coppia(r1, r2, dati, cond)
            pronostici_selezionati.append(pronostico)
            coppie_usate.add(coppia_key)

        if len(pronostici_selezionati) >= 3:
            break

    # Strutturazione output JSON
    output_json = {
        "tipo_analisi": "Isotopie e Cadenze Gemelle",
        "previsioni_top": pronostici_selezionati,
    }

    try:
        with open(file_uscita, "w", encoding="utf-8") as f:
            json.dump(output_json, f, indent=4, ensure_ascii=False)
        print(
            f"✅ Analisi Isotopa completata! Salvate {len(pronostici_selezionati)} previsioni top in '{file_uscita}'."
        )
    except Exception as e:
        print(f"❌ Errore salvataggio: {e}")


if __name__ == "__main__":
    main()

import json
import os


def carica_estrazioni(filepath):
    """Carica il file JSON sorgente e converte i dati in numeri interi."""
    if not os.path.exists(filepath):
        print(f"❌ Errore: Il file '{filepath}' non esiste.")
        return None

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Errore durante la lettura di '{filepath}': {e}")
        return None

    estrazioni_pulite = {}
    for ruota, estrazioni in data.items():
        estrazioni_pulite[ruota] = []
        for estrazione in estrazioni:
            # Conversione esplicita in interi
            estrazione_int = [int(n) for n in estrazione]
            estrazioni_pulite[ruota].append(estrazione_int)

    return estrazioni_pulite


def analizza_frequenze(estrazioni_ruota):
    """Calcola la frequenza di ciascun numero (1-90)."""
    frequenze = {n: 0 for n in range(1, 91)}
    for estrazione in estrazioni_ruota:
        for numero in estrazione:
            if 1 <= numero <= 90:
                frequenze[numero] += 1
    return frequenze


def analizza_ritardi(estrazioni_ruota):
    """Calcola il ritardo attuale di ciascun numero (1-90)."""
    ritardi = {n: 0 for n in range(1, 91)}
    for numero in range(1, 91):
        ritardo = 0
        trovato = False
        for estrazione in reversed(estrazioni_ruota):
            if numero in estrazione:
                trovato = True
                break
            ritardo += 1
        ritardi[numero] = ritardo if trovato else len(estrazioni_ruota)
    return ritardi


def main():
    file_ingresso = "estrazioni.json"
    file_uscita = "risultati_v4.json"

    dati = carica_estrazioni(file_ingresso)

    if not dati:
        print("Impossibile procedere: dati non caricati o file vuoto.")
        return

    risultati_finali = {}

    # Elaborazione di tutte le ruote
    for ruota, estrazioni in dati.items():
        if not estrazioni:
            continue

        totale_estrazioni = len(estrazioni)
        freq = analizza_frequenze(estrazioni)
        rit = analizza_ritardi(estrazioni)

        # Ordinamento Top 5 Frequenti e Ritardatari
        top_frequenti = sorted(freq.items(), key=lambda x: x[1], reverse=True)[
            :5
        ]
        top_ritardatari = sorted(
            rit.items(), key=lambda x: x[1], reverse=True
        )[:5]

        # Strutturazione dei dati JSON per la ruota corrente
        risultati_finali[ruota] = {
            "totale_estrazioni_analizzate": totale_estrazioni,
            "top_frequenti": [
                {"numero": num, "frequenza": f} for num, f in top_frequenti
            ],
            "top_ritardatari": [
                {"numero": num, "ritardo": r} for num, r in top_ritardatari
            ],
            "statistiche_complete": {
                "frequenze": freq,
                "ritardi": rit,
            },
        }

    # Scrittura del file JSON di output
    try:
        with open(file_uscita, "w", encoding="utf-8") as f:
            json.dump(risultati_finali, f, indent=4, ensure_ascii=False)
        print(f"✅ Analisi completata con successo!")
        print(f"📄 I risultati sono stati salvati in '{file_uscita}'")
    except Exception as e:
        print(f"❌ Errore durante il salvataggio del file JSON: {e}")


if __name__ == "__main__":
    main()

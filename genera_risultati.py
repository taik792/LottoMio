import json
import os


def carica_estrazioni(filepath):
    """Carica il file JSON e converte tutti i valori in numeri interi."""
    if not os.path.exists(filepath):
        print(f"Errore: Il file '{filepath}' non esiste nella cartella attuale.")
        return None

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    estrazioni_pulite = {}
    for ruota, estrazioni in data.items():
        estrazioni_pulite[ruota] = []
        for estrazione in estrazioni:
            # Converte ogni numero della cinquina in intero
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
    """Calcola il ritardo attuale di ciascun numero (1-90).

    Scorre le estrazioni dal fondo (la più recente) verso l'inizio.
    """
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
    file_path = "estrazioni.json"
    dati = carica_estrazioni(file_path)

    if not dati:
        return

    print("==========================================")
    print("      ANALISI STATISTICA ESTRAZIONI       ")
    print("==========================================")

    # Scorre ed elabora automaticamente tutte le ruote nel file
    for ruota, estrazioni in dati.items():
        if not estrazioni:
            continue

        totale_estrazioni = len(estrazioni)
        freq = analizza_frequenze(estrazioni)
        rit = analizza_ritardi(estrazioni)

        # Prende i primi 5 più frequenti e i primi 5 più ritardatari
        top_frequenti = sorted(freq.items(), key=lambda x: x[1], reverse=True)[
            :5
        ]
        top_ritardatari = sorted(
            rit.items(), key=lambda x: x[1], reverse=True
        )[:5]

        print(f"\n RUOTA DI {ruota.upper()} ({totale_estrazioni} estrazioni)")
        print("-" * 40)

        print("  [+] Top 5 Più Frequenti:")
        for num, f in top_frequenti:
            print(f"      - Numero {num:2d} -> Uscito {f} volte")

        print("  [-] Top 5 Più Ritardatari:")
        for num, r in top_ritardatari:
            print(f"      - Numero {num:2d} -> Ritardo: {r} estrazioni")

        print("=" * 40)


if __name__ == "__main__":
    main()

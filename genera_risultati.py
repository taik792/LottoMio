import json
import os


def carica_estrazioni(filepath):
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    estrazioni_pulite = {}
    for ruota, estrazioni in data.items():
        estrazioni_pulite[ruota] = [
            [int(n) for n in est] for est in estrazioni
        ]
    return estrazioni_pulite


def analizza_frequenze(estrazioni_ruota):
    frequenze = {n: 0 for n in range(1, 91)}
    for estrazione in estrazioni_ruota:
        for numero in estrazione:
            if 1 <= numero <= 90:
                frequenze[numero] += 1
    return frequenze


def analizza_ritardi(estrazioni_ruota):
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


def genera_consiglio(top_frequenti, top_ritardatari):
    """Genera i consigli di gioco basandosi sulle statistiche."""
    # Ambata consigliata: Il primo ritardatario assoluto
    ambata = top_ritardatari[0][0]

    # Ambo consigliato: Il primo ritardatario + Il primo più frequente
    # (Se coincidono, prende il secondo frequente)
    freq1 = top_frequenti[0][0]
    if freq1 == ambata:
        freq1 = top_frequenti[1][0]

    ambo = [ambata, freq1]

    # Lunghetta/Terno: I primi 2 ritardatari + I primi 2 frequenti
    lunghetta = list(
        dict.fromkeys(
            [
                top_ritardatari[0][0],
                top_ritardatari[1][0],
                top_frequenti[0][0],
                top_frequenti[1][0],
            ]
        )
    )

    return {
        "ambata": ambata,
        "ambo": ambo,
        "quartina": lunghetta,
    }


def main():
    file_ingresso = "estrazioni.json"
    file_uscita = "risultati_v4.json"

    dati = carica_estrazioni(file_ingresso)
    if not dati:
        return

    risultati_finali = {}

    for ruota, estrazioni in dati.items():
        if not estrazioni:
            continue

        freq = analizza_frequenze(estrazioni)
        rit = analizza_ritardi(estrazioni)

        top_frequenti = sorted(freq.items(), key=lambda x: x[1], reverse=True)[
            :5
        ]
        top_ritardatari = sorted(
            rit.items(), key=lambda x: x[1], reverse=True
        )[:5]

        # Genera le giocate consigliate
        consiglio = genera_consiglio(top_frequenti, top_ritardatari)

        risultati_finali[ruota] = {
            "totale_estrazioni_analizzate": len(estrazioni),
            "top_frequenti": [
                {"numero": num, "frequenza": f} for num, f in top_frequenti
            ],
            "top_ritardatari": [
                {"numero": num, "ritardo": r} for num, r in top_ritardatari
            ],
            "consiglio_gioco": consiglio,
        }

    with open(file_uscita, "w", encoding="utf-8") as f:
        json.dump(risultati_finali, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    main()

import json
import os


def carica_estrazioni(filepath):
    if not os.path.exists(filepath):
        print(f"❌ Errore: Il file '{filepath}' non esiste.")
        return None

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Errore durante la lettura: {e}")
        return None

    estrazioni_pulite = {}
    for ruota, estrazioni in data.items():
        estrazioni_pulite[ruota] = [
            [int(n) for n in est] for est in estrazioni
        ]

    return estrazioni_pulite


def calcola_statistiche_ruota(estrazioni):
    totale = len(estrazioni)

    # 1. Frequenze Generali
    freq_totali = {n: 0 for n in range(1, 91)}
    for est in estrazioni:
        for num in est:
            if 1 <= num <= 90:
                freq_totali[num] += 1

    # 2. Ritardi Attuali
    ritardi = {n: 0 for n in range(1, 91)}
    for num in range(1, 91):
        r = 0
        trovato = False
        for est in reversed(estrazioni):
            if num in est:
                trovato = True
                break
            r += 1
        ritardi[num] = r if trovato else totale

    # 3. Trend Recente (Ultime 18 estrazioni ~ 1 mese e mezzo di gioco)
    recenti = estrazioni[-18:] if totale >= 18 else estrazioni
    freq_recenti = {n: 0 for n in range(1, 91)}
    for est in recenti:
        for num in est:
            if 1 <= num <= 90:
                freq_recenti[num] += 1

    return freq_totali, ritardi, freq_recenti


def pronostico_lottologo(freq_totali, ritardi, freq_recenti):
    """Algoritmo avanzato di selezione delle combinazioni."""
    # Ordiniamo i dati
    top_ritardatari = sorted(ritardi.items(), key=lambda x: x[1], reverse=True)
    top_frequenti = sorted(
        freq_totali.items(), key=lambda x: x[1], reverse=True
    )
    top_caldi = sorted(freq_recenti.items(), key=lambda x: x[1], reverse=True)

    # A. AMBATA CAPOGIOCO: Il maggior ritardatario
    ambata = top_ritardatari[0][0]

    # B. PRIMO ABBINAMENTO: Il numero più "caldo" delle ultime 18 estrazioni (diverso dall'ambata)
    abbinamento_caldo = next(
        num for num, f in top_caldi if num != ambata
    )

    # C. SECONDO ABBINAMENTO: Numero frequente con Decina e Parità differenti (Filtro Simmetrico)
    decina_ambata = ambata // 10
    parita_ambata = ambata % 2

    abbinamento_simmetrico = None
    for num, _ in top_frequenti:
        if num != ambata and num != abbinamento_caldo:
            decina_num = num // 10
            parita_num = num % 2
            # Cerchiamo un numero con decina diversa e parità opposta
            if decina_num != decina_ambata and parita_num != parita_ambata:
                abbinamento_simmetrico = num
                break

    # Se il filtro è troppo stretto, prendiamo il secondo più frequente
    if not abbinamento_simmetrico:
        abbinamento_simmetrico = next(
            num
            for num, _ in top_frequenti
            if num != ambata and num != abbinamento_caldo
        )

    # D. TERZO ABBINAMENTO (per la Quartina): Secondo ritardatario assoluto
    secondo_ritardatario = next(
        num for num, _ in top_ritardatari if num != ambata
    )

    # Composizione Giocate
    ambo_secco = [ambata, abbinamento_caldo]
    quartina = list(
        dict.fromkeys(
            [
                ambata,
                abbinamento_caldo,
                abbinamento_simmetrico,
                secondo_ritardatario,
            ]
        )
    )

    return {
        "ambata": ambata,
        "ambo": ambo_secco,
        "quartina": quartina,
        "top_frequenti": [
            {"numero": n, "frequenza": f} for n, f in top_frequenti[:5]
        ],
        "top_ritardatari": [
            {"numero": n, "ritardo": r} for n, r in top_ritardatari[:5]
        ],
    }


def main():
    file_ingresso = "estrazioni.json"
    file_uscita = "risultati_v4.json"

    dati = carica_estrazioni(file_ingresso)
    if not dati:
        print("Impossibile procedere: dati non validi o mancanti.")
        return

    risultati_finali = {}

    for ruota, estrazioni in dati.items():
        if not estrazioni:
            continue

        freq_tot, ritardi, freq_rec = calcola_statistiche_ruota(estrazioni)
        analisi = pronostico_lottologo(freq_tot, ritardi, freq_rec)

        risultati_finali[ruota] = {
            "totale_estrazioni_analizzate": len(estrazioni),
            "top_frequenti": analisi["top_frequenti"],
            "top_ritardatari": analisi["top_ritardatari"],
            "consiglio_gioco": {
                "ambata": analisi["ambata"],
                "ambo": analisi["ambo"],
                "quartina": analisi["quartina"],
            },
        }

    try:
        with open(file_uscita, "w", encoding="utf-8") as f:
            json.dump(risultati_finali, f, indent=4, ensure_ascii=False)
        print(f"✅ Analisi completata! File '{file_uscita}' aggiornato.")
    except Exception as e:
        print(f"❌ Errore durante il salvataggio: {e}")


if __name__ == "__main__":
    main()

import json
import os


def diagnostica_e_analizza(filepath):
    print(f"1. Verifico esistenza file '{filepath}'...")

    if not os.path.exists(filepath):
        print(
            f"   ❌ ERRORE: Il file '{filepath}' NON esiste in questa cartella!"
        )
        print(f"   📁 Cartella attuale di lavoro: {os.getcwd()}")
        return

    print("   ✅ File trovato!\n")

    print("2. Tento la lettura del file JSON...")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        print("   ✅ JSON caricato con successo!")
    except Exception as e:
        print(f"   ❌ ERRORE nel leggere il JSON: {e}")
        return

    print(f"\n3. Contenuto trovato nel JSON:")
    print(f"   - Tipo di dato principale: {type(data)}")

    if isinstance(data, dict):
        print(f"   - Chiavi (ruote) trovate: {list(data.keys())}")
        for ruota, estrazioni in data.items():
            print(
                f"   - Ruota '{ruota}': contiene {len(estrazioni)} estrazioni."
            )
            if len(estrazioni) > 0:
                print(
                    f"     Esempio prima estrazione: {estrazioni[0]} (tipo elementi: {[type(x) for x in estrazioni[0]]})"
                )
    else:
        print(
            "   ⚠️ Il JSON non è un dizionario con le ruote, ma un altro tipo di dato."
        )
        return

    print("\n==========================================")
    print("         INIZIO ANALISI DATI              ")
    print("==========================================")

    for ruota, estrazioni in data.items():
        if not estrazioni:
            continue

        # Convertiamo in interi
        estrazioni_int = []
        for est in estrazioni:
            estrazioni_int.append([int(x) for x in est])

        # Frequenze
        freq = {n: 0 for n in range(1, 91)}
        for est in estrazioni_int:
            for num in est:
                if 1 <= num <= 90:
                    freq[num] += 1

        # Ritardi
        rit = {n: 0 for n in range(1, 91)}
        for num in range(1, 91):
            r = 0
            trovato = False
            for est in reversed(estrazioni_int):
                if num in est:
                    trovato = True
                    break
                r += 1
            rit[num] = r if trovato else len(estrazioni_int)

        top_freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:5]
        top_rit = sorted(rit.items(), key=lambda x: x[1], reverse=True)[:5]

        print(f"\n📍 RUOTA DI {ruota.upper()} ({len(estrazioni_int)} estrazioni)")
        print("  Top 5 Frequenti  :", [f"N.{n} ({f}v)" for n, f in top_freq])
        print("  Top 5 Ritardatari:", [f"N.{n} ({r}r)" for n, r in top_rit])


# Esegui la diagnostica
diagnostica_e_analizza("estrazioni.json")

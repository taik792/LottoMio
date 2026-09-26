import os

def main():
    # Stampa a schermo della Top 5 reale per i colpi 2-5 elaborata sul backtest generale
    print("\n" + "="*65)
    print("🏆 CLASSIFICA TOP 5 CONFIGURAZIONI: FASCIA D'ORO (COLPI 2-5) 🏆")
    print("=================================================================")
    top_5 = [
        {"pos": "1°", "b": "TORINO", "r": "NAPOLI", "f": 31, "oro": "3.15% (124 Ambi)", "tot": "6.15% (242 Ambi)"},
        {"pos": "2°", "b": "NAPOLI", "r": "FIRENZE", "f": 1, "oro": "3.13% (123 Ambi)", "tot": "6.12% (241 Ambi)"},
        {"pos": "3°", "b": "MILANO", "r": "FIRENZE", "f": 2, "oro": "3.09% (122 Ambi)", "tot": "5.98% (236 Ambi)"},
        {"pos": "4°", "b": "BARI", "r": "ROMA", "f": 44, "oro": "2.98% (118 Ambi)", "tot": "5.72% (226 Ambi)"},
        {"pos": "5°", "b": "FIRENZE", "r": "MILANO", "f": 10, "oro": "2.68% (106 Ambi)", "tot": "5.56% (219 Ambi)"}
    ]
    for c in top_5:
        print(f"🏅 {c['pos']} POSTO: Ruota Base [{c['b']}] + Ruota Recupero [{c['r']}] | Fisso: +{c['f']}")
        print(f"   📊 Fascia Oro (2-5 c.): {c['oro']} | Ciclo Totale (1-9 c.): {c['tot']}")
        print("-" * 65)

if __name__ == "__main__":
    main()

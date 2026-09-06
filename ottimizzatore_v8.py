import json
import os

def fuori_90(numero):
    while numero > 90: numero -= 90
    while numero <= 0: numero += 90
    return numero

def calcola_diametrale(numero):
    if numero <= 45: return numero + 45
    return numero - 45

def scopri_fisso_migliore():
    if not os.path.exists('estrazioni.json'):
        print("Errore: estrazioni.json non trovato.")
        return

    with open('estrazioni.json', 'r', encoding='utf-8') as f:
        archivio = json.load(f)

    ruote = {k.upper(): v for k, v in archivio.items() if isinstance(v, list)}
    if "BARI" not in ruote or "MILANO" not in ruote: return

    estrazioni_bari = ruote["BARI"]
    estrazioni_milano = ruote["MILANO"]
    tot_estrazioni = len(estrazioni_bari)
    
    classifica_fisso = []

    print("Analisi di ottimizzazione in corso sui 90 numeri fissi...")

    # Testiamo ogni possibile numero fisso da 1 a 90
    for fisso in range(1, 91):
        vincite_ambata = 0
        vincite_ambo = 0
        totale_previsioni = 0

        for i in range(tot_estrazioni - 9):
            if not estrazioni_bari[i] or len(estrazioni_bari[i]) < 1: continue
            
            primo_bari = int(estrazioni_bari[i][0])
            ambata = fuori_90(primo_bari + fisso)
            abbinamento = calcola_diametrale(ambata)
            
            totale_previsioni += 1
            vinta_ambata = False
            vinto_ambo = False

            for colpo in range(1, 10):
                idx = i + colpo
                num_ba = [int(n) for n in estrazioni_bari[idx][:5]]
                num_mi = [int(n) for n in estrazioni_milano[idx][:5]]

                if not vinta_ambata and ((ambata in num_ba) or (ambata in num_mi)):
                    vincite_ambata += 1
                    vinta_ambata = True

                if not vinto_ambo:
                    if (ambata in num_ba and abbinamento in num_ba) or (ambata in num_mi and abbinamento in num_mi):
                        vincite_ambo += 1
                        vinto_ambo = True

        if totale_previsioni > 0:
            p_ambata = (vincite_ambata / totale_previsioni) * 100
            p_ambo = (vincite_ambo / totale_previsioni) * 100
            classifica_fisso.append({
                "fisso": fisso,
                "perc_ambata": p_ambata,
                "perc_ambo": p_ambo,
                "vincite_ambo": vincite_ambo
            })

    # Ordiniamo la classifica per percentuale di ambata più alta
    classifica_fisso.sort(key=lambda x: x["perc_ambata"], reverse=True)

    print("=" * 65)
    print("      🏆 I 3 MIGLIORI FISSI PER AMBATA (Bari + Fisso) 🏆      ")
    print("=" * 65)
    for idx, item in enumerate(classifica_fisso[:3]):
        print(f"{idx+1}° Posto -> Fisso: +{item['fisso']} | Ambata: {item['perc_ambata']:.2f}% | Ambi Vinti: {item['vincite_ambo']} ({item['perc_ambo']:.2f}%)")

    # Ordiniamo la classifica per numero di ambi vinti
    classifica_fisso.sort(key=lambda x: x["vincite_ambo"], reverse=True)

    print("\n" + "=" * 65)
    print("      🔥 I 3 MIGLIORI FISSI PER AMBO SECCO (Diametrale) 🔥     ")
    print("=" * 65)
    for idx, item in enumerate(classifica_fisso[:3]):
        print(f"{idx+1}° Posto -> Fisso: +{item['fisso']} | Ambi Vinti: {item['vincite_ambo']} ({item['perc_ambo']:.2f}%) | Ambata: {item['perc_ambata']:.2f}%")

if __name__ == "__main__":
    scopri_fisso_migliore()

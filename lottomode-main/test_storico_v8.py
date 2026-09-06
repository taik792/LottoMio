import json
import os

def fuori_90(numero):
    while numero > 90: numero -= 90
    while numero <= 0: numero += 90
    return numero

def calcola_diametrale(numero):
    if numero <= 45: return numero + 45
    return numero - 45

def esegui_backtest():
    if not os.path.exists('estrazioni.json'):
        print("Errore: Il file estrazioni.json non esiste in questa cartella.")
        return

    with open('estrazioni.json', 'r', encoding='utf-8') as f:
        archivio_completo = json.load(f)

    # Pulizia delle ruote e standardizzazione in maiuscolo
    ruote_pulite = {k.upper(): v for k, v in archivio_completo.items() if isinstance(v, list)}
    
    if "BARI" not in ruote_pulite or "MILANO" not in ruote_pulite:
        print("Errore: Ruote di BARI o MILANO non trovate nell'archivio.")
        return

    estrazioni_bari = ruote_pulite["BARI"]
    estrazioni_milano = ruote_pulite["MILANO"]
    tot_estrazioni = len(estrazioni_bari)

    # Variabili per le statistiche
    totale_previsioni = 0
    vincite_ambata = 0
    vincite_ambo = 0
    colpi_totale_ambata = 0

    print("=" * 60)
    print("        REPORT DI BACKTESTING - LOTTO ISOTOPO V8        ")
    print("=" * 60)

    # Ciclo su tutte le estrazioni storiche (lasciamo le ultime 9 fuori perché non avrebbero i colpi per completarsi)
    for i in range(tot_estrazioni - 9):
        # 1. Trova la condizione di partenza (1° di Bari)
        estrazione_corrente_bari = estrazioni_bari[i]
        if not estrazione_corrente_bari or len(estrazione_corrente_bari) < 1:
            continue
            
        primo_bari = int(estrazione_corrente_bari[0])
        
        # 2. Calcola la previsione con le tue formule
        ambata = fuori_90(primo_bari + 15)
        abbinamento = calcola_diametrale(ambata)
        ambo_secco = [ambata, abbinamento]
        
        totale_previsioni += 1
        vinta_ambata_qua = False
        vinto_ambo_qua = False
        
        # 3. Controlla i 9 colpi successivi (da i+1 a i+9)
        for colpo in range(1, 10):
            indice_estrazione = i + colpo
            
            # Estrazioni reali nei colpi successivi su Bari e Milano
            num_bari_futuri = [int(n) for n in estrazioni_bari[indice_estrazione][:5]]
            num_milano_futuri = [int(n) for n in estrazioni_milano[indice_estrazione][:5]]
            
            # Controllo Ambata
            if not vinta_ambata_qua:
                if (ambata in num_bari_futuri) or (ambata in num_milano_futuri):
                    vincite_ambata += 1
                    colpi_totale_ambata += colpo
                    vinta_ambata_qua = True
                    print(f"[OK] Ambata {ambata} vinta al {colpo}° colpo (Calcolata da 1° Ba: {primo_bari})")
            
            # Controllo Ambo Secco (entrambi i numeri devono essere nella stessa ruota nello stesso colpo)
            if not vinto_ambo_qua:
                ambo_su_bari = ambo_secco[0] in num_bari_futuri and ambo_secco[1] in num_bari_futuri
                ambo_su_milano = ambo_secco[0] in num_milano_futuri and ambo_secco[1] in num_milano_futuri
                if ambo_su_bari or ambo_su_milano:
                    vincite_ambo += 1
                    vinto_ambo_qua = True
                    ruota_vincita = "BARI" if ambo_su_bari else "MILANO"
                    print(f"🌟 [BOOM] AMBO SECCO {ambo_secco[0]}-{ambo_secco[1]} su {ruota_vincita} al {colpo}° colpo!")

    # 4. Calcolo e stampa delle percentuali finali
    if totale_previsioni > 0:
        perc_ambata = (vincite_ambata / totale_previsioni) * 100
        perc_ambo = (vincite_ambo / totale_previsioni) * 100
        media_colpi = colpi_totale_ambata / vincite_ambata if vincite_ambata > 0 else 0
        
        print("=" * 60)
        print("                      STATISTICHE FINALI                    ")
        print("=" * 60)
        print(f"Previsioni totali analizzate: {totale_previsioni}")
        print(f"Ambate vinte: {vincite_ambata} ({perc_ambata:.2f}%)")
        print(f"Ambi secchi vinti: {vincite_ambo} ({perc_ambo:.2f}%)")
        if vincite_ambata > 0:
            print(f"Velocità media di uscita ambata: {media_colpi:.1f} colpi")
    else:
        print("Non ci sono abbastanza estrazioni storiche per fare il test.")

if __name__ == "__main__":
    esegui_backtest()

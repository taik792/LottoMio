import json
import os

FISSO_OTTIMIZZATO = 31
RUOTA_BASE_SIGLA = "TO"      
RUOTA_RECUPERO_SIGLA = "NA"   
RUOTA_BASE_NOME = "TORINO"
RUOTA_RECUPERO_NOME = "NAPOLI"

FILE_ESTRAZIONI = "estrazioni.json"
FILE_RISULTATI = "risultati_v4.json"

def fuori_90(numero):
    while numero > 90: numero -= 90
    while numero < 1: numero += 90
    return numero

def calcola_diametrale(numero):
    return numero + 45 if numero <= 45 else numero - 45

def analizza_file_estrazioni():
    if not os.path.exists(FILE_ESTRAZIONI):
        return []
    cronologia = {}
    with open(FILE_ESTRAZIONI, "r", encoding="utf-8") as f:
        for riga in f:
            riga = riga.strip()
            if not riga: continue
            parti = riga.split("\t")
            if len(parti) < 7: continue
            data = parti[0]
            ruota = parti[1]
            try:
                numeri = [int(x) for x in parti[2:7]]
            except ValueError: continue
            if data not in cronologia: cronologia[data] = {}
            cronologia[data][ruota] = numeri
    return [{"data": d, "ruote": cronologia[d]} for d in sorted(list(cronologia.keys()))]

def main():
    estrazioni = analizza_file_estrazioni()
    if not estrazioni:
        print("Errore: Nessun dato trovato in estrazioni.json")
        return

    tot_estrazioni = len(estrazioni)
    ultima_estrazione = estrazioni[-1]
    data_attuale = ultima_estrazione["data"]
    
    numeri_to = ultima_estrazione["ruote"].get(RUOTA_BASE_SIGLA, [])
    primo_estratto = numeri_to[0] if numeri_to else 10
    
    ambata = fuori_90(primo_estratto + FISSO_OTTIMIZZATO)
    ambo_secco = calcola_diametrale(ambata)
    d_p1 = fuori_90(ambo_secco + 1)
    d_m1 = fuori_90(ambo_secco - 1)

    previsioni_output = {
        RUOTA_BASE_NOME: {
            "ambata": ambata, "ambo": [ambata, ambo_secco], "ambetti": [[ambata, d_p1], [ambata, d_m1]]
        },
        RUOTA_RECUPERO_NOME: {
            "ambata": ambata, "ambo": [ambata, ambo_secco], "ambetti": [[ambata, d_p1], [ambata, d_m1]]
        }
    }

    storico_verificato = []
    # Generazione automatica lineare dei colpi reali passati
    for indietro in range(1, 11):
        idx = tot_estrazioni - 1 - indietro
        if idx < 0: continue
        est_passata = estrazioni[idx]
        num_to_p = est_passata["ruote"].get(RUOTA_BASE_SIGLA, [])
        if not num_to_p: continue
        
        ambata_p = fuori_90(num_to_p[0] + FISSO_OTTIMIZZATO)
        ambo_p = calcola_diametrale(ambata_p)
        
        stato = "In gioco"
        esito_colpo = ""
        colpi_passati = tot_estrazioni - 1 - idx
        colpi_limite = min(9, colpi_passati)
        
        for colpo in range(1, colpi_limite + 1):
            est_v = estrazioni[idx + colpo]
            n_to = est_v["ruote"].get(RUOTA_BASE_SIGLA, [])
            n_na = est_v["ruote"].get(RUOTA_RECUPERO_SIGLA, [])
            
            if (ambata_p in n_to and ambo_p in n_to) or (ambata_p in n_na and ambo_p in n_na):
                stato = "Ambo Vincente"
                esito_colpo = f"Esito al {colpo}° colpo"
                break
            elif ambata_p in n_to or ambata_p in n_na:
                stato = "Ambata Vincente"
                esito_colpo = f"Esito al {colpo}° colpo"
                break
                
        if stato == "In gioco":
            if colpi_passati < 9:
                esito_colpo = f"{colpi_passati + 1}° Colpo"
            else:
                stato = "Finito Negativo"
                esito_colpo = "Fuori colpi"

        storico_verificato.append({
            "data": est_passata["data"],
            "ruote": f"{RUOTA_BASE_NOME} - {RUOTA_RECUPERO_NOME}",
            "ambata": ambata_p,
            "ambo": f"{ambata_p} - {ambo_p}",
            "colpi": esito_colpo,
            "stato": stato
        })

    with open(FILE_RISULTATI, "w", encoding="utf-8") as f:
        json.dump({"info_concorso": {"numero": "Lotto Intelligence V8", "data": data_attuale}, "previsioni": previsioni_output, "storico_verificato": storico_verificato}, f, indent=4, ensure_ascii=False)
    print("✅ risultati_v4.json generato.")

if __name__ == "__main__":
    main()

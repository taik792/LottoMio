import json
import os

def inserimento_riservato_amministratore(nome_file="estrazioni.json"):
    # 1. Controllo presenza file
    if not os.path.exists(nome_file):
        print(f"❌ Errore: Il file {nome_file} non è stato trovato nella cartella corrente.")
        return

    # 2. Caricamento del database esistente
    with open(nome_file, "r", encoding="utf-8") as f:
        database = json.load(f)

    print("==========================================================")
    print(" 🔐 INTERFACCIA DI INSERIMENTO ESTRAZIONI (RISERVATO A TE)")
    print("==========================================================")
    print("Nota: I dati verranno inseriti in fondo (dal più vecchio al più giovane).\n")

    # Elenco esatto delle ruote del tuo file JSON
    ruote = ["Bari", "Cagliari", "Firenze", "Genova", "Milano", "Napoli", "Palermo", "Roma", "Torino", "Venezia"]
    nuova_estrazione = {}

    # 3. Raccolta dati ruota per ruota
    for ruota in ruote:
        while True:
            try:
                print(f"➡️ Ruota di {ruota.upper()}:")
                stringa_numeri = input("   Inserisci i 5 numeri separati da uno spazio: ").strip()
                
                # Separa la stringa e trasforma in numeri interi
                numeri = [int(n) for n in stringa_numeri.split()]
                
                # Controllo di sicurezza: devono essere esattamente 5 numeri
                if len(numeri) != 5:
                    print("   ⚠️ Errore! Devi inserire esattamente 5 numeri (es: 12 45 67 89 2). Riprova.")
                    continue
                
                # Controllo di sicurezza: i numeri del lotto vanno da 1 a 90
                if any(n < 1 or n > 90 for n in numeri):
                    print("   ⚠️ Errore! I numeri del lotto devono essere compresi tra 1 e 90. Riprova.")
                    continue
                
                # Se tutto è ok, salva temporaneamente i numeri di questa ruota
                nuova_estrazione[ruota] = numeri
                break
                
            except ValueError:
                print("   ⚠️ Errore! Inserisci solo numeri interi validi separati da uno spazio. Riprova.")

    # 4. Riepilogo e Conferma di sicurezza prima di scrivere sul file
    print("\n==========================================================")
    print(" RIEPILOGO NUOVA ESTRAZIONE DA INSERIRE:")
    print("==========================================================")
    for ruota, numeri in nuova_estrazione.items():
        print(f"• {ruota}: {numeri}")
    print("==========================================================")
    
    conferma = input("\nSei sicuro che i dati siano corretti? Salvo nel database? (s/n): ").strip().lower()

    if conferma == 's':
        # 5. Eseguiamo il .append() alla fine della lista per mantenere l'ordine cronologico
        for ruota in ruote:
            database[ruota].append(nuova_estrazione[ruota])
        
        # 6. Sovrascriviamo il file JSON mantenendo la stessa formattazione ordinata
        with open(nome_file, "w", encoding="utf-8") as f:
            json.dump(database, f, indent=2, ensure_ascii=False)
            
        print("\n✅ Perfetto! L'estrazione è stata inserita correttamente in fondo al file.")
        print("Adesso puoi avviare il motore per generare i nuovi risultati per il sito!")
    else:
        print("\n❌ Operazione annullata. Nessun dato è stato modificato.")

if __name__ == "__main__":
    inserimento_riservato_amministratore()

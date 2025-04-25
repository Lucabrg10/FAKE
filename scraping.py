import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
import html

# 2. Funzione per estrarre la trascrizione dal JSON nella pagina
def get_transcript(slug):
    url = f"https://www.ted.com/talks/{slug}/transcript"
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Cerca il blocco <script type="application/ld+json">
        script_tag = soup.find("script", type="application/ld+json")
        if script_tag:
            data = json.loads(script_tag.string)
            raw_transcript = data.get("transcript", "").strip()

            # 🔽 Decodifica entità HTML
            clean_transcript = html.unescape(raw_transcript)
            return clean_transcript if clean_transcript else None
        else:
            return None

    except Exception as e:
        print(f"Errore con slug {slug}: {e}")
        return None

# 3. Script principale (solo primi 10)
def main():
    # Carica il file CSV locale
    df = pd.read_csv("final_list.csv")

    transcripts = []
    for i, row in df.iterrows():
        slug = row['slug']
        print(f"Scarico trascrizione per: {slug}")
        transcript = get_transcript(slug)
        transcripts.append(transcript)

    # Aggiungi la colonna delle trascrizioni al DataFrame
    df['transcript'] = transcripts

    # Salva il risultato in un nuovo file CSV nella stessa cartella
    df.to_csv("final_with_transcripts_10.csv", index=False)
    print("✅ Completato! File salvato come final_with_transcripts_10.csv")

# 4. Esegui il main
if __name__ == "__main__":
    main()

---
name: estrai-sito
description: Copia nel workspace il contenuto di un sito (pagine, schede prodotto, PDF, Excel, link ai video), legge tutti i documenti scaricati e scrive un README con l'analisi; se esiste già una copia, la aggiorna e dice cosa è cambiato. Usa questa skill quando l'agente dice "copia il sito MAK/NPK/MATE/TRK", "scarica il sito agenti", "estrai il sito X in Siti/Y", "aggiorna la copia del sito", o porta il sito di un concorrente o di un fornitore da studiare.
---

# estrai-sito — un sito dentro il workspace, letto per intero

Le copie dei siti stanno in `Siti/<NOME>/`. Gli script sono già pronti in `Siti/_script/` e sono stati provati sui siti MAK: usali, non riscriverli. Se uno script si rompe (il sito è cambiato), correggilo e dillo all'agente.

## I siti MAK

| Cartella | Sito | Come si copia |
|---|---|---|
| `Siti/NPK` | https://noproblemkit.com | `python3 Siti/_script/scarica_sito.py --sito https://noproblemkit.com --cartella NPK --escludi "ground_catalog\|antifurti"`, poi i configuratori con `python3 Siti/_script/npk_dati.py` (circa mezz'ora, CSV in `Siti/NPK/dati/`) |
| `Siti/MATE` | https://www.mate-tech.it | `python3 Siti/_script/scarica_sito.py --sito https://www.mate-tech.it --cartella MATE` |
| `Siti/MAK` | https://makwheels.it | `python3 Siti/_script/scarica_sito.py --sito https://makwheels.it --cartella MAK` (oltre 500 articoli di news: chiedi all'agente se li vuole o se bastano `--tipi prodotti,pagine,promozioni,testimonial`) |
| `Siti/TRK` | https://trkwheels.it | `python3 Siti/_script/scarica_sito.py --sito https://trkwheels.it --cartella TRK` |
| `Siti/EBOOK` | sito riservato agli agenti (Google Site) | vedi «Il sito agenti» qui sotto |

Su Windows al posto di `python3` si scrive `python`, e al posto di `.venv/bin/python` si scrive `.venv\Scripts\python`.

## Regole

- **Prima conta, poi scarica.** Lancia lo script con `--conta` e mostra all'agente quante pagine ci sono. Se sono più di 300, chiedi conferma prima di scaricare.
- **Con calma.** Gli script fanno una richiesta alla volta, con una pausa. Se il sito risponde 403 o 429, lo script si ferma da solo: dillo all'agente e riprova più tardi. Il rilancio riparte da dove si era fermato.
- **Leggi tutto.** Dopo lo scarico, `.venv/bin/python Siti/_script/estrai_testo.py --cartella <NOME>` estrae il testo di ogni PDF, Excel, Word e PowerPoint. I PDF segnati «SOLO IMMAGINI» li guardi come immagini: `pdftoppm -r 80 -png <file> <prefisso>`, poi leggi le immagini. A fine lavoro di' quanti file sono stati scaricati e quanti letti, e nomina quelli che non sei riuscito a leggere.
- **Cataloghi sfogliabili** (flippingbook, issuu): lo script non li prende. Cercali nelle pagine «Download» o «Cataloghi» del sito. Di solito hanno un pulsante «Scarica PDF»: scarica il PDF in `Siti/<NOME>/flippingbook/` e leggilo come gli altri.
- **Niente su GitHub.** Le copie dei siti sono escluse dal `.gitignore` del workspace (solo `Siti/_script/` e `Siti/README.md` vanno in git). Prima di un commit controlla con `git status`.

## Il sito agenti

È riservato: serve il login Google dell'agente. **Non chiedere mai password e non scriverle da nessuna parte.**

1. L'agente apre il Chrome dedicato:
   - Mac: `zsh Siti/_script/avvia_chrome_ebook.sh`
   - Windows: `powershell -ExecutionPolicy Bypass -File Siti\_script\avvia_chrome_ebook.ps1`
2. Fa il login nella finestra che si apre e aspetta di vedere la home del sito.
3. Tu lanci, in ordine:
   - `.venv/bin/python Siti/_script/ebook_pagine.py` (pagine, immagini, `collegamenti.csv`);
   - `.venv/bin/python Siti/_script/ebook_file.py` (i file Drive; video e file oltre 50 MB restano solo elencati in `file.csv`);
   - `estrai_testo.py --cartella EBOOK`.
4. La finestra di quel Chrome deve restare aperta finché gli script lavorano. Se una connessione viene rifiutata («Browser context management is not supported»): fai chiudere quel Chrome all'agente, riaprilo con il punto 1 e rilancia. Gli script riprendono da dove si erano fermati.

Il materiale del sito agenti contiene prezzi netti, accordi e regole riservate alla rete agenti: resta su questo computer, mai online, mai in pagine pubblicate.

## Cosa deve esserci alla fine in `Siti/<NOME>/`

| Percorso | Contenuto |
|---|---|
| `pagine/`, `prodotti/`, `articoli/`… | una pagina = un file Markdown, con titolo, URL e data |
| `download/` | PDF ed Excel scaricati |
| `testo/` e `testo.csv` | il testo estratto di ogni documento e l'esito |
| `video.md` | i link ai video trovati (i video non si scaricano) |
| `indice.csv` | elenco di pagine e documenti |
| `README.md` | lo scrivi tu (vedi sotto) |

## Il README della copia

Scrivi `Siti/<NOME>/README.md` con:
- data della copia e numeri: pagine per tipo, documenti scaricati, documenti letti, video;
- com'è fatto il sito: sezioni, cosa c'è dove;
- cosa dice di utile per vendere: gamme, novità, argomenti, promozioni al pubblico;
- difetti trovati: pagine vuote, link rotti, dati che non tornano;
- contraddizioni con il materiale che l'agente ha già in `Listini/` o con gli altri siti (prezzi, codici, misure, nomi), con la fonte di ciascuna versione.

## Aggiornare una copia esistente

1. Rinomina `README.md` in `README-<data della copia vecchia>.md`.
2. Rilancia lo script con `--aggiorna`.
3. In testa al README nuovo scrivi «Cosa è cambiato dal <data>»: pagine e prodotti nuovi o spariti, prezzi cambiati, documenti nuovi.

## Alla fine

1. Proponi all'agente l'ingest nel wiki con la skill `wiki` (un sito per volta, in una conversazione nuova).
2. Resoconto in poche righe:
   - cosa c'è;
   - quanti file scaricati e quanti letti;
   - le 3-5 cose più utili per la vendita;
   - le contraddizioni da chiarire con l'azienda.

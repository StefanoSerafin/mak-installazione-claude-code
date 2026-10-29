# Wiki MAK — schema

Il mio second brain di agente MAK S.p.A., costruito con il metodo «LLM Wiki» di Andrej Karpathy (https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f), lo stesso visto nel modulo 1 del corso avanzato di Raffaele Gaito.

Claude scrive e mantiene le pagine; io leggo, indirizzo e faccio domande. Al posto di ricercare ogni volta tra PDF e siti, Claude legge le fonti una volta, le riassume in pagine collegate tra loro e poi risponde partendo dal wiki.

## I tre livelli

1. **Sorgenti**: le copie dei siti in `../Siti/`, i listini e i cataloghi in `../Listini/`, gli appunti in `../Clienti/`. Non si modificano e non si copiano qui dentro: si leggono.
2. **Wiki**: `wiki/`, pagine Markdown. Le scrive solo Claude.
3. **Schema**: questo file. Si aggiorna insieme a me quando una convenzione cambia.

## Struttura

| Cartella | Contenuto |
|---|---|
| `wiki/MAK/` | ruote in lega: gamme, modelli, finiture, tecnica (ET, PCD, foro centrale, canale, omologazioni NAD, ETRTO), accessori |
| `wiki/MATE/` | sensori TPMS, strumenti di diagnosi e programmazione, wallbox, procedure |
| `wiki/NPK/` | kit ruota di scorta, kit riparazione, antifurti, calze e catene da neve |
| `wiki/TRK/` | ruote truck in lega e in acciaio, marchi distribuiti, accessori truck |
| `wiki/EBOOK/` | sito riservato agenti: condizioni, procedure, promo push, regole. Pagine con `riservato: sì` |
| `wiki/Marketing/` | promozioni, campagne, materiali, eventi, fidelizzazione |
| `wiki/Network/` | network di gommisti e officine, accordi con le case. Niente nomi di clienti |
| `wiki/Clienti/` | clienti rilevanti e i loro dati. Esclusa da git |
| `wiki/Fonti/` | una pagina-riassunto per ogni sorgente o lotto letto |

`index.md` è il catalogo di tutte le pagine. `log.md` è la cronologia. `_templates/` contiene i modelli. `_script/lint.py` controlla la salute del wiki.

Per aggiungere un'area (per esempio `Concorrenza`): si aggiunge una riga nella tabella qui sopra, si crea la cartella con la pagina hub dello stesso nome e la si scrive in `index.md`. Il lint legge le aree da questa tabella.

## Convenzioni delle pagine

Ogni pagina inizia con:

    ---
    tipo: prodotto        # prodotto | concetto | procedura | persona | organizzazione | network | cliente | progetto | fonte | analisi
    area: NPK             # una delle aree della tabella Struttura
    fonti:                # percorsi relativi alla cartella del workspace; obbligatori per tipo fonte
      - Siti/NPK/README.md
    aggiornato: 2026-11-02
    riservato: no         # sì per materiale riservato agli agenti e dati clienti
    ---

- Lingua italiana. Numeri, codici e misure riportati esattamente come nella sorgente.
- Nome file = titolo della pagina, univoco in tutto il wiki. Se il nome è generico, porta il marchio (`Listino prezzi NPK`).
- Link interni solo con `[[wikilink]]`. Ogni pagina linka la pagina hub della sua area nella riga `Area:`.
- Ogni area ha una pagina hub con lo stesso nome dell'area (`NPK`, `MATE`…) che elenca le sue pagine.
- Ogni affermazione non ovvia rimanda, nella sezione «Fonti», a una pagina di `wiki/Fonti/`. Solo le pagine fonte puntano ai file in `../Siti/` e `../Listini/`.
- Se due sorgenti si contraddicono, entrambe le versioni vanno nella sezione «Da verificare» con la fonte di ciascuna. Mai scegliere in silenzio.
- La sezione «Argomenti di vendita» ha due sottosezioni:
  - **«Dalle sorgenti MAK»**: ciò che dicono siti, cataloghi e documenti;
  - **«Dal mio metodo»**: ciò che ho scritto o detto io.

  Le frasi proposte da Claude non diventano «mio metodo» finché non le approvo.
- Una pagina, un argomento. Sopra le ~300 righe si divide.
- I dati voluminosi (configuratori, listini, tabelle di applicazione) non si ricopiano: la pagina spiega cosa contengono, come leggerli e dove sono.
- I dati di clienti e rivenditori stanno solo in `wiki/Clienti/`. Le pagine cliente non si elencano in `index.md` né in `log.md`: il loro indice è la pagina hub `Clienti`, e nel log si scrive solo quante sono.
- Nelle tabelle l'alias di un link si scrive `[[Pagina\|testo]]`.
- Credenziali, PIN, password, cellulari ed email personali non si scrivono mai nel wiki.

## Procedura: ingest

Si fa **un lotto per conversazione** (un sito, o un gruppo di documenti dello stesso marchio). Finito il lotto: `/clear` e conversazione nuova.

1. Leggere la sorgente, partendo dal testo già estratto: `README.md` della copia, `pagine/`, `prodotti/`, `testo/`. PDF ed Excel grezzi solo se il testo non basta.
2. Leggere `index.md` per sapere quali pagine esistono già.
3. Decidere l'elenco delle pagine da creare e da aggiornare e mostrarmelo prima di scrivere. Per il primo lotto: poche pagine (5-8), da rivedere insieme.
4. Creare la pagina in `wiki/Fonti/` dal modello `_templates/fonte.md`.
5. Creare o aggiornare le pagine dell'area dal modello `_templates/pagina.md`; aggiornare `aggiornato:` su ogni pagina toccata.
6. Aggiornare la pagina hub dell'area e `index.md` (una riga per ogni pagina nuova).
7. Aggiungere la voce in `log.md`.
8. Eseguire `python3 _script/lint.py` (Windows: `python _script\lint.py`) dalla cartella `Second Brain` e correggere fino a zero errori.

## Procedura: query

1. Leggere `index.md`, poi solo le pagine pertinenti.
2. Rispondere citando le pagine usate. Se il wiki non basta, dirlo e andare alla sorgente in `../Siti/` o `../Listini/`.
3. Se la risposta ha valore duraturo (un confronto, un'analisi), proporre di archiviarla come pagina `tipo: analisi` e registrarla in `log.md` come `query`.

## Procedura: lint

1. Eseguire `_script/lint.py`: frontmatter, link rotti, pagine orfane, sorgenti inesistenti, pagine assenti dall'indice.
2. A lettura: contraddizioni tra pagine, affermazioni superate da sorgenti più recenti, concetti citati spesso ma senza pagina propria.
3. Dirmi cosa è stato corretto e cosa richiede una mia decisione; registrare in `log.md` come `lint`.

## Formato di log.md

    ## [AAAA-MM-GG] ingest | Titolo della sorgente o del lotto

    Create: [[Pagina A]], [[Pagina B]]. Aggiornate: [[Pagina C]].
    Note: cosa è rimasto da verificare.

Tipi di voce: `setup`, `ingest`, `query`, `lint`. Il file si scrive solo in fondo: le voci passate non si modificano.

## Stato dei lotti

| Lotto | Area | Sorgente | Stato |
|---|---|---|---|
| 1 | NPK (pilota) | `../Siti/NPK/` | da fare |
| 2 | MATE | `../Siti/MATE/` | da fare |
| 3 | MAK | `../Siti/MAK/` | da fare |
| 4 | TRK | `../Siti/TRK/` | da fare |
| 5 | EBOOK, Marketing, Network | `../Siti/EBOOK/` | da fare |

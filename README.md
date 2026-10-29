# Installare Claude Code — guida per i colleghi agenti MAK

Guida passo per passo, per Mac e per Windows, in due livelli:
- **Livello 1 · Installazione**: Claude Code e tutto quello che serve al corso (Git, VS Code con l'estensione, Homebrew o Chocolatey, GitHub, il workspace MAK di partenza). I colleghi lo seguono **a casa, prima dell'incontro**; all'incontro si guarda lo screenshot della verifica finale e si sistema chi è rimasto indietro.
- **Livello 2 · Siti e wiki** (dal 2026-10-29): Claude copia e legge i siti NPK, MATE, MAK, TRK e il sito agenti, poi costruisce il second brain del collega (metodo LLM Wiki di Karpathy) da aprire in Obsidian. Si fa in più giorni. Link diretto: `…/mak-installazione-claude-code/#livello-2`.

**Online:** https://stefanoserafin.github.io/mak-installazione-claude-code/ (pubblicata il 2026-10-21)

Un solo file di dati, `data/passi.json`, genera tutto il resto: web app, slide, PDF e i due zip. Per cambiare un comando o una spiegazione si tocca solo il JSON e si rigenera.

## Struttura

| File | Ruolo |
|---|---|
| `data/passi.json` | **Unica fonte.** Fasi (ognuna con `livello` 1 o 2), passaggi Mac e Windows, verifiche finali dei due livelli, fonti ufficiali, data di verifica, scadenza |
| `data/build.py` | Controlla il JSON e genera `index.html`, `slides.html`, `claude-workspace-mak.zip` e `livello-2.zip` |
| `data/figure.py` | I disegni schematici di VS Code (SVG inline, versione Mac e Windows) con i punti da cliccare numerati: `panoramica`, `estensioni`, `apri-cartella`, `fiducia`, `tavolozza-code`, `tavolozza-icone`, `login` |
| `index.template.html` | Modello della web app (stile e codice inline, nessuna dipendenza esterna) |
| `index.html` | Web app **generata**: schede Livello 1 / Livello 2 e Mac / Windows, spunte salvate nel browser, pulsanti «Copia». `#livello-2` o `?livello=2` apre il secondo livello. Non modificare a mano |
| `slides.template.html` / `slides.html` | Slide per l'incontro di verifica (frecce per scorrere, F per lo schermo intero). `slides.html` è generato |
| `genera_pdf.sh` | Genera `pdf/guida-mac.pdf`, `pdf/guida-windows.pdf` (livello 1), `pdf/livello-2-mac.pdf` e `pdf/livello-2-windows.pdf` da `index.html` con Chrome headless |
| `starter/Claude Workspace/` | Il workspace di partenza: `CLAUDE.md` da agente MAK con le parti `[[ ]]` da completare, cartelle `Clienti`, `Listini`, `Campagne`, `Tool`, tre skill (`messaggio-settimanale`, `riassunto-visita`, `nuovo-tool`) |
| `claude-workspace-mak.zip` | Lo zip del workspace, **generato** da `build.py`, scaricabile dalla web app |
| `starter-livello-2/` | Cosa aggiunge il livello 2 al workspace (vedi sotto). Contiene `LEGGIMI-LIVELLO-2.md`, che dice a Claude come scompattarlo senza sovrascrivere niente |
| `livello-2.zip` | Lo zip del livello 2, **generato** da `build.py` |
| `sw.js` | Service worker network-first: la guida resta leggibile senza rete dopo la prima apertura |

## Rigenerare

```
python3 data/build.py
./genera_pdf.sh
```

`build.py` si ferma con l'elenco degli errori se un passaggio non ha tutti i campi (`id`, `fase`, `titolo`, `perche`, `fai`, `vedi`, `se_non_va`, `minuti`, `fonte`) o se cita una fase o una fonte che non esiste.

Nel testo, quello che il collega deve scrivere va tra apici inversi (\`così\`): nella pagina compare tra virgolette rosse, che non vengono copiate. Campi facoltativi di un passaggio: `figure` (elenco di disegni di `figure.py`), `comando` (con il pulsante «Copia»), `zip: true` o `zip: 2` (pulsante di download dello zip del livello 1 o del livello 2), `prompt_verifica: true` o `prompt_verifica: 2` (il messaggio di verifica del livello 1 o del 2). Ogni caso di `se_non_va` può avere un suo `comando`.

## Aggiornare

- **Prima di ogni nuovo gruppo di colleghi** ricontrollare i comandi sulle pagine elencate in `fonti` di `passi.json` e aggiornare `verificato` (compare in fondo alla guida e nelle slide). Claude Code cambia spesso.
- **Data dell'incontro**: `scadenza` in formato `AAAA-MM-GG`. Se è `null`, la web app non mostra la frase e il PDF stampa «Da finire entro il ____» da compilare a penna.
- **Correzioni dai colleghi Windows**: vanno nel JSON (nuovi casi in `se_non_va`), poi si rigenera e si ripubblica. Quando un collega avrà completato la guida Windows da cima a fondo, togliere l'avviso «non ancora provata» da `index.template.html`.

## Cosa installa la guida

- **Account**: tutti con lo stesso indirizzo Gmail («Continua con Google» dove c'è), con verifica in due passaggi.
- **VS Code**: estensione Claude Code (Anthropic) più le tre consigliate nel corso: `tomoki1207.pdf` (vscode-pdf), `pomdtr.excalidraw-editor` (Excalidraw), `vscode-icons-team.vscode-icons` (vscode-icons), installate con `code --install-extension`.
- **Programmi** (consigliati nel corso, Modulo 6): Pandoc, FFmpeg, whisper.cpp, Node.js e il motore PDF. Su Mac `brew install pandoc ffmpeg whisper-cpp node` e `brew install --cask basictex`; su Windows `choco install pandoc ffmpeg whisper-cpp miktex nodejs-lts -y`. Nomi verificati il 2026-10-21 su formulae.brew.sh, community.chocolatey.org e Visual Studio Marketplace.

## Verifiche fatte

- **2026-10-21**:
  - comandi controllati su code.claude.com (setup, troubleshoot-install, vs-code), brew.sh, chocolatey.org/install, code.visualstudio.com, git-scm.com, cli.github.com, claude.com/pricing;
  - parte Mac ripercorsa sul Mac di Stefano, controllando che le uscite di `claude --version`, `git --version`, `brew --version` e `gh auth status` corrispondano a «Cosa devi vedere»;
  - zip scompattato in una cartella di prova e messaggio di verifica eseguito con Claude Code: la tabella esce corretta e, per ogni riga non OK, rimanda al passaggio giusto della guida.
- **Windows**: non ancora provato su un PC.

## Differenze rispetto al corso di Gaito (aprile-maggio 2026)

- Per installare Claude Code su Windows **non serve** PowerShell da amministratore: serve solo per Chocolatey.
- Git per Windows è **consigliato**, non obbligatorio: senza, Claude Code usa PowerShell al posto di Git Bash.
- I disegni di VS Code sono schematici (SVG), non screenshot: valgono per Mac e Windows e non mostrano dati personali.

## Cosa non c'è, di proposito

- Niente testo, immagini o skill del corso di Raffaele Gaito: la guida è scritta sulla documentazione ufficiale.
- Niente dati di clienti, PIN o credenziali. Il contatto è «scrivi a Stefano», senza numero, perché la pagina è pubblica.

## Livello 2

Il collega scarica `livello-2.zip` e lo fa scompattare a Claude con le istruzioni di `LEGGIMI-LIVELLO-2.md`: niente viene sovrascritto, il `.gitignore` si unisce a quello che c'è, il `CLAUDE.md` del collega riceve in fondo la sezione «Livello 2».

| In `starter-livello-2/` | Cosa fa |
|---|---|
| `.claude/skills/estrai-sito/` | versione generica della skill `estrai-sito` di Stefano: tabella dei cinque siti con il comando giusto per ciascuno, regole (prima conta, leggere tutto, niente su GitHub), sito agenti con login del collega |
| `.claude/skills/wiki/` | ingest a lotti (un marchio per conversazione, NPK come pilota da 5–8 pagine), query, lint |
| `Siti/_script/scarica_sito.py` | copia di un sito WordPress dalla sitemap: pagine per tipo, documenti, `video.md`, `indice.csv`; `--conta`, `--tipi`, `--escludi`, `--max-pagine`, `--aggiorna`; una richiesta al secondo, si ferma da solo su 403/429, un rilancio riparte da dove era |
| `Siti/_script/estrai_testo.py` | testo di PDF, Excel, Word, PowerPoint in `testo/`, con `testo.csv` e l'elenco dei PDF fatti solo di immagini |
| `Siti/_script/npk_dati.py` | i configuratori di noproblemkit.com in CSV (da `Mak/noproblemkit/_script/scarica_dati.py`, senza la parte zona MI/MB/LO, 2 richieste in parallelo) |
| `Siti/_script/ebook_pagine.py`, `ebook_file.py`, `avvia_chrome_ebook.sh` / `.ps1` | il sito agenti da un Chrome dedicato (`~/.mak-ebook-chrome`, porta 9333) in cui il login lo fa il collega; video e file oltre 50 MB solo elencati |
| `Second Brain/` | schema del wiki adattato da quello di Stefano (aree MAK, MATE, NPK, TRK, EBOOK, Marketing, Network, Clienti; «Dal mio metodo»), modelli, `lint.py` che legge le aree dallo schema, indice, log, hub vuoti, `.obsidian/` con i colori del grafo per area |
| `.gitignore` | fuori da git le copie dei siti (sito agenti compreso), i clienti, `.venv`, PDF ed Excel |

Lo zip è pubblico come la pagina: **non deve contenere niente di Stefano** (pagine del wiki, copie dei siti, dati clienti, credenziali). Prima di ripubblicare: `unzip -p livello-2.zip | grep -i -E "stefano|serafin|passphrase"` deve uscire vuoto.

Le differenze rispetto agli script di Stefano:
- **Immagini del sito agenti** scaricate con urllib e i cookie della sessione. `ctx.request` di playwright 1.64 su Chrome 156 dà «Browser context management is not supported» e rompe le connessioni successive.
- **PyMuPDF** importato come `pymupdf`. L'avviso di deprecazione di `fitz` rompeva la lettura del numero di pagine.

### Verifiche del livello 2

- **2026-10-29**:
  - `scarica_sito.py` provato su makwheels.it, trkwheels.it, mate-tech.it e noproblemkit.com (15 pagine ciascuno), con la scheda ruota APOLLO confrontata con `Mak/Sito Mak/ruote/apollo.md`: stessi dati;
  - `estrai_testo.py` provato su 23 PDF, tutti con testo;
  - `npk_dati.py` avviato e fermato dopo 100 secondi, mentre scaricava regolarmente;
  - sito agenti provato con 3 pagine e 25 file dal Chrome dedicato di Stefano, poi cancellati dalla prova;
  - web app provata con Playwright a larghezza iPhone e desktop (schede, `#livello-2`, spunte, «Copia», download dei due zip).
  - prova da capo a fondo come un collega, in un workspace di prova del livello 1 già compilato, con `claude -p` che eseguiva i messaggi della guida:
    - scompattamento dello zip: nessun file sovrascritto, `.gitignore` esistente unito, sezione aggiunta al CLAUDE.md;
    - ambiente Python creato con il comando della guida;
    - copia di TRK (26 pagine, 5 PDF più 2 flippingbook letti) e di NPK senza configuratori (24 pagine, 7 PDF letti), con README e contraddizioni;
    - lotto pilota del wiki NPK: 8 pagine, lint a 0 errori;
    - messaggio di verifica: tabella corretta, con un falso allarme su `Clienti/README.md` poi corretto nel testo del messaggio.
- **Windows**: non ancora provato.


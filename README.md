# Installare Claude Code — guida per i colleghi agenti MAK

Guida passo per passo, per Mac e per Windows, per installare Claude Code e tutto quello che serve al corso: Git, VS Code con l'estensione, Homebrew o Chocolatey, GitHub e il workspace MAK di partenza. I colleghi la seguono **a casa, prima dell'incontro**; all'incontro si guarda lo screenshot della verifica finale e si sistema chi è rimasto indietro.

**Online:** https://stefanoserafin.github.io/mak-installazione-claude-code/ (da pubblicare)

Un solo file di dati, `data/passi.json`, genera tutto il resto: web app, slide, PDF e zip. Per cambiare un comando o una spiegazione si tocca solo il JSON e si rigenera.

## Struttura

| File | Ruolo |
|---|---|
| `data/passi.json` | **Unica fonte.** Fasi, passaggi Mac e Windows, verifica finale, fonti ufficiali, data di verifica, scadenza |
| `data/build.py` | Controlla il JSON e genera `index.html`, `slides.html`, `claude-workspace-mak.zip` |
| `index.template.html` | Modello della web app (stile e codice inline, nessuna dipendenza esterna) |
| `index.html` | Web app **generata**: schede Mac e Windows, spunte salvate nel browser, pulsanti «Copia». Non modificare a mano |
| `slides.template.html` / `slides.html` | Slide per l'incontro di verifica (frecce per scorrere, F per lo schermo intero). `slides.html` è generato |
| `genera_pdf.sh` | Genera `pdf/guida-mac.pdf` e `pdf/guida-windows.pdf` da `index.html` con Chrome headless |
| `starter/Claude Workspace/` | Il workspace di partenza: `CLAUDE.md` da agente MAK con le parti `[[ ]]` da completare, cartelle `Clienti`, `Listini`, `Campagne`, `Tool`, tre skill (`messaggio-settimanale`, `riassunto-visita`, `nuovo-tool`) |
| `claude-workspace-mak.zip` | Lo zip del workspace, **generato** da `build.py`, scaricabile dalla web app |
| `sw.js` | Service worker network-first: la guida resta leggibile senza rete dopo la prima apertura |

## Rigenerare

```
python3 data/build.py
./genera_pdf.sh
```

`build.py` si ferma con l'elenco degli errori se un passaggio non ha tutti i campi (`id`, `fase`, `titolo`, `perche`, `fai`, `vedi`, `se_non_va`, `minuti`, `fonte`) o se cita una fase o una fonte che non esiste.

Campi facoltativi di un passaggio: `comando` (con il pulsante «Copia»), `zip: true` (pulsante di download del workspace), `prompt_verifica: true` (il messaggio di verifica da incollare in Claude). Ogni caso di `se_non_va` può avere un suo `comando`.

## Aggiornare

- **Prima di ogni nuovo gruppo di colleghi** ricontrollare i comandi sulle pagine elencate in `fonti` di `passi.json` e aggiornare `verificato` (compare in fondo alla guida e nelle slide). Claude Code cambia spesso.
- **Data dell'incontro**: `scadenza` in formato `AAAA-MM-GG`. Se è `null`, la web app non mostra la frase e il PDF stampa «Da finire entro il ____» da compilare a penna.
- **Correzioni dai colleghi Windows**: vanno nel JSON (nuovi casi in `se_non_va`), poi si rigenera e si ripubblica. Quando un collega avrà completato la guida Windows da cima a fondo, togliere l'avviso «non ancora provata» da `index.template.html`.

## Verifiche fatte

- **2026-10-21**:
  - comandi controllati su code.claude.com (setup, troubleshoot-install, vs-code), brew.sh, chocolatey.org/install, code.visualstudio.com, git-scm.com, cli.github.com, claude.com/pricing;
  - parte Mac ripercorsa sul Mac di Stefano, controllando che le uscite di `claude --version`, `git --version`, `brew --version` e `gh auth status` corrispondano a «Cosa devi vedere»;
  - zip scompattato in una cartella di prova e messaggio di verifica eseguito con Claude Code: la tabella esce corretta e, per ogni riga non OK, rimanda al passaggio giusto della guida.
- **Windows**: non ancora provato su un PC.

## Differenze rispetto al corso di Gaito (aprile-maggio 2026)

- Per installare Claude Code su Windows **non serve** PowerShell da amministratore: serve solo per Chocolatey.
- Git per Windows è **consigliato**, non obbligatorio: senza, Claude Code usa PowerShell al posto di Git Bash.
- La prova del gestore dei programmi converte il file in **Word** (Pandoc da solo) invece che in PDF, per non dover installare anche BasicTeX o MiKTeX (diverse centinaia di MB).

## Cosa non c'è, di proposito

- Niente testo, immagini o skill del corso di Raffaele Gaito: la guida è scritta sulla documentazione ufficiale.
- Niente dati di clienti, PIN o credenziali. Il contatto è «scrivi a Stefano», senza numero, perché la pagina è pubblica.

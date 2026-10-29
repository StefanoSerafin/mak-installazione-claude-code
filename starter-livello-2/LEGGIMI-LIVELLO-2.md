# Livello 2 — cosa aggiunge questo zip

Questo zip si aggiunge al workspace del livello 1: **non sostituisce niente**.

| Cosa | Dove va |
|---|---|
| Skill `estrai-sito` (copia di un sito, letto per intero) | `.claude/skills/estrai-sito/` |
| Skill `wiki` (il second brain: ingest, query, lint) | `.claude/skills/wiki/` |
| Gli script per i siti MAK e il README | `Siti/` |
| Lo scheletro del wiki: schema, modelli, lint, indice, log, pagine hub, impostazioni di Obsidian | `Second Brain/` |
| Cosa non va su GitHub | `.gitignore` |

## Istruzioni per Claude

Le esegue Claude quando l'agente gli chiede di scompattare lo zip.

1. Scompatta lo zip in una cartella temporanea, non direttamente nel workspace.
2. Copia nel workspace (la cartella aperta in VS Code) ogni file dello zip, mantenendo le sottocartelle, **tranne questo LEGGIMI**.
3. **Non sovrascrivere nessun file che esiste già.** Se un file c'è già, lascialo com'è e alla fine elencalo all'agente. Unica eccezione: `.gitignore`. Se esiste, aggiungi in fondo le righe che mancano invece di sostituirlo.
4. Accoda al `CLAUDE.md` del workspace la sezione qui sotto, «Da aggiungere a CLAUDE.md», se non c'è già.
5. Rendi eseguibile lo script per il Mac: `chmod +x Siti/_script/avvia_chrome_ebook.sh`.
6. Cancella la cartella temporanea. Lo zip in Download lascialo: chiedi all'agente se vuole che lo cancelli.
7. Mostra all'agente l'elenco di cosa hai aggiunto e ricordagli di aprire una conversazione nuova: le skill nuove si caricano all'inizio della conversazione.

## Da aggiungere a CLAUDE.md

```markdown
## Livello 2: siti e second brain

| Cartella | Cosa contiene |
|---|---|
| `Siti/` | le copie dei siti MAK, NPK, MATE, TRK e del sito agenti, fatte con la skill `estrai-sito` (copie fuori da git) |
| `Second Brain/` | il mio wiki (metodo LLM Wiki di Karpathy): schema in `Second Brain/CLAUDE.md`, pagine in `wiki/`, si apre con Obsidian |

- Per le domande sui prodotti, sulle condizioni o sulle procedure MAK parti dal wiki (`Second Brain/index.md`); se non basta, vai alle copie in `Siti/`.
- Quando una copia di un sito viene aggiornata o arriva materiale nuovo in `Listini/`, proponi l'ingest nel wiki con la skill `wiki`.
- Il materiale del sito agenti (`Siti/EBOOK`, pagine del wiki con `riservato: sì`) è riservato alla rete agenti: mai su GitHub, mai in pagine pubblicate.
- Lavori lunghi (copia di un sito, ingest): un lotto per conversazione, poi `/clear`.
```

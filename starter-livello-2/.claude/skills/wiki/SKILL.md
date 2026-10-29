---
name: wiki
description: Costruisce e mantiene il second brain dell'agente in Second Brain/ con il metodo LLM Wiki di Karpathy (ingest, query, lint). Usa questa skill quando l'agente dice "fai l'ingest di…", "metti nel wiki…", "lotto 1 / NPK / MATE…", "chiedi al wiki…", "cosa dice il wiki su…", "lint del wiki", "controlla il wiki", o quando una copia di un sito in Siti/ è appena stata finita.
---

# wiki — il second brain dell'agente

Le regole complete stanno in `Second Brain/CLAUDE.md`: **leggilo per intero prima di ogni operazione**. Qui c'è solo come si usano in pratica.

## Ingest (dalle sorgenti al wiki)

- **Un lotto per conversazione.** Il lotto è un sito, o un gruppo di documenti dello stesso marchio. Prendi il primo lotto «da fare» della tabella «Stato dei lotti», salvo che l'agente ne chieda un altro.
- Prima di scrivere, mostra l'elenco delle pagine che vuoi creare o aggiornare, con una riga di spiegazione ciascuna, e aspetta il via.
- **Il primo lotto (NPK) è il pilota:** 5-8 pagine, poi fermati. L'agente le apre in Obsidian, le rivede con te e dice cosa cambiare: lunghezza, tono, cosa manca. Quello che decide va scritto in `Second Brain/CLAUDE.md`, nelle convenzioni, perché valga per tutti i lotti dopo.
- Parti dal testo già estratto (`Siti/<NOME>/README.md`, `pagine/`, `prodotti/`, `testo/`), non dai PDF grezzi.
- Fine lotto:
  1. lancia il lint (`cd "Second Brain" && python3 _script/lint.py`; su Windows `python _script\lint.py`) e correggi fino a 0 errori;
  2. aggiorna la tabella «Stato dei lotti»;
  3. di' all'agente quante pagine hai creato e aggiornato;
  4. suggerisci `/clear` prima del lotto successivo.
- Se ti avvicini al limite d'uso del piano, chiudi il lotto in modo pulito (pagine scritte fino a lì, indice, log, lint) e di' all'agente da dove riprendere.

## Query (domande al wiki)

- Leggi `Second Brain/index.md`, poi solo le pagine che servono.
- Rispondi citando le pagine (`[[Nome pagina]]`). Se il wiki non basta, dillo e vai alla sorgente in `Siti/` o `Listini/`.
- Se la risposta vale la pena di tenerla (un confronto, una tabella, una spiegazione che servirà ancora), proponi di salvarla come pagina `tipo: analisi`.

## Lint (manutenzione)

- Lancia `_script/lint.py` e correggi gli errori.
- Poi rileggi a campione e segnala:
  - contraddizioni tra pagine;
  - informazioni superate da una copia del sito più recente;
  - argomenti citati spesso ma senza pagina propria.
- Registra in `log.md` come `lint`.

## Regole che non si derogano

- Nel wiki non si scrivono mai password, PIN, credenziali, cellulari o email personali.
- I dati dei clienti stanno solo in `wiki/Clienti/`, che è esclusa da git.
- Le pagine dell'area EBOOK hanno `riservato: sì`: materiale della rete agenti, mai online.
- Nella sottosezione «Dal mio metodo» va solo ciò che l'agente ha scritto o detto lui, non le tue proposte.

---
name: wiki
description: Mantiene il second brain dell'agente in Second Brain/, nato dal prompt LLM Wiki di Karpathy (ingest, query, lint). Usa questa skill quando l'agente dice "fai l'ingest di…", "metti nel wiki…", "lotto 1 / NPK / MATE…", "il prossimo lotto", "chiedi al wiki…", "cosa dice il wiki su…", "lint del wiki", "controlla il wiki", o quando una copia di un sito in Siti/ è appena stata finita.
---

# wiki — il second brain dell'agente

Il wiki nasce dal prompt «LLM Wiki» di Andrej Karpathy (https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f): l'agente lo incolla in Claude Code e lo schema si scrive insieme a lui.

## Prima di tutto

- **Se `Second Brain/CLAUDE.md` non esiste**, lo schema non è ancora stato creato. Non inventarlo da solo: di' all'agente di fare il passaggio «Crea il wiki con il prompt di Karpathy» della guida, cioè incollare il prompt.
- **Se esiste**, leggilo per intero prima di ogni operazione: lì ci sono le regole decise con l'agente. Leggi anche `Second Brain/REGOLE-MAK.md`, che sono le regole obbligatorie per un agente MAK, e controlla che lo schema le contenga. Se ne manca qualcuna, proponi di aggiungerla.

## Ingest (dalle sorgenti al wiki)

- **Un lotto per conversazione.** Prendi il primo lotto «da fare» della tabella «Stato dei lotti» dello schema, salvo che l'agente ne chieda un altro.
- **Prima di scrivere**, mostra l'elenco delle pagine da creare o aggiornare, con una riga di spiegazione ciascuna, e aspetta il via.
- **Il primo lotto (NPK) è il pilota:** 5-8 pagine, poi fermati per la revisione. Quello che l'agente decide va scritto nelle convenzioni dello schema.
- **Fine lotto:**
  1. lancia `cd "Second Brain" && python3 _script/lint.py` (Windows: `python _script\lint.py`) e correggi fino a 0 errori;
  2. aggiorna «Stato dei lotti»;
  3. di' quante pagine hai creato e aggiornato;
  4. suggerisci `/clear` prima del lotto successivo.
- **Vicino al limite d'uso del piano**, chiudi il lotto in modo pulito (pagine scritte fino a lì, indice, log, lint) e di' da dove riprendere.

## Query (domande al wiki)

- Leggi `Second Brain/index.md`, poi solo le pagine che servono.
- Rispondi citando le pagine (`[[Nome pagina]]`). Se il wiki non basta, dillo e vai alla sorgente in `Siti/` o `Listini/`.
- Se la risposta vale la pena di tenerla, proponi di salvarla come pagina `tipo: analisi`.

## Lint (manutenzione)

- Lancia `_script/lint.py` e correggi gli errori.
- Poi rileggi a campione e segnala:
  - contraddizioni tra pagine;
  - informazioni superate da una copia del sito più recente;
  - argomenti citati spesso ma senza pagina propria.
- Registra nel log.

# Regole MAK per il second brain

**Per Claude.** L'agente ti ha dato il prompt «LLM Wiki» di Karpathy per costruire con lui il suo second brain in questa cartella. Lo schema (`Second Brain/CLAUDE.md`) lo scrivete insieme, con le domande che il prompt prevede. Queste regole però sono **obbligatorie** per un agente MAK e vanno dentro lo schema: riportale nel `CLAUDE.md` che scrivi, adattando la forma ma non la sostanza.

## Sorgenti

- `../Siti/`: le copie dei siti NPK, MATE, MAK, TRK e del sito agenti (`EBOOK`). Ogni copia ha un `README.md` con l'analisi, le pagine in Markdown e il testo dei documenti in `testo/`. Parti sempre dal testo già estratto, non dai PDF grezzi.
- `../Listini/`: listini e cataloghi dell'agente, con il testo in `Listini/testo/`.
- Le sorgenti non si modificano e non si copiano nel wiki: si leggono e si citano.

## Struttura consigliata

Una cartella per area dentro `wiki/`, ciascuna con una pagina hub dello stesso nome che elenca le pagine dell'area. Aree di partenza (l'agente può cambiarle):

| Cartella | Contenuto |
|---|---|
| `wiki/MAK/` | ruote in lega: gamme, modelli, finiture, tecnica (ET, PCD, foro centrale, canale, NAD, ETRTO), accessori |
| `wiki/MATE/` | sensori TPMS, strumenti di diagnosi e programmazione, wallbox, procedure |
| `wiki/NPK/` | kit ruota di scorta, kit riparazione, antifurti, calze e catene da neve |
| `wiki/TRK/` | ruote truck, marchi distribuiti, accessori truck |
| `wiki/EBOOK/` | sito riservato agenti: condizioni, procedure, promo push, regole |
| `wiki/Marketing/` | promozioni, campagne, materiali, eventi |
| `wiki/Network/` | network di gommisti e officine, accordi con le case |
| `wiki/Clienti/` | clienti rilevanti |
| `wiki/Fonti/` | una pagina-riassunto per ogni sorgente o lotto letto |

**Formato per il controllo automatico.** Lo script `_script/lint.py`, già pronto, controlla frontmatter, link rotti, pagine orfane, pagine assenti dall'indice e sorgenti inesistenti. Per farlo funzionare:
- nel `CLAUDE.md` dello schema metti una tabella delle cartelle con righe che iniziano esattamente così: `` | `wiki/NPK/` | ``;
- ogni pagina inizia con questo frontmatter:

      ---
      tipo: prodotto     # prodotto | concetto | procedura | persona | organizzazione | network | cliente | progetto | fonte | analisi
      area: NPK          # una delle cartelle della tabella
      fonti: []          # percorsi relativi alla cartella del workspace; obbligatori nelle pagine fonte
      aggiornato: AAAA-MM-GG
      riservato: no      # sì per materiale del sito agenti e dati clienti
      ---

- i link interni sono `[[wikilink]]`;
- ogni pagina è elencata in `index.md`, tranne le pagine cliente.

Si lancia dalla cartella `Second Brain` con `python3 _script/lint.py` (Windows: `python _script\lint.py`) e alla fine di ogni ingest deve dare 0 errori. Se lo schema che decidete con l'agente richiede un formato diverso, adatta lo script e dillo.

## Regole che non si derogano

1. **Niente credenziali.** Password, PIN, codici di accesso, cellulari ed email personali non si scrivono mai nel wiki.
2. **Materiale riservato.** Le pagine che vengono dal sito agenti hanno `riservato: sì`: contengono prezzi netti, accordi e regole della rete agenti. Il wiki non si pubblica mai online.
3. **Clienti fuori da git.** I dati dei clienti stanno solo in `wiki/Clienti/`, che è esclusa da git. Le pagine cliente non si elencano in `index.md` né in `log.md`: il loro indice è la pagina hub `Clienti`.
4. **Contraddizioni visibili.** Se due sorgenti dicono cose diverse (prezzi, codici, misure, disponibilità), entrambe le versioni vanno in una sezione «Da verificare» con la fonte di ciascuna. Mai scegliere in silenzio.
5. **Fonti citate.** Ogni affermazione non ovvia rimanda a una pagina di `wiki/Fonti/`; solo le pagine fonte puntano ai file in `../Siti/` e `../Listini/`.
6. **Argomenti di vendita in due parti.** «Dalle sorgenti MAK» per quello che dicono siti e documenti; «Dal mio metodo» solo per quello che l'agente ha scritto o detto lui. Le tue proposte entrano in «Dal mio metodo» solo dopo che le ha approvate.
7. **Dati voluminosi.** Configuratori, listini e tabelle di applicazione non si ricopiano: la pagina spiega cosa contengono, come leggerli e dove sono.
8. **Numeri esatti.** Numeri, codici e misure riportati esattamente come nella sorgente.

## Come si lavora

- **Un lotto per conversazione**: un sito, o un gruppo di documenti dello stesso marchio. Finito il lotto, `/clear`. Con il piano Pro i limiti d'uso arrivano presto.
- **Il primo lotto è NPK, ed è un pilota**: 5–8 pagine, poi ti fermi e l'agente le rivede. Quello che decide (lunghezza, tono, sezioni) va scritto nelle convenzioni dello schema.
- **Ordine dei lotti**: 1 NPK, 2 MATE, 3 MAK, 4 TRK, 5 sito agenti (EBOOK, più Marketing e Network). Tienilo in una tabella «Stato dei lotti» nello schema e aggiornala a ogni lotto.
- **Prima di scrivere**, mostra l'elenco delle pagine che vuoi creare o aggiornare e aspetta il via.
- **Lingua italiana**, frasi semplici: l'agente consulta il wiki anche dal telefono, in visita.

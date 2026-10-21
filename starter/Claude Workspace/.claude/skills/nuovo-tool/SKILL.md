---
name: nuovo-tool
description: Guida la creazione di una piccola web app a partire da un Excel, un PDF o un'idea (per esempio una tabella di taglie, un listino da consultare, un calcolo che si fa spesso), con un'intervista iniziale e una pagina HTML unica che funziona anche offline e su telefono. Usala quando l'utente dice «voglio un tool per…», «trasforma questo Excel in un'app» o chiede una pagina da consultare dal telefono.
---

# Nuovo tool

## 1. Intervista

Prima di scrivere codice fai queste domande, una alla volta, e aspetta la risposta:

1. Cosa deve fare il tool, in una frase? (es. «dalla misura del pneumatico mi dice la taglia della calza da neve»)
2. Chi lo usa: solo io, i colleghi, i clienti?
3. Da quali dati parte? Fatti indicare il file (Excel, PDF, CSV) e leggilo.
4. Dove si apre di solito: telefono in visita, computer in ufficio, tutti e due?
5. I dati sono riservati (prezzi netti, sconti, dati di clienti)? Se sì, il tool resta solo sul computer o va protetto prima di metterlo online.

Riassumi le risposte in cinque righe e chiedi conferma.

## 2. Costruisci

- Crea la cartella `Tool/<nome-del-tool>/` (nome in minuscolo con i trattini).
- Un solo file `index.html` con HTML, stile e codice dentro, senza librerie scaricate da Internet: deve funzionare anche senza rete.
- I dati letti dal file sorgente vanno dentro la pagina. Se il file sorgente cambierà, scrivi anche un piccolo script che rigenera la pagina e spiega come lanciarlo.
- Pensata prima per il telefono: testi leggibili, pulsanti grandi, niente tabelle troppo larghe.
- Su iPhone deve funzionare in Safari: prova i filtri e i campi di ricerca come li userebbe una persona.

## 3. Prova

- Apri la pagina nel browser e controlla tre casi reali presi dal file sorgente: il risultato deve coincidere.
- Mostra all'utente come aprirla (doppio clic sul file) e cosa controllare.

## 4. Pubblicazione

Si pubblica su GitHub Pages **solo se l'utente lo chiede**, e prima:

- ricontrolla che non ci siano dati riservati (vedi domanda 5);
- spiega che l'indirizzo sarà raggiungibile da chiunque lo conosca;
- chiedi conferma esplicita prima di creare il repository e fare il push.

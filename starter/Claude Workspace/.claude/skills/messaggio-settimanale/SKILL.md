---
name: messaggio-settimanale
description: Scrive la bozza del messaggio settimanale ai clienti (WhatsApp, email, post social) a partire dal tema o dal prodotto della campagna. Usala quando l'utente chiede il messaggio della settimana, un testo per WhatsApp ai clienti, una mail promozionale o un post su un prodotto MAK, NPK o MATE.
---

# Messaggio settimanale ai clienti

Prepara le bozze del messaggio che l'agente manda ai suoi clienti, tutte sullo stesso tema.

## 1. Raccogli le informazioni

Se l'utente non le ha già date, chiedi in un solo messaggio:

- il tema o il prodotto (per esempio: kit ruotino NPK, calze da neve, sensori TPMS);
- l'offerta, se c'è: prezzo, condizioni, scadenza;
- i canali: WhatsApp, email, post social (di default tutti e tre);
- se ci sono un'immagine, una locandina o un link da allegare.

## 2. Guarda il contesto

- Leggi `CLAUDE.md` per il tono e i marchi.
- Se nella cartella `Campagne/` ci sono messaggi precedenti, leggi gli ultimi tre per riprenderne lo stile e non ripetere le stesse frasi.

## 3. Scrivi le bozze

- **WhatsApp**: al massimo 600 caratteri. Prima riga che si capisce anche nell'anteprima della notifica. Una sola richiesta d'azione alla fine («rispondi a questo messaggio», «chiamami», «ordina dal portale»). Poche emoji.
- **Email**: oggetto (massimo 50 caratteri) e testo di 5–8 righe, con la stessa richiesta d'azione.
- **Post social**: 2–4 righe e, se servono, 3–5 hashtag.

## 4. Regole

- Mai inventare prezzi, sconti, scadenze o codici prodotto: se mancano scrivi `[PREZZO]`, `[SCADENZA]`, `[CODICE]` e segnalalo.
- Codici e misure si riportano esattamente come li ha dati l'utente.
- Niente promesse tecniche (omologazioni, compatibilità con una vettura) che l'utente non abbia confermato.
- Il messaggio parla al cliente (gommista, officina, carrozzeria), non all'automobilista, salvo indicazione diversa.

## 5. Salva

Mostra le bozze. Se l'utente le approva, salvale in `Campagne/AAAA-MM-GG-tema.md` (data di oggi, tema in minuscolo con i trattini).

---
name: riassunto-visita
description: Trasforma gli appunti di una visita o di una telefonata a un cliente (testo scritto in fretta, dettato, foto di appunti) in una scheda ordinata con interessi, obiezioni e prossimi passi, salvata nella cartella del cliente. Usala quando l'utente incolla appunti di una visita, dice «ho visto il cliente…» o chiede di riassumere un incontro.
---

# Riassunto della visita

## 1. Leggi gli appunti

Gli appunti possono essere disordinati, dettati o in una foto. Se manca il nome del cliente o la data, chiedili (la data di default è oggi).

## 2. Scrivi la scheda

Usa questa struttura, lasciando fuori le sezioni vuote:

```
# Visita — <Cliente> — <AAAA-MM-GG>

**Chi ho incontrato:** …
**Tipo di cliente:** gommista / officina / carrozzeria / ricambista / concessionario

## Cosa è emerso
- …

## Prodotti di interesse
- MAK / NPK / MATE: …

## Obiezioni e dubbi
- …

## Prossimi passi
- [ ] Cosa — entro quando — chi lo fa

## Da preparare per la prossima visita
- …
```

## 3. Regole

- Riporta solo quello che c'è negli appunti. Se una cosa non è chiara scrivi «da verificare», non completarla a intuito.
- Quantità, prezzi, codici e misure esattamente come negli appunti.
- Niente dati personali oltre a quelli che servono (no codici fiscali, no dati bancari).

## 4. Salva

Mostra la scheda. Se l'utente la approva, salvala in `Clienti/<Nome cliente>/AAAA-MM-GG-visita.md`, creando la cartella del cliente se non esiste. Se nella cartella ci sono visite precedenti, aggiungi in fondo una riga «Rispetto all'ultima visita: …» con cosa è cambiato.

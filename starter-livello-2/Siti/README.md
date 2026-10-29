# Siti — le copie dei siti MAK

Ogni cartella è la copia di un sito, fatta con la skill `estrai-sito` e gli script di `_script/`. È una fotografia alla data della copia: il sito cambia, i file no. Per aggiornare una copia basta chiedere a Claude «aggiorna la copia del sito NPK».

| Cartella | Sito | Note |
|---|---|---|
| `NPK/` | noproblemkit.com | pagine + `dati/` con i configuratori in CSV (ruotini, kit, antifurti, calze, catene, veicoli) |
| `MATE/` | mate-tech.it | pagine, schede prodotto, manuali in PDF |
| `MAK/` | makwheels.it | pagine, schede ruote e ricambi, promozioni, news |
| `TRK/` | trkwheels.it | pagine e tabelle tecniche in PDF |
| `EBOOK/` | sito riservato agli agenti | **materiale riservato**: prezzi netti, accordi, regole. Resta su questo computer |

Dentro ogni copia:
- `README.md` con l'analisi;
- le pagine in Markdown;
- `download/` con i documenti scaricati e `testo/` con il loro testo estratto;
- `video.md` con i link ai video.

Su GitHub vanno solo questo file e `_script/`: le copie sono escluse dal `.gitignore`.

## Gli script

| Script | Cosa fa |
|---|---|
| `scarica_sito.py` | copia un sito pubblico dalla sua sitemap (`--conta` per sapere prima quante pagine sono) |
| `estrai_testo.py` | estrae il testo di PDF, Excel, Word e PowerPoint scaricati |
| `npk_dati.py` | scarica i configuratori di noproblemkit.com in CSV |
| `avvia_chrome_ebook.sh` / `.ps1` | apre il Chrome dedicato al sito agenti (il login lo fai tu) |
| `ebook_pagine.py` | copia le pagine del sito agenti da quel Chrome |
| `ebook_file.py` | scarica i file Drive collegati al sito agenti (i video restano solo elencati) |

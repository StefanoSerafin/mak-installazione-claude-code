#!/usr/bin/env python3
"""Controlli di salute del wiki. Uso, dalla cartella Second Brain: python3 _script/lint.py
(su Windows: python _script\\lint.py). Le aree valide sono quelle della tabella «Struttura» di CLAUDE.md."""
import re
import sys
import unicodedata
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
WORKSPACE = VAULT.parent
WIKI = VAULT / "wiki"

TIPI = {"prodotto", "concetto", "procedura", "persona", "organizzazione",
        "network", "cliente", "progetto", "fonte", "analisi"}
AREE = set(re.findall(r"^\| `wiki/([^/`]+)/` \|", (VAULT / "CLAUDE.md").read_text(encoding="utf-8"), re.M)) - {"Fonti"}
CAMPI = ("tipo", "area", "fonti", "aggiornato", "riservato")
LINK = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")


def nfc(testo):
    return unicodedata.normalize("NFC", testo.strip())


def frontmatter(testo):
    """Legge il frontmatter: valori semplici e liste di una riga per voce."""
    if not testo.startswith("---\n"):
        return None
    fine = testo.find("\n---", 4)
    if fine == -1:
        return None
    dati, chiave = {}, None
    for riga in testo[4:fine].splitlines():
        if re.match(r"^\s+- ", riga) and chiave:
            dati[chiave].append(riga.split("- ", 1)[1].strip())
        elif ":" in riga:
            chiave, valore = riga.split(":", 1)
            chiave = chiave.strip()
            valore = valore.split(" #")[0].strip()
            dati[chiave] = [] if valore in ("", "[]") else valore
    return dati


def link(testo):
    # nelle tabelle Obsidian vuole la barra dell'alias scritta \|: si toglie la barra rovesciata
    return {nfc(nome.rstrip("\\")) for nome in LINK.findall(testo)}


def main():
    errori = []
    if not AREE:
        sys.exit("Non trovo le aree nella tabella «Struttura» di CLAUDE.md.")
    pagine = sorted(WIKI.rglob("*.md"))
    nomi = {}
    for p in pagine:
        nome = nfc(p.stem)
        if nome in nomi:
            errori.append(f"nome duplicato: {p.relative_to(VAULT)} e {nomi[nome].relative_to(VAULT)}")
        nomi[nome] = p

    entranti = {nome: 0 for nome in nomi}
    for p in pagine:
        rel = p.relative_to(VAULT)
        testo = p.read_text(encoding="utf-8")
        fm = frontmatter(testo)
        if fm is None:
            errori.append(f"{rel}: frontmatter mancante")
            continue
        for campo in CAMPI:
            if campo not in fm:
                errori.append(f"{rel}: manca il campo '{campo}'")
        if fm.get("tipo") not in TIPI:
            errori.append(f"{rel}: tipo non valido '{fm.get('tipo')}'")
        if fm.get("area") not in AREE:
            errori.append(f"{rel}: area non valida '{fm.get('area')}'")
        cartella = p.relative_to(WIKI).parts[0]
        if cartella == "Fonti":
            if fm.get("tipo") != "fonte":
                errori.append(f"{rel}: in Fonti/ il tipo deve essere 'fonte'")
        elif fm.get("area") != cartella:
            errori.append(f"{rel}: area '{fm.get('area')}' diversa dalla cartella '{cartella}'")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(fm.get("aggiornato", ""))):
            errori.append(f"{rel}: 'aggiornato' deve essere AAAA-MM-GG")
        if fm.get("riservato") not in ("sì", "no"):
            errori.append(f"{rel}: 'riservato' deve essere sì o no")
        fonti = fm.get("fonti", [])
        if isinstance(fonti, str):
            fonti = [fonti]
        if fm.get("tipo") == "fonte" and not fonti:
            errori.append(f"{rel}: una pagina fonte deve elencare almeno un file in 'fonti'")
        for f in fonti:
            if not (WORKSPACE / f).exists():
                errori.append(f"{rel}: sorgente inesistente '{f}'")
        for destinazione in link(testo):
            if destinazione not in nomi:
                errori.append(f"{rel}: link rotto [[{destinazione}]]")
            elif destinazione != nfc(p.stem):
                entranti[destinazione] += 1

    for nome, n in entranti.items():
        # una pagina hub (stesso nome della sua cartella) può restare senza link finché l'area è vuota
        if n == 0 and nome != nfc(nomi[nome].parent.name):
            errori.append(f"{nomi[nome].relative_to(VAULT)}: pagina orfana (nessun link in entrata)")

    indice = link((VAULT / "index.md").read_text(encoding="utf-8"))
    # le pagine cliente non stanno in index.md (che è in git): il loro indice è l'hub Clienti
    hub_clienti = WIKI / "Clienti" / "Clienti.md"
    if hub_clienti.exists():
        in_hub = link(hub_clienti.read_text(encoding="utf-8"))
        indice |= {n for n in in_hub if n in nomi and nomi[n].parent.name == "Clienti"}
    for nome in nomi:
        if nome not in indice:
            errori.append(f"{nomi[nome].relative_to(VAULT)}: manca in index.md")
    for nome in indice - set(nomi):
        errori.append(f"index.md: link rotto [[{nome}]]")

    for e in errori:
        print("ERRORE", e)
    print(f"{len(pagine)} pagine, {len(errori)} errori")
    return 1 if errori else 0


if __name__ == "__main__":
    sys.exit(main())

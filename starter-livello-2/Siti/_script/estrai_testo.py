#!/usr/bin/env python3
"""Estrae il testo dai documenti scaricati di un sito (PDF, Excel, Word, PowerPoint, RTF):

    .venv/bin/python Siti/_script/estrai_testo.py --cartella MAK

Legge Siti/<CARTELLA>/download/ (anche nelle sottocartelle) e scrive il testo in
Siti/<CARTELLA>/testo/<stesso percorso>.txt, così tutto il materiale è cercabile.
Scrive Siti/<CARTELLA>/testo.csv con pagine/fogli, caratteri estratti ed esito per ogni file.

Non fa OCR: i PDF fatti solo di immagini (locandine, scansioni) risultano "SOLO IMMAGINI" e
Claude li deve guardare come immagini (pdftoppm). I file già estratti non vengono rifatti.
Richiede PyMuPDF, openpyxl, xlrd (installati nel .venv del workspace al livello 2)."""
import argparse, csv, os, re, subprocess, sys, zipfile

import openpyxl, xlrd

QUI = os.path.dirname(os.path.abspath(__file__))
SITI = os.path.join(QUI, "..")
MIN_CAR_PAGINA = 40  # sotto questa media per pagina il PDF è considerato fatto di immagini


def riga(celle):
    v = ["" if c is None else str(c).replace("\n", " ").strip() for c in celle]
    while v and not v[-1]:
        v.pop()
    return ";".join(v)


UN_PDF = """import sys
try:
    import pymupdf as fitz
except ImportError:
    import fitz
doc = fitz.open(sys.argv[1])
sys.stdout.buffer.write(("%d\\n" % len(doc)).encode())
for n, p in enumerate(doc):
    sys.stdout.buffer.write(("--- pagina %d ---\\n%s\\n\\n" % (n + 1, p.get_text().strip())).encode("utf-8"))
"""


def pdf(percorso):
    # un processo per PDF: PyMuPDF dopo qualche centinaio di file nello stesso processo va in crash
    out = subprocess.run([sys.executable, "-c", UN_PDF, percorso], capture_output=True)
    if out.returncode:  # su qualche PDF PyMuPDF va in crash: ripiego su pdftotext (poppler)
        txt = subprocess.run(["pdftotext", "-layout", percorso, "-"], capture_output=True, text=True, check=True).stdout
        pagine = txt.split("\f")
        return "\n\n".join("--- pagina %d ---\n%s" % (n + 1, p.strip()) for n, p in enumerate(pagine)), len(pagine), "pagine"
    n, _, testo = out.stdout.decode("utf-8", "replace").partition("\n")
    return testo.strip(), int(n), "pagine"


def xlsx(percorso):
    wb = openpyxl.load_workbook(percorso, read_only=True, data_only=True)
    parti = []
    for ws in wb.worksheets:
        righe = [r for r in (riga(x) for x in ws.iter_rows(values_only=True)) if r]
        parti.append("--- foglio: %s ---\n%s" % (ws.title, "\n".join(righe)))
    return "\n\n".join(parti), len(wb.worksheets), "fogli"


def xls(percorso):
    wb = xlrd.open_workbook(percorso)
    parti = []
    for ws in wb.sheets():
        righe = [r for r in (riga(ws.row_values(i)) for i in range(ws.nrows)) if r]
        parti.append("--- foglio: %s ---\n%s" % (ws.name, "\n".join(righe)))
    return "\n\n".join(parti), wb.nsheets, "fogli"


def office(percorso, schema, etichetta):
    """Word e PowerPoint sono zip di XML: prendo il testo dei paragrafi."""
    if not zipfile.is_zipfile(percorso):  # non è un vero .docx: PDF o vecchio .doc rinominato
        with open(percorso, "rb") as f:
            return pdf(percorso) if f.read(4) == b"%PDF" else rtf(percorso)
    with zipfile.ZipFile(percorso) as z:
        nomi = sorted((n for n in z.namelist() if re.match(schema, n)),
                      key=lambda n: [int(x) for x in re.findall(r"\d+", n)])
        parti = []
        for n in nomi:
            x = z.read(n).decode("utf-8", "replace")
            par = ["".join(re.findall(r"<(?:w|a):t[^>]*>([^<]*)</(?:w|a):t>", p))
                   for p in re.split(r"</(?:w|a):p>", x)]
            parti.append("\n".join(p for p in par if p.strip()))
    return "\n\n".join(parti), len(nomi), etichetta


def rtf(percorso):
    out = subprocess.run(["textutil", "-convert", "txt", "-stdout", percorso], capture_output=True, text=True)
    return out.stdout, 1, "documenti"


ESTRATTORI = {
    ".pdf": pdf, ".xlsx": xlsx, ".xls": xls, ".rtf": rtf,
    ".docx": lambda p: office(p, r"word/document\.xml$", "documenti"),
    ".pptx": lambda p: office(p, r"ppt/slides/slide\d+\.xml$", "slide"),
}


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--cartella", required=True, help="nome della cartella dentro Siti/, es. MAK")
    radice = os.path.join(SITI, a.parse_args().cartella)
    download, testo_dir = os.path.join(radice, "download"), os.path.join(radice, "testo")
    if not os.path.isdir(download):
        sys.exit(f"Non trovo {download}: prima scarica il sito.")
    righe = []
    for cart, _, files in sorted(os.walk(download)):
        rel = os.path.relpath(cart, download)
        rel = "" if rel == "." else rel
        for nome in sorted(files):
            est = os.path.splitext(nome)[1].lower()
            if est not in ESTRATTORI:
                continue
            origine = os.path.join(cart, nome)
            dest = os.path.join(testo_dir, rel, nome + ".txt")
            try:
                if os.path.exists(dest):
                    with open(dest, encoding="utf-8") as f:
                        testo = f.read()
                    m = re.match(r"# (\d+) (\w+)\n", testo)
                    n, unita = (int(m.group(1)), m.group(2)) if m else (0, "")
                    testo = testo[m.end():] if m else testo
                else:
                    testo, n, unita = ESTRATTORI[est](origine)
                    os.makedirs(os.path.dirname(dest), exist_ok=True)
                    with open(dest, "w", encoding="utf-8") as f:
                        f.write("# %d %s\n%s" % (n, unita, testo))
                car = len(re.sub(r"--- (pagina|foglio)[^\n]*---|\s", "", testo))
                esito = "SOLO IMMAGINI" if est == ".pdf" and car < MIN_CAR_PAGINA * max(n, 1) else "TESTO"
                if car == 0:
                    esito = "SOLO IMMAGINI" if est == ".pdf" else "VUOTO"
                righe.append([rel, nome, est[1:], n, unita, car, esito, os.path.relpath(dest, radice)])
            except Exception as e:
                righe.append([rel, nome, est[1:], "", "", 0, "ERRORE: %s" % str(e).splitlines()[0][:100], ""])
            print("%-13s %7s car  %s" % (righe[-1][6][:13], righe[-1][5], os.path.join(rel, nome)[:90]), flush=True)
    with open(os.path.join(radice, "testo.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["sottocartella", "file", "tipo", "n", "unita", "caratteri", "esito", "testo"])
        w.writerows(righe)
    tot = len(righe)
    img = [r[1] for r in righe if r[6] == "SOLO IMMAGINI"]
    err = [r[1] for r in righe if r[6].startswith("ERRORE")]
    print(f"\nDocumenti: {tot}  con testo: {tot - len(img) - len(err)}  solo immagini: {len(img)}  errori: {len(err)}")
    for n in img:
        print("  da guardare come immagine:", n)
    for n in err:
        print("  non leggibile:", n)


if __name__ == "__main__":
    main()

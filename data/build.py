#!/usr/bin/env python3
"""Genera index.html (web app), slides.html (slide per l'incontro) e lo zip del workspace
a partire da data/passi.json. Uso: python3 data/build.py"""

import html
import json
import re
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import figure  # noqa: E402

BASE = Path(__file__).resolve().parent.parent
DATI = json.loads((BASE / "data" / "passi.json").read_text(encoding="utf-8"))
OBBLIGATORI = ("id", "fase", "titolo", "perche", "fai", "vedi", "se_non_va", "minuti", "fonte")
SISTEMI = {"mac": "Mac", "windows": "Windows"}


def controlla():
    errori = []
    fasi = {f["id"] for f in DATI["fasi"]}
    for so in SISTEMI:
        visti = set()
        for p in DATI[so]:
            for campo in OBBLIGATORI:
                if campo not in p:
                    errori.append(f"{so}/{p.get('id', '?')}: manca «{campo}»")
            if p.get("fase") not in fasi:
                errori.append(f"{so}/{p.get('id')}: fase sconosciuta «{p.get('fase')}»")
            for nome in p.get("figure", []):
                if nome not in figure.FIGURE:
                    errori.append(f"{so}/{p.get('id')}: disegno sconosciuto «{nome}»")
            if p.get("fonte") not in DATI["fonti"]:
                errori.append(f"{so}/{p.get('id')}: fonte sconosciuta «{p.get('fonte')}»")
            if p.get("id") in visti:
                errori.append(f"{so}/{p.get('id')}: id ripetuto")
            visti.add(p.get("id"))
    if errori:
        sys.exit("Errori in passi.json:\n- " + "\n- ".join(errori))


def testo(s):
    """Escape HTML, **grassetto** e `testo da scrivere` (mostrato tra virgolette, che non si copiano)."""
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", lambda m: f'<code class="scrivi{" corto" if len(m.group(1)) <= 28 else ""}">{m.group(1)}</code>', s)
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)


def figure_html(p, so):
    out = []
    for nome in p.get("figure", []):
        disegno, didascalia = figure.FIGURE[nome](so)
        voci = "".join(f"<li>{testo(d)}</li>" for d in didascalia)
        out.append(f'<figure class="figura">{disegno}<figcaption><ol class="legenda">{voci}</ol>'
                   f'<p class="nota-disegno">Disegno schematico: colori e posizioni possono essere un po\' diversi sul tuo schermo.</p>'
                   f'</figcaption></figure>')
    return "".join(out)


def blocco_comando(cmd, etichetta="Comando"):
    return (f'<div class="cmd"><div class="cmd-testa"><span>{etichetta}</span>'
            f'<button type="button" class="copia noprint">Copia</button></div>'
            f'<pre><code>{html.escape(cmd, quote=False)}</code></pre></div>')


def passo_html(p, n, so):
    out = [f'<article class="passo" id="{p["id"]}">',
           f'<label class="passo-testa"><input type="checkbox" class="spunta" data-id="{p["id"]}">'
           f'<span class="num">{n}</span><span class="tit">{testo(p["titolo"])}</span>'
           f'<span class="min">{p["minuti"]} min</span></label>',
           f'<p class="perche">{testo(p["perche"])}</p>',
           '<ol class="fai">' + "".join(f"<li>{testo(f)}</li>" for f in p["fai"]) + "</ol>",
           figure_html(p, so)]
    if p.get("comando"):
        out.append(blocco_comando(p["comando"]))
    if p.get("zip"):
        out.append(f'<p class="noprint"><a class="bottone" href="{DATI["zip"]}" download>Scarica {DATI["zip"]}</a></p>'
                   f'<p class="solostampa">Lo zip si scarica dalla web app (indirizzo in fondo).</p>')
    if p.get("prompt_verifica"):
        out.append(blocco_comando(DATI["verifica_prompt"], "Messaggio da incollare in Claude"))
    out.append(f'<p class="vedi"><b>Cosa devi vedere</b> {testo(p["vedi"])}</p>')
    if p["se_non_va"]:
        casi = []
        for c in p["se_non_va"]:
            pezzo = f'<li><b>{testo(c["se"])}</b> — {testo(c["fai"])}'
            if c.get("comando"):
                pezzo += blocco_comando(c["comando"])
            casi.append(pezzo + "</li>")
        out.append('<details class="nonva"><summary>Se non va</summary><ul>' + "".join(casi) + "</ul></details>")
    out.append(f'<p class="fonte">Fonte: <a href="{DATI["fonti"][p["fonte"]]}" target="_blank" rel="noopener">'
               f'{html.escape(DATI["fonti"][p["fonte"]].split("//")[1])}</a></p>')
    out.append("</article>")
    return "\n".join(out)


def guida_html(so):
    parti, n = [], 0
    for i, f in enumerate(DATI["fasi"]):
        passi = [p for p in DATI[so] if p["fase"] == f["id"]]
        if not passi:
            continue
        parti.append(f'<section class="fase"><h2><span>Fase {i}</span> {testo(f["titolo"])}</h2>'
                     f'<p class="obiettivo">{testo(f["obiettivo"])}</p>')
        for p in passi:
            n += 1
            parti.append(passo_html(p, n, so))
        parti.append("</section>")
    return "\n".join(parti)


def slide_fase(i, f):
    colonne = []
    for so, nome in SISTEMI.items():
        passi = [p for p in DATI[so] if p["fase"] == f["id"]]
        righe = []
        for p in passi:
            riga = f"<li><strong>{testo(p['titolo'])}</strong>"
            if p.get("comando"):
                prima = p["comando"].splitlines()[0]
                if len(prima) > 60:
                    prima = prima[:57] + "…"
                riga += f"<code>{html.escape(prima)}</code>"
            righe.append(riga + "</li>")
        errori = [c["se"] for p in passi for c in p["se_non_va"]][:2]
        err = "".join(f"<li>{testo(e)}</li>" for e in errori)
        colonne.append(f'<div class="col"><h3>{nome}</h3><ul class="passi">{"".join(righe)}</ul>'
                       + (f'<p class="lab">Errori tipici</p><ul class="err">{err}</ul>' if err else "")
                       + "</div>")
    return (f'<section class="slide"><p class="kicker">Fase {i} di {len(DATI["fasi"]) - 1}</p>'
            f'<h2>{testo(f["titolo"])}</h2><p class="ob">{testo(f["obiettivo"])}</p>'
            f'<div class="due">{"".join(colonne)}</div></section>')


def slides_html():
    s = [f'<section class="slide copertina"><p class="kicker">Corso Claude Code per agenti MAK</p>'
         f'<h1>Installare Claude Code</h1><p class="sotto">Verifica insieme: chi è pronto parte, chi è indietro si sistema adesso.</p>'
         f'<p class="chi">Comandi verificati sulla documentazione ufficiale il {data_it(DATI["verificato"])}</p></section>',
         '<section class="slide"><h2>Come facciamo oggi</h2><ol class="grande">'
         '<li>Apri VS Code nella tua cartella Claude Workspace.</li>'
         '<li>Mostra lo screenshot della tabella di verifica (o rifalla adesso).</li>'
         '<li>Tutte le righe OK: aiuta il vicino. Qualche riga no: la sistemiamo con la guida, fase per fase.</li>'
         '</ol></section>']
    for i, f in enumerate(DATI["fasi"]):
        if f["id"] != "verifica":
            s.append(slide_fase(i, f))
    s.append('<section class="slide"><h2>La verifica</h2><p class="ob">Si incolla nel pannello di Claude, in VS Code:</p>'
             f'<blockquote>{testo(DATI["verifica_prompt"])}</blockquote></section>')
    s.append('<section class="slide"><h2>Dove ci si blocca di solito</h2><div class="due">'
             '<div class="col"><h3>Mac</h3><ul class="err">'
             '<li><code>command not found: claude</code>: manca il PATH (due comandi nella guida)</li>'
             '<li><code>command not found: brew</code>: saltati i «Next steps» di Homebrew</li>'
             '<li>VS Code non vede un programma appena installato: chiudi e riapri VS Code</li>'
             '</ul></div><div class="col"><h3>Windows</h3><ul class="err">'
             '<li><code>\'claude\' is not recognized</code>: manca <code>%USERPROFILE%\\.local\\bin</code> nel PATH</li>'
             '<li><code>\'irm\' is not recognized</code>: sei nel Prompt dei comandi, non in PowerShell</li>'
             '<li>Chocolatey: PowerShell va aperta «come amministratore»</li>'
             '</ul></div></div></section>')
    s.append('<section class="slide"><h2>E adesso si lavora</h2><ul class="grande">'
             '<li>Come si parla a Claude: il risultato e il contesto, non i passaggi.</li>'
             '<li>Il tuo CLAUDE.md: cosa sa Claude di te e dei tuoi clienti.</li>'
             '<li>Le skill: le cose che fai ogni settimana diventano un comando.</li>'
             '<li>Primo tool: da un tuo Excel a una pagina da consultare dal telefono.</li>'
             '</ul></section>')
    return "\n".join(s)


MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto",
        "settembre", "ottobre", "novembre", "dicembre"]


def data_it(iso):
    a, m, g = iso.split("-")
    return f"{int(g)} {MESI[int(m) - 1]} {a}"


def crea_zip():
    sorgente = BASE / "starter" / "Claude Workspace"
    dest = BASE / DATI["zip"]
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(sorgente.rglob("*")):
            if f.is_file() and f.name != ".DS_Store":
                z.write(f, f.relative_to(sorgente).as_posix())
    return dest


def main():
    controlla()
    scadenza = DATI.get("scadenza")
    if scadenza:
        riga_scad = f'<p class="scadenza">Da finire entro il <strong>{data_it(scadenza)}</strong>.</p>'
    else:
        riga_scad = '<p class="scadenza solostampa">Da finire entro il ____________________</p>'
    sost = {
        "<!--TITOLO-->": testo(DATI["titolo"]),
        "<!--SOTTOTITOLO-->": testo(DATI["sottotitolo"]),
        "<!--SCADENZA-->": riga_scad,
        "<!--VERIFICATO-->": data_it(DATI["verificato"]),
        "<!--CONTATTO-->": testo(DATI["contatto"]),
        "<!--MINUTI_MAC-->": str(sum(p["minuti"] for p in DATI["mac"])),
        "<!--MINUTI_WIN-->": str(sum(p["minuti"] for p in DATI["windows"])),
        "<!--GUIDA_MAC-->": guida_html("mac"),
        "<!--GUIDA_WIN-->": guida_html("windows"),
    }
    pagina = (BASE / "index.template.html").read_text(encoding="utf-8")
    for k, v in sost.items():
        pagina = pagina.replace(k, v)
    (BASE / "index.html").write_text(pagina, encoding="utf-8")

    slide = (BASE / "slides.template.html").read_text(encoding="utf-8").replace("<!--SLIDES-->", slides_html())
    (BASE / "slides.html").write_text(slide, encoding="utf-8")

    z = crea_zip()
    print(f"index.html: {len(DATI['mac'])} passaggi Mac, {len(DATI['windows'])} Windows")
    n_slide = slide.count('<section class="slide')
    print(f"slides.html: {n_slide} slide")
    print(f"{z.name}: {len(zipfile.ZipFile(z).namelist())} file")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Genera index.html (web app), slides.html (slide per l'incontro) e i due zip del workspace
(livello 1: starter/, livello 2: starter-livello-2/) a partire da data/passi.json.
Uso: python3 data/build.py"""

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
    for f in DATI["fasi"]:
        if f.get("livello") not in (1, 2):
            errori.append(f"fase {f['id']}: «livello» deve essere 1 o 2")
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
            if p.get("zip") not in (None, False, True, 1, 2) or p.get("prompt_verifica") not in (None, False, True, 1, 2):
                errori.append(f"{so}/{p.get('id')}: «zip» e «prompt_verifica» valgono 1 o 2")
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
        nome = DATI["zip_2"] if p["zip"] == 2 else DATI["zip"]
        out.append(f'<p class="noprint"><a class="bottone" href="{nome}" download>Scarica {nome}</a></p>'
                   f'<p class="solostampa">Lo zip si scarica dalla web app (indirizzo in fondo).</p>')
    if p.get("prompt_verifica"):
        prompt = DATI["verifica_prompt_2"] if p["prompt_verifica"] == 2 else DATI["verifica_prompt"]
        out.append(blocco_comando(prompt, "Messaggio da incollare in Claude"))
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


def fasi_livello(livello):
    """Fasi del livello con il loro numero: il livello 1 parte da 0 («Prima di cominciare»), il 2 da 1."""
    fasi = [f for f in DATI["fasi"] if f["livello"] == livello]
    return list(enumerate(fasi, 0 if livello == 1 else 1))


def passi_livello(so, livello):
    ids = {f["id"] for f in DATI["fasi"] if f["livello"] == livello}
    return [p for p in DATI[so] if p["fase"] in ids]


def guida_html(so, livello):
    parti, n = [], 0
    for i, f in fasi_livello(livello):
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


def slide_fase(i, f, totale):
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
    return (f'<section class="slide"><p class="kicker">Fase {i} di {totale}</p>'
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
    fasi1 = fasi_livello(1)
    for i, f in fasi1:
        if f["id"] != "verifica":
            s.append(slide_fase(i, f, len(fasi1) - 1))
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
    # livello 2
    s.append(f'<section class="slide copertina"><p class="kicker">Livello 2</p><h1>I siti e il tuo second brain</h1>'
             f'<p class="sotto">{testo(DATI["sottotitolo_2"])}</p></section>')
    s.append('<section class="slide"><h2>Come funziona</h2><ol class="grande">'
             '<li><strong>Siti/</strong>: Claude copia e legge i siti NPK, MATE, MAK, TRK e il sito agenti.</li>'
             '<li><strong>Second Brain/</strong>: con quelle copie scrive il tuo wiki, un marchio alla volta (metodo di Karpathy).</li>'
             '<li><strong>Obsidian</strong>: il wiki si sfoglia come un sito; a Claude si fanno domande e risponde citando le pagine.</li>'
             '<li>Un lavoro lungo per conversazione, poi <code>/clear</code>: Claude resta preciso e il piano Pro basta.</li>'
             '</ol></section>')
    fasi2 = fasi_livello(2)
    for i, f in fasi2:
        if f["id"] != "l2-obsidian":
            s.append(slide_fase(i, f, len(fasi2)))
    s.append('<section class="slide"><h2>La verifica del livello 2</h2><p class="ob">Si incolla nel pannello di Claude, in VS Code:</p>'
             f'<blockquote>{testo(DATI["verifica_prompt_2"])}</blockquote></section>')
    return "\n".join(s)


MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto",
        "settembre", "ottobre", "novembre", "dicembre"]


def ore(minuti):
    h = round(minuti / 60)
    return f"{h} ore" if h != 1 else "un'ora"


def data_it(iso):
    a, m, g = iso.split("-")
    return f"{int(g)} {MESI[int(m) - 1]} {a}"


def crea_zip(sorgente, nome):
    dest = BASE / nome
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(sorgente.rglob("*")):
            if f.is_file() and f.name != ".DS_Store" and "__pycache__" not in f.parts:
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
        "<!--TITOLO_2-->": testo(DATI["titolo_2"]),
        "<!--SOTTOTITOLO_2-->": testo(DATI["sottotitolo_2"]),
        "<!--MINUTI_MAC-->": str(sum(p["minuti"] for p in passi_livello("mac", 1))),
        "<!--MINUTI_WIN-->": str(sum(p["minuti"] for p in passi_livello("windows", 1))),
        "<!--ORE2_MAC-->": ore(sum(p["minuti"] for p in passi_livello("mac", 2))),
        "<!--ORE2_WIN-->": ore(sum(p["minuti"] for p in passi_livello("windows", 2))),
        "<!--GUIDA_MAC-->": guida_html("mac", 1),
        "<!--GUIDA_WIN-->": guida_html("windows", 1),
        "<!--GUIDA2_MAC-->": guida_html("mac", 2),
        "<!--GUIDA2_WIN-->": guida_html("windows", 2),
    }
    resti = [k for k in sost if k not in (BASE / "index.template.html").read_text(encoding="utf-8")]
    if resti:
        sys.exit("Segnaposto mancanti in index.template.html: " + ", ".join(resti))
    pagina = (BASE / "index.template.html").read_text(encoding="utf-8")
    for k, v in sost.items():
        pagina = pagina.replace(k, v)
    (BASE / "index.html").write_text(pagina, encoding="utf-8")

    slide = (BASE / "slides.template.html").read_text(encoding="utf-8").replace("<!--SLIDES-->", slides_html())
    (BASE / "slides.html").write_text(slide, encoding="utf-8")

    zip1 = crea_zip(BASE / "starter" / "Claude Workspace", DATI["zip"])
    zip2 = crea_zip(BASE / "starter-livello-2", DATI["zip_2"])
    for liv in (1, 2):
        print(f"index.html livello {liv}: {len(passi_livello('mac', liv))} passaggi Mac, "
              f"{len(passi_livello('windows', liv))} Windows")
    n_slide = slide.count('<section class="slide')
    print(f"slides.html: {n_slide} slide")
    for z in (zip1, zip2):
        print(f"{z.name}: {len(zipfile.ZipFile(z).namelist())} file")


if __name__ == "__main__":
    main()

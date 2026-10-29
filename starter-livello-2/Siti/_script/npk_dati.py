#!/usr/bin/env python3
"""Scarica i dati strutturati di noproblemkit.com (i configuratori NPK) e li salva in
Siti/NPK/dati/ come CSV: ruotini, kit e antifurti per vettura, calze e catene per misura, veicoli.

Uso:  python3 Siti/_script/npk_dati.py                 (configuratori: il caso normale)
      python3 Siti/_script/npk_dati.py --solo rivenditori-base   (solo l'elenco dei rivenditori NPK)

Le pagine del sito si copiano a parte con scarica_sito.py; queste sono le tabelle che il sito
mostra solo dentro i configuratori (circa 9.000 schede), per questo servono uno script dedicato.

Sorgenti (tutte pubbliche, le stesse che usa il sito dal browser):
  - cataloghi   : endpoint ajax JetSmartFilters dei configuratori, 100 schede per chiamata
  - veicoli     : endpoint gerarchico marca -> modello -> anno (filtro 30167)
  - rivenditori : /wp-content/uploads/retailers.json + scheda singola (città, CAP, nazione)

Le risposte grezze restano in cache: rilanciando lo script riparte da dove si era fermato.
Per un aggiornamento pulito, cancellare la cartella di cache.
"""
import argparse, csv, gzip, hashlib, html, json, os, re, sys, tempfile, time
import urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor

BASE = "https://noproblemkit.com"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
      "(KHTML, like Gecko) Version/17.0 Safari/605.1.15")
QUI = os.path.dirname(os.path.abspath(__file__))
DATI = os.path.join(QUI, "..", "NPK", "dati")
WORKERS = 2  # richieste in parallelo: poche, per non pesare sul sito
FILTRO_VEICOLO = "30167"

# post type -> (pagina, query id del loop, widget id, post id della pagina)
CATALOGHI = {
    "ground_spare_wheel": ("/prodotti/kit-ruota-di-scorta/", "loop-ruote", "0d4aaa4", "48545"),
    "antifurti": ("/prodotti/kit-bulloneria-antifurto/", "default", "6bbb9e7", "30053"),
    "ground_snow_socks": ("/prodotti/calze-da-neve/", "loop-calze", "20fbff6", "30055"),
    "ground_snow_chain": ("/prodotti/catene-da-neve/", "loop-catene", "1a35317", "30057"),
}

CACHE = None


def scarica(url, dati=None, tentativi=4):
    """GET/POST con cache su disco. Ritorna il testo della risposta."""
    chiave = hashlib.sha1((url + "|" + json.dumps(dati, sort_keys=True)).encode()).hexdigest()
    percorso = os.path.join(CACHE, chiave[:2], chiave)
    if os.path.exists(percorso):
        with gzip.open(percorso, "rt", encoding="utf-8") as f:
            return f.read()
    corpo = urllib.parse.urlencode(dati).encode() if dati else None
    intestazioni = {"User-Agent": UA, "Accept-Encoding": "gzip"}
    if dati:
        intestazioni["X-Requested-With"] = "XMLHttpRequest"
    for n in range(tentativi):
        try:
            req = urllib.request.Request(url, data=corpo, headers=intestazioni)
            with urllib.request.urlopen(req, timeout=60) as r:
                grezzo = r.read()
                if r.headers.get("Content-Encoding") == "gzip":
                    grezzo = gzip.decompress(grezzo)
            testo = grezzo.decode("utf-8", errors="replace")
            os.makedirs(os.path.dirname(percorso), exist_ok=True)
            with gzip.open(percorso, "wt", encoding="utf-8") as f:
                f.write(testo)
            return testo
        except Exception as e:  # rete instabile o 5xx: riprova con attesa crescente
            if n == tentativi - 1:
                print(f"  ERRORE {url} {dati and list(dati.items())[:3]}: {e}", file=sys.stderr)
                return ""
            time.sleep(2 * (n + 1))


def in_parallelo(funzione, elementi, etichetta):
    risultati, fatti = [], 0
    with ThreadPoolExecutor(WORKERS) as pool:
        for r in pool.map(funzione, elementi):
            risultati.append(r)
            fatti += 1
            if fatti % 250 == 0:
                print(f"  {etichetta}: {fatti}/{len(elementi)}", flush=True)
    return risultati


def testo(frammento):
    t = re.sub(r"<(script|style)\b.*?</\1>", "", frammento, flags=re.S)
    t = re.sub(r"<[^>]+>", "\n", t)
    return [r.strip() for r in html.unescape(t).split("\n") if r.strip()]


def scrivi_csv(nome, righe, colonne):
    os.makedirs(DATI, exist_ok=True)
    with open(os.path.join(DATI, nome), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=colonne, delimiter=";", extrasaction="ignore")
        w.writeheader()
        w.writerows(righe)
    print(f"-> dati/{nome}: {len(righe)} righe")


# ---------------------------------------------------------------- cataloghi

def chiamata_loop(post_type, pagina=1, filtri=None):
    percorso, query_id, widget, post_id = CATALOGHI[post_type]
    dati = {
        "action": "jet_smart_filters",
        "provider": f"epro-loop-builder/{query_id}",
        "defaults[post_status]": "publish",
        "defaults[post_type]": post_type,
        "defaults[orderby]": "ID",
        "defaults[order]": "asc",
        "defaults[posts_per_page]": "100",
        "settings[widget_id]": widget,
        "settings[filtered_post_id]": post_id,
        "paged": str(pagina),
    }
    for tassonomia, termine in (filtri or {}).items():
        dati[f"query[_tax_query_{tassonomia}]"] = str(termine)
    grezzo = scarica(f"{BASE}{percorso}?jsf_ajax=1", dati)
    try:
        d = json.loads(grezzo)
    except ValueError:
        return [], 0
    schede = re.split(r'(?=<div data-elementor-type="loop-item")', d.get("content", ""))[1:]
    return schede, int(d.get("pagination", {}).get("max_num_pages") or 0)


def tutte_le_schede(post_type):
    schede, pagine = chiamata_loop(post_type)
    for blocco, _ in in_parallelo(lambda p: chiamata_loop(post_type, p),
                                  list(range(2, pagine + 1)), post_type):
        schede += blocco
    return schede


def classi(scheda):
    c = re.search(r'class="([^"]*)"', scheda).group(1).split()
    out = {"id": next(x[5:] for x in c if x.startswith("post-"))}
    for x in c:
        m = re.match(r"ground_products_([a-z]+)-(.+)", x)
        if m:
            out[m.group(1)] = m.group(2)
    return out


def dopo(righe, etichetta):
    return righe[righe.index(etichetta) + 1] if etichetta in righe[:-1] else ""


def immagine(scheda):
    m = re.search(r'<img[^>]*src="([^"]+)"', scheda)
    return m.group(1) if m else ""


def prezzo(righe):
    return next((r.replace("€", "").strip() for r in righe if r.startswith("€")), "")


def codice(righe):
    """Il codice articolo è la riga subito prima del prezzo (o del pulsante)."""
    for i, r in enumerate(righe):
        if r.startswith("€") or r.lower() == "trova rivenditore":
            return righe[i - 1] if i else ""
    return ""


def estrai_ruotini():
    righe = []
    for s in tutte_le_schede("ground_spare_wheel"):
        t, c = testo(s), classi(s)
        righe.append({
            "post_id": c["id"], "marca_slug": c.get("brand", ""), "modello_slug": c.get("modello", ""),
            "anno_slug": c.get("anno", ""), "tipo": dopo(t, "Tipo:"), "pneumatico": dopo(t, "Pneumatico:"),
            "ingombro": dopo(t, "Ingombro:"), "ruota": dopo(t, "Ruota:"), "descrizione": t[0] if t else "",
            "codice": codice(t), "prezzo_sito_eur": prezzo(t), "immagine": immagine(s),
        })
    return righe


def estrai_misure(post_type):
    pagina = scarica(BASE + CATALOGHI[post_type][0])
    blocco = re.search(r'name="ground_products_diametro".*?</select>', pagina, re.S).group(0)
    diametri = dict(opzioni(blocco))
    righe = []
    for s in tutte_le_schede(post_type):
        t, c = testo(s), classi(s)
        if "Misura:" not in t:  # scheda segnaposto vuota presente sul sito
            continue
        righe.append({
            "diametro": diametri.get(c.get("diametro", ""), ""),
            "post_id": c["id"], "descrizione": t[0] if t else "", "linea": t[1] if len(t) > 1 else "",
            "misura": dopo(t, "Misura:"), "diametro_term_id": c.get("diametro", ""),
            "codice": codice(t), "prezzo_sito_eur": prezzo(t), "immagine": immagine(s),
        })
    return righe


def scheda_antifurto(s):
    t = testo(s)
    return {
        "post_id": classi(s)["id"], "titolo": t[0] if t else "",
        "id_auto": next((r.split(":", 1)[1].strip() for r in t if r.startswith("ID Auto:")), ""),
        "codice": next((r.split(":", 1)[1].strip() for r in t if r.startswith("Parte:")), ""),
        "descrizione": next((r for r in t[1:] if not re.match(r"(ID Auto|Parte):|TROVA", r, re.I)), ""),
        "immagine": immagine(s),
    }


# ------------------------------------------------------------------ veicoli

def opzioni(frammento):
    return [(v, html.unescape(html.unescape(e))) for v, e in
            re.findall(r'<option\s+value="(\d+)"\s+data-label="([^"]*)"', frammento)]


def livello(profondita, valori):
    dati = {"action": "jet_smart_filters_get_hierarchy_level", "filter_id": FILTRO_VEICOLO,
            "depth": str(profondita)}
    for i, (tassonomia, termine) in enumerate(valori):
        dati[f"values[{i}][value]"] = termine
        dati[f"values[{i}][tax]"] = tassonomia
    try:
        return opzioni(json.loads(scarica(f"{BASE}/wp-admin/admin-ajax.php", dati))["data"][f"level_{profondita}"])
    except (ValueError, KeyError, TypeError):
        return []


def albero_veicoli():
    """Lista di (marca_id, marca, modello_id, modello, [(anno_id, anno), ...])."""
    pagina = scarica(f"{BASE}/prodotti/kit-bulloneria-antifurto/")
    blocco = re.search(r'name="ground_products_brand".*?</select>', pagina, re.S).group(0)
    marche = opzioni(blocco)
    modelli = in_parallelo(lambda m: livello(1, [("ground_products_brand", m[0])]), marche, "modelli")
    coppie = [(mid, marca, oid, modello) for (mid, marca), lista in zip(marche, modelli)
              for oid, modello in lista]
    anni = in_parallelo(lambda c: livello(2, [("ground_products_brand", c[0]),
                                              ("ground_products_modello", c[2])]), coppie, "anni")
    return [c + (a,) for c, a in zip(coppie, anni)]


def slug(etichetta):
    s = re.sub(r"[^a-z0-9]+", "-", etichetta.lower()).strip("-")
    return s


def fai_veicoli_e_cataloghi(solo):
    albero = albero_veicoli()
    scrivi_csv("veicoli.csv",
               [{"marca": ma, "modello": mo, "anno": an, "marca_term_id": mid,
                 "modello_term_id": oid, "anno_term_id": aid}
                for mid, ma, oid, mo, anni in albero for aid, an in (anni or [("", "")])],
               ["marca", "modello", "anno", "marca_term_id", "modello_term_id", "anno_term_id"])

    # --- ruotini: le schede portano gli slug dei termini, le etichette vengono dall'albero
    marca_da_slug = {slug(ma): ma for _, ma, _, _, _ in albero}
    modello_da_slug, anni_modello = {}, {}
    for _, ma, _, mo, anni in albero:
        modello_da_slug.setdefault((slug(ma), slug(mo)), mo)
        anni_modello.setdefault((slug(ma), slug(mo)), []).extend(anni)
    # lo slug di un termine a volte è il suo term id, a volte non coincide con l'etichetta
    modello_da_id = {oid: mo for _, _, oid, mo, _ in albero}
    anni_da_modello_id = {oid: anni for _, _, oid, _, anni in albero}
    anno_da_id = {aid: an for _, _, _, _, anni in albero for aid, an in anni}
    anno_da_slug = {slug(an): an for an in anno_da_id.values()}
    ruotini = estrai_ruotini()
    for r in ruotini:
        k = (r["marca_slug"], r["modello_slug"])
        r["marca"] = marca_da_slug.get(r["marca_slug"], r["marca_slug"].upper())
        r["modello"] = (modello_da_slug.get(k) or modello_da_id.get(r["modello_slug"])
                        or r["modello_slug"].replace("-", " ").upper())
        candidati = anni_modello.get(k) or anni_da_modello_id.get(r["modello_slug"], [])
        r["anno"] = next((an for aid, an in candidati
                          if r["anno_slug"] in (aid, slug(an))), "")
        if not r["anno"]:
            r["anno"] = anno_da_id.get(r["anno_slug"]) or anno_da_slug.get(r["anno_slug"], "")
        if not r["anno"] and len({an for _, an in candidati}) == 1:
            r["anno"] = candidati[0][1]
    scrivi_csv("ruotini.csv", ruotini,
               ["marca", "modello", "anno", "tipo", "pneumatico", "ingombro", "ruota", "codice",
                "prezzo_sito_eur", "descrizione", "immagine", "marca_slug", "modello_slug",
                "anno_slug", "post_id"])

    scrivi_csv("calze-da-neve.csv", estrai_misure("ground_snow_socks"),
               ["diametro", "misura", "linea", "descrizione", "codice", "prezzo_sito_eur", "immagine", "post_id"])
    scrivi_csv("catene-da-neve.csv", estrai_misure("ground_snow_chain"),
               ["diametro", "misura", "linea", "descrizione", "codice", "prezzo_sito_eur", "immagine", "post_id"])

    # --- antifurti: la scheda porta solo "ID Auto" (marca.modello.anno in codice).
    # Si interroga il configuratore modello per modello per risalire alle etichette.
    antifurti = {a["post_id"]: a for a in map(scheda_antifurto, tutte_le_schede("antifurti"))}

    def per_modello(v):
        mid, _, oid, _, _ = v
        return chiamata_loop("antifurti", 1, {"ground_products_brand": mid,
                                              "ground_products_modello": oid})[0]

    risposte = in_parallelo(per_modello, albero, "antifurti per modello")
    da_dettagliare = []
    for v, schede in zip(albero, risposte):
        mid, ma, oid, mo, anni = v
        trovati = [scheda_antifurto(s)["post_id"] for s in schede]
        for pid in trovati:
            if pid in antifurti:
                antifurti[pid].update(marca=ma, modello=mo)
                if len(anni) == 1:
                    antifurti[pid]["anno"] = anni[0][1]
        if len(anni) > 1 and trovati:
            da_dettagliare += [(mid, oid, aid, an) for aid, an in anni]

    def per_anno(x):
        mid, oid, aid, _ = x
        return chiamata_loop("antifurti", 1, {"ground_products_brand": mid,
                                              "ground_products_modello": oid,
                                              "ground_products_anno": aid})[0]

    for (_, _, _, an), schede in zip(da_dettagliare,
                                     in_parallelo(per_anno, da_dettagliare, "antifurti per anno")):
        for s in schede:
            pid = scheda_antifurto(s)["post_id"]
            if pid in antifurti:
                antifurti[pid]["anno"] = an
    scrivi_csv("antifurti.csv",
               sorted(antifurti.values(), key=lambda a: (a.get("marca", "~"), a.get("modello", ""), a["id_auto"])),
               ["marca", "modello", "anno", "id_auto", "codice", "descrizione", "immagine", "titolo", "post_id"])


# -------------------------------------------------------------- rivenditori

CAMPI_SCHEDA = {"indirizzo": "d685e43", "citta": "9856537", "cap": "35ed875", "nazione": "d05d27f",
                "telefono": "d25e873", "email": "d5187a2"}


def fai_rivenditori(con_schede=True):
    """con_schede=False: solo il JSON della mappa (1 chiamata, niente città/CAP/nazione)."""
    base = {str(r["id"]): r for r in json.loads(scarica(f"{BASE}/wp-content/uploads/retailers.json"))}
    indice = scarica(f"{BASE}/sitemap_index.xml")
    url_schede = []
    for sm in re.findall(r"<loc>([^<]*ground_catalog-sitemap[^<]*)</loc>", indice):
        url_schede += [u for u in re.findall(r"<loc>([^<]+)</loc>", scarica(sm)) if "/rivenditori/" in u]

    def leggi(url):
        pagina = scarica(url)
        r = {"url": url}
        m = re.search(r"\bpostid-(\d+)", pagina)
        r["id"] = m.group(1) if m else ""
        for campo, el in CAMPI_SCHEDA.items():
            m = re.search(r'elementor-element-%s\b[^>]*>(.*?)</div>' % el, pagina, re.S)
            r[campo] = " ".join(testo(m.group(1))).strip(" ,") if m else ""
        m = re.search(r"<h1[^>]*>(.*?)</h1>", pagina, re.S)
        r["ragione_sociale"] = " ".join(testo(m.group(1))) if m else ""
        return r

    if con_schede:  # ~7.000 pagine a ~2 s l'una: circa un'ora
        righe = in_parallelo(leggi, url_schede, "schede rivenditore")
    else:
        righe = []
    visti = set()
    for r in righe:
        b = base.get(r["id"], {})
        visti.add(r["id"])
        r["lat"], r["lng"] = b.get("lat", ""), b.get("lng", "")
        r["ragione_sociale"] = r["ragione_sociale"] or html.unescape(b.get("title", ""))
        for campo in ("indirizzo", "telefono", "email"):
            r[campo] = r[campo] or b.get(campo, "")
    for pid, b in base.items():  # presenti nel JSON della mappa ma senza scheda in sitemap
        if pid not in visti:
            righe.append({"id": pid, "ragione_sociale": html.unescape(b.get("title", "")),
                          "indirizzo": b.get("indirizzo", ""), "telefono": b.get("telefono", ""),
                          "email": b.get("email", ""), "lat": b.get("lat", ""), "lng": b.get("lng", ""),
                          "url": ""})
    if not con_schede:
        for r in righe:
            r["ragione_sociale"] = re.sub(r"\s+", " ", r["ragione_sociale"]).strip()
    righe.sort(key=lambda r: (r.get("nazione", ""), r.get("cap", ""), r["ragione_sociale"]))
    scrivi_csv("rivenditori.csv", righe,
               ["ragione_sociale", "indirizzo", "cap", "citta", "nazione", "telefono", "email",
                "lat", "lng", "url", "id"])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default=os.path.join(tempfile.gettempdir(), "noproblemkit-cache"))
    ap.add_argument("--solo", choices=["cataloghi", "rivenditori", "rivenditori-base"], default="cataloghi")
    a = ap.parse_args()
    CACHE = a.cache
    os.makedirs(CACHE, exist_ok=True)
    if a.solo in (None, "cataloghi"):
        fai_veicoli_e_cataloghi(a.solo)
    if a.solo != "cataloghi":
        fai_rivenditori(con_schede=a.solo != "rivenditori-base")

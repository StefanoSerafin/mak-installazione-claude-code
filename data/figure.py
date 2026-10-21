"""Disegni schematici di VS Code (SVG inline) per la guida.
Non sono screenshot: riproducono la disposizione di VS Code con i punti da cliccare numerati in rosso.
Ogni figura: funzione(os) -> (svg, didascalia). os è "mac" o "windows"."""

from html import escape

W, H = 640, 380
BG, SIDE, ACT, BORDO = "#1f1f1f", "#181818", "#181818", "#2b2b2b"
TESTO, SPENTO, BLU, ROSSO = "#cccccc", "#8b8b8b", "#0078d4", "#e5433d"
FONT = 'font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif"'
TOP = 30          # altezza barra del titolo
STATUS = 22       # altezza barra di stato
ACT_W = 40        # barra delle attività
SIDE_X, SIDE_W = 40, 170
CLAUDE_X = 430


def t(x, y, s, size=11, col=TESTO, peso="normal", ancora="start"):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{col}" font-weight="{peso}" '
            f'text-anchor="{ancora}" {FONT}>{escape(s)}</text>')


def rett(x, y, w, h, col, r=0, extra=""):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{col}" {extra}/>'


def segno(n, x, y):
    """Pallino rosso numerato."""
    return (f'<circle cx="{x}" cy="{y}" r="12" fill="{ROSSO}" stroke="#fff" stroke-width="2"/>'
            + t(x, y + 4.5, str(n), 13, "#fff", "bold", "middle"))


def cornice(x, y, w, h):
    """Riquadro rosso attorno al punto da cliccare."""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="none" stroke="{ROSSO}" stroke-width="3"/>'


def finestra(os, titolo="Claude Workspace — Visual Studio Code"):
    p = [rett(0, 0, W, H, BG, 10), rett(0, 0, W, TOP, "#181818", 10), rett(0, TOP - 10, W, 10, "#181818")]
    if os == "mac":
        for i, c in enumerate(("#ff5f57", "#febc2e", "#28c840")):
            p.append(f'<circle cx="{16 + i * 18}" cy="15" r="6" fill="{c}"/>')
        p.append(t(W / 2, 19, titolo, 11, SPENTO, ancora="middle"))
    else:
        voci = ["File", "Edit", "Selection", "View", "Go", "Run", "Terminal", "Help"]
        x = 34
        p.append(f'<rect x="10" y="9" width="14" height="12" rx="2" fill="{BLU}"/>')
        for v in voci:
            p.append(t(x, 19, v, 11, TESTO))
            x += len(v) * 6.4 + 12
        p.append(t(W - 14, 20, "—   ☐   ✕", 11, SPENTO, ancora="end"))
    return "".join(p)


def barra_attivita(acceso=None):
    """Icone a sinistra: 0 Explorer, 1 Search, 2 Source Control, 3 Extensions, 4 Claude."""
    p = [rett(0, TOP, ACT_W, H - TOP - STATUS, ACT), f'<line x1="{ACT_W}" y1="{TOP}" x2="{ACT_W}" y2="{H - STATUS}" stroke="{BORDO}"/>']
    for i in range(5):
        y = TOP + 14 + i * 38
        col = "#ffffff" if i == acceso else SPENTO
        if i == acceso:
            p.append(rett(0, y - 6, 3, 34, "#ffffff"))
        if i == 0:   # file
            p.append(f'<rect x="12" y="{y}" width="12" height="16" rx="1" fill="none" stroke="{col}" stroke-width="1.6"/>'
                     f'<rect x="16" y="{y + 4}" width="12" height="16" rx="1" fill="{ACT}" stroke="{col}" stroke-width="1.6"/>')
        elif i == 1:  # cerca
            p.append(f'<circle cx="19" cy="{y + 8}" r="6" fill="none" stroke="{col}" stroke-width="1.8"/>'
                     f'<line x1="23" y1="{y + 12}" x2="28" y2="{y + 18}" stroke="{col}" stroke-width="2"/>')
        elif i == 2:  # git
            p.append(f'<circle cx="15" cy="{y + 3}" r="3" fill="none" stroke="{col}" stroke-width="1.6"/>'
                     f'<circle cx="15" cy="{y + 18}" r="3" fill="none" stroke="{col}" stroke-width="1.6"/>'
                     f'<circle cx="26" cy="{y + 8}" r="3" fill="none" stroke="{col}" stroke-width="1.6"/>'
                     f'<line x1="15" y1="{y + 6}" x2="15" y2="{y + 15}" stroke="{col}" stroke-width="1.6"/>')
        elif i == 3:  # estensioni: quattro quadrati, uno staccato
            for dx, dy in ((0, 7), (8, 7), (0, 15)):
                p.append(f'<rect x="{11 + dx}" y="{y + dy - 2}" width="7" height="7" fill="none" stroke="{col}" stroke-width="1.6"/>')
            p.append(f'<rect x="{22}" y="{y - 2}" width="7" height="7" fill="none" stroke="{col}" stroke-width="1.6" transform="rotate(45 25.5 {y + 1.5})"/>')
        else:         # scintilla di Claude
            p.append(t(20, y + 16, "✻", 19, "#d97757" if i != acceso else "#ffb08a", "bold", "middle"))
    return "".join(p)


def barra_stato(evidenzia=False):
    p = [rett(0, H - STATUS, W, STATUS, "#181818"), f'<line x1="0" y1="{H - STATUS}" x2="{W}" y2="{H - STATUS}" stroke="{BORDO}"/>',
         t(10, H - 7, "main", 10, SPENTO), t(W - 12, H - 7, "✻ Claude Code", 11, TESTO, ancora="end")]
    return "".join(p)


def esplora(file=True):
    p = [rett(SIDE_X, TOP, SIDE_W, H - TOP - STATUS, SIDE), f'<line x1="{SIDE_X + SIDE_W}" y1="{TOP}" x2="{SIDE_X + SIDE_W}" y2="{H - STATUS}" stroke="{BORDO}"/>',
         t(SIDE_X + 12, TOP + 20, "EXPLORER", 10, SPENTO, "bold"),
         t(SIDE_X + 12, TOP + 42, "⌄ CLAUDE WORKSPACE", 10, TESTO, "bold")]
    if file:
        voci = ["› .claude", "› Campagne", "› Clienti", "› Listini", "› Tool", "   CLAUDE.md", "   cose-che-posso-fare.txt"]
        for i, v in enumerate(voci):
            p.append(t(SIDE_X + 18, TOP + 64 + i * 20, v, 11, TESTO))
    return "".join(p)


def editor(x0=SIDE_X + SIDE_W, x1=CLAUDE_X):
    p = [rett(x0, TOP, x1 - x0, H - TOP - STATUS, BG)]
    for i, w in enumerate((140, 180, 90, 160, 120, 170, 60, 150)):
        p.append(rett(x0 + 34, TOP + 24 + i * 18, w * (x1 - x0) / 260, 6, "#3a3a3a", 3))
        p.append(t(x0 + 22, TOP + 30 + i * 18, str(i + 1), 9, "#5a5a5a", ancora="end"))
    return "".join(p)


def pannello_claude(stato="chat"):
    x, w = CLAUDE_X, W - CLAUDE_X
    p = [rett(x, TOP, w, H - TOP - STATUS, SIDE), f'<line x1="{x}" y1="{TOP}" x2="{x}" y2="{H - STATUS}" stroke="{BORDO}"/>',
         t(x + 12, TOP + 20, "✻ Claude Code", 11, TESTO, "bold")]
    if stato == "login":
        p += [t(x + w / 2, TOP + 120, "✻", 40, "#d97757", "bold", "middle"),
              t(x + w / 2, TOP + 150, "Claude Code", 14, TESTO, "bold", "middle"),
              rett(x + 40, TOP + 175, w - 80, 30, "#d97757", 6),
              t(x + w / 2, TOP + 195, "Sign in", 12, "#fff", "bold", "middle")]
    else:
        p += [rett(x + 60, TOP + 40, w - 72, 26, "#2d2d2d", 8), t(x + 70, TOP + 57, "Che modello sei?", 11, TESTO),
              rett(x + 12, TOP + 80, w - 50, 6, "#3a3a3a", 3), rett(x + 12, TOP + 94, w - 70, 6, "#3a3a3a", 3),
              rett(x + 12, TOP + 108, w - 90, 6, "#3a3a3a", 3),
              rett(x + 10, H - STATUS - 56, w - 20, 44, "#2d2d2d", 8, f'stroke="{BORDO}"'),
              t(x + 20, H - STATUS - 30, "Scrivi qui il messaggio…", 11, SPENTO)]
    return "".join(p)


def svg(corpo, etichetta):
    return (f'<svg class="figura-svg" viewBox="0 0 {W} {H}" role="img" aria-label="{escape(etichetta)}" '
            f'xmlns="http://www.w3.org/2000/svg">{corpo}</svg>')


# ---------- figure ----------

def panoramica(os):
    c = (finestra(os) + barra_attivita(0) + esplora() + editor() + pannello_claude() + barra_stato()
         + segno(1, 20, TOP + 200) + cornice(SIDE_X + 4, TOP + 32, SIDE_W - 8, 160) + segno(2, SIDE_X + SIDE_W - 14, TOP + 46)
         + cornice(CLAUDE_X + 4, TOP + 4, W - CLAUDE_X - 8, H - TOP - STATUS - 8) + segno(3, W - 22, TOP + 22)
         + cornice(W - 98, H - STATUS - 1, 94, STATUS) + segno(4, W - 112, H - 34))
    return svg(c, "VS Code con il pannello di Claude"), [
        "Barra delle attività: in alto l'elenco dei file, più in basso le Estensioni e l'icona a scintilla di Claude.",
        "L'elenco dei file della cartella aperta (qui Claude Workspace).",
        "Il pannello di Claude: si scrive in basso, la risposta compare sopra.",
        "«✻ Claude Code» nella barra in basso: un clic apre il pannello di Claude anche quando non c'è nessun file aperto."]


def estensioni(os):
    side = (rett(SIDE_X, TOP, 220, H - TOP - STATUS, SIDE)
            + t(SIDE_X + 12, TOP + 20, "EXTENSIONS: MARKETPLACE", 10, SPENTO, "bold")
            + rett(SIDE_X + 10, TOP + 32, 200, 24, "#2a2a2a", 3, f'stroke="{BLU}"')
            + t(SIDE_X + 18, TOP + 48, "Claude Code", 11, TESTO)
            + rett(SIDE_X + 6, TOP + 66, 208, 64, "#04395e", 4)
            + rett(SIDE_X + 14, TOP + 76, 36, 36, "#d97757", 6) + t(SIDE_X + 32, TOP + 101, "✻", 22, "#fff", "bold", "middle")
            + t(SIDE_X + 58, TOP + 86, "Claude Code for VS Code", 11, TESTO, "bold")
            + t(SIDE_X + 58, TOP + 103, "Anthropic", 10, SPENTO)
            + f'<circle cx="{SIDE_X + 115}" cy="{TOP + 99}" r="5" fill="{BLU}"/>' + t(SIDE_X + 115, TOP + 102, "✓", 8, "#fff", "bold", "middle")
            + rett(SIDE_X + 160, TOP + 108, 46, 16, BLU, 2) + t(SIDE_X + 183, TOP + 120, "Install", 9, "#fff", "bold", "middle")
            + rett(SIDE_X + 6, TOP + 136, 208, 44, SIDE) + rett(SIDE_X + 14, TOP + 142, 30, 30, "#3a3a3a", 4)
            + t(SIDE_X + 52, TOP + 156, "Altre estensioni con nomi simili…", 10, SPENTO))
    c = (finestra(os) + barra_attivita(3) + editor(SIDE_X + 220, W) + side + barra_stato()
         + cornice(4, TOP + 120, 32, 30) + segno(1, 46, TOP + 118)
         + cornice(SIDE_X + 8, TOP + 30, 204, 28) + segno(2, SIDE_X + 226, TOP + 44)
         + cornice(SIDE_X + 54, TOP + 92, 70, 16) + segno(3, SIDE_X + 138, TOP + 100)
         + cornice(SIDE_X + 157, TOP + 105, 52, 22) + segno(4, SIDE_X + 226, TOP + 116))
    tasti = "⌘ + ⇧ + X" if os == "mac" else "Ctrl + Shift + X"
    return svg(c, "Installare l'estensione Claude Code"), [
        f"L'icona Estensioni (i quattro quadratini) oppure {tasti}.",
        "Nella casella di ricerca scrivi `Claude Code`.",
        "Controlla l'editore: Anthropic, con il bollino blu di verifica. Le estensioni con nomi simili di altri autori non vanno installate.",
        "Clicca «Install»."]


def apri_cartella(os):
    voci = ["New Text File", "New File…", "New Window", "—", "Open File…", "Open Folder…", "Open Recent  ›", "—", "Save"]
    if os == "mac":
        barra = (rett(0, 0, W, 22, "#e8e8e8") + t(14, 15, "", 12, "#000") + t(34, 15, "Code", 11, "#000", "bold")
                 + t(76, 15, "File", 11, "#000") + t(108, 15, "Edit   Selection   View   Go   Run   Terminal   Window   Help", 11, "#000"))
        y0, mx = 22, 70
        fondo = rett(0, 22, W, H - 22, "#2a2a2a")
        menu_col, menu_txt = "#f4f4f4", "#000"
    else:
        barra = finestra(os)
        y0, mx = TOP - 4, 28
        fondo = barra_attivita(0) + esplora(False) + editor(SIDE_X + SIDE_W, W) + barra_stato()
        menu_col, menu_txt = "#252526", TESTO
    menu = [rett(mx, y0 + 2, 200, 12 + len(voci) * 22, menu_col, 6, f'stroke="{BORDO}"')]
    for i, v in enumerate(voci):
        y = y0 + 8 + i * 22
        if v == "—":
            menu.append(f'<line x1="{mx + 8}" y1="{y + 11}" x2="{mx + 192}" y2="{y + 11}" stroke="#888" stroke-opacity=".4"/>')
            continue
        if v == "Open Folder…":
            menu.append(rett(mx + 4, y, 192, 20, BLU, 4))
            menu.append(t(mx + 14, y + 14, v, 11, "#fff"))
        else:
            menu.append(t(mx + 14, y + 14, v, 11, menu_txt))
    hi = y0 + 8 + 5 * 22
    pos_file = (90, 11) if os == "mac" else (44, 15)
    pos_segno = (56, 40) if os == "mac" else (14, 46)
    c = (fondo + barra + "".join(menu) + cornice(pos_file[0] - 18, pos_file[1] - 9, 36, 18)
         + segno(1, *pos_segno) + cornice(mx + 2, hi - 2, 196, 24) + segno(2, mx + 216, hi + 10))
    dove = "nella barra in alto dello schermo (su Mac i menu non sono dentro la finestra)" if os == "mac" else "in alto a sinistra nella finestra di VS Code"
    scelta = "«Open»" if os == "mac" else "«Seleziona cartella»"
    return svg(c, "Aprire la cartella di lavoro"), [
        f"Il menu File, {dove}.",
        f"«Open Folder…», poi Documenti → Claude Workspace e {scelta}."]


def fiducia(os):
    c = (finestra(os) + barra_attivita(0) + esplora(False) + editor(SIDE_X + SIDE_W, W) + barra_stato()
         + rett(0, 0, W, H, "#000", 10, 'fill-opacity=".45"')
         + rett(110, 70, 420, 220, "#252526", 10, f'stroke="{BORDO}"')
         + f'<path d="M150 88 l14 6 v12 c0 10 -7 16 -14 19 c-7 -3 -14 -9 -14 -19 v-12 z" fill="none" stroke="{BLU}" stroke-width="2.5"/>' + t(176, 104, "Do you trust the authors of the files", 13, TESTO, "bold")
         + t(176, 122, "in this folder?", 13, TESTO, "bold")
         + rett(176, 140, 330, 6, "#3a3a3a", 3) + rett(176, 154, 280, 6, "#3a3a3a", 3)
         + rett(176, 196, 200, 30, BLU, 4) + t(276, 215, "Yes, I trust the authors", 11, "#fff", "bold", "middle")
         + rett(176, 236, 200, 30, "#3a3a3a", 4) + t(276, 255, "No, I don't trust the authors", 11, TESTO, ancora="middle")
         + cornice(172, 192, 208, 38) + segno(1, 398, 211))
    return svg(c, "Domanda sulla fiducia nella cartella"), [
        "Rispondi «Yes, I trust the authors»: è la tua cartella. Per cartelle scaricate da altri o che non conosci si risponde no."]


def tavolozza(os, scritto, voci, scelta, etichetta, didascalia):
    x, w = 140, 360
    corpo = [finestra(os), barra_attivita(0), esplora(), editor(SIDE_X + SIDE_W, W), barra_stato(),
             rett(x, TOP + 6, w, 36 + len(voci) * 24, "#252526", 6, f'stroke="{BORDO}"'),
             rett(x + 8, TOP + 14, w - 16, 24, "#313131", 3, f'stroke="{BLU}"'), t(x + 16, TOP + 30, scritto, 11, TESTO)]
    for i, v in enumerate(voci):
        y = TOP + 46 + i * 24
        if i == scelta:
            corpo.append(rett(x + 4, y, w - 8, 22, "#04395e", 3))
        corpo.append(t(x + 14, y + 15, v, 11, TESTO))
    ys = TOP + 46 + scelta * 24
    corpo += [cornice(x + 6, TOP + 12, w - 12, 28), segno(1, x + w + 18, TOP + 26),
              cornice(x + 2, ys - 2, w - 4, 26), segno(2, x + w + 18, ys + 11)]
    return svg("".join(corpo), etichetta), didascalia


def tavolozza_code(os):
    return tavolozza(os, "> shell command",
                     ["Shell Command: Install 'code' and optionally 'copilot' commands…",
                      "Shell Command: Uninstall 'code' command from PATH"], 0,
                     "Attivare il comando code",
                     ["Premi ⌘ + ⇧ + P: si apre la barra dei comandi in alto. Scrivi `shell command`.",
                      "Scegli «Shell Command: Install 'code' … in PATH» (il testo esatto può cambiare un po'). Se chiede di installare anche Copilot, rispondi No."])


def tavolozza_icone(os):
    tasti = "⌘ + ⇧ + P" if os == "mac" else "Ctrl + Shift + P"
    c2, d2 = tavolozza(os, "Select File Icon Theme", ["None", "Minimal (Visual Studio Code)", "Seti (Visual Studio Code)", "VSCode Icons"], 3, "Tema delle icone", [])
    return c2, [f"Premi {tasti}, scrivi `file icon theme` e scegli «Preferences: File Icon Theme».",
                "Nell'elenco scegli «VSCode Icons»: file e cartelle prendono icone diverse a seconda del tipo."]


def login(os):
    c = (finestra(os) + barra_attivita(4) + esplora() + editor() + pannello_claude("login") + barra_stato()
         + cornice(W - 98, H - STATUS - 1, 94, STATUS) + segno(1, W - 112, H - 34)
         + cornice(CLAUDE_X + 36, TOP + 171, W - CLAUDE_X - 72, 38) + segno(2, W - 22, TOP + 190))
    return svg(c, "Accesso a Claude dentro VS Code"), [
        "Clicca «✻ Claude Code» in basso a destra (oppure l'icona a scintilla nella barra a sinistra).",
        "La prima volta compare «Sign in»: cliccalo, entra nel browser con il tuo account Claude e autorizza. Poi torna a VS Code."]


FIGURE = {
    "panoramica": panoramica,
    "estensioni": estensioni,
    "apri-cartella": apri_cartella,
    "fiducia": fiducia,
    "tavolozza-code": tavolozza_code,
    "tavolozza-icone": tavolozza_icone,
    "login": login,
}

#!/bin/zsh
# Rigenera i PDF stampabili da index.html: livello 1 (guida-mac, guida-windows)
# e livello 2 (livello-2-mac, livello-2-windows).
# Prima: python3 data/build.py
cd "${0:A:h}"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
for liv in 1 2; do
  for os in mac windows; do
    if [[ $liv == 1 ]]; then out="pdf/guida-$os.pdf"; else out="pdf/livello-2-$os.pdf"; fi
    "$CHROME" --headless --disable-gpu --no-pdf-header-footer --virtual-time-budget=3000 \
      --print-to-pdf="$out" "file://$PWD/index.html?os=$os&livello=$liv&stampa=1" 2>/dev/null
    echo "$out"
  done
done

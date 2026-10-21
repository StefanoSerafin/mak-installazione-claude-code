#!/bin/zsh
# Rigenera i PDF stampabili (uno per Mac, uno per Windows) da index.html.
# Prima: python3 data/build.py
cd "${0:A:h}"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
for os in mac windows; do
  "$CHROME" --headless --disable-gpu --no-pdf-header-footer --virtual-time-budget=3000 \
    --print-to-pdf="pdf/guida-$os.pdf" "file://$PWD/index.html?os=$os&stampa=1" 2>/dev/null
  echo "pdf/guida-$os.pdf"
done

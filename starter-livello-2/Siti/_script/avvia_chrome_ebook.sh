#!/bin/zsh
# Apre un Chrome separato da quello di tutti i giorni (profilo ~/.mak-ebook-chrome) sul sito
# agenti MAK, con la porta 9333 aperta perché ebook_pagine.py ed ebook_file.py possano leggerlo.
# Il login Google lo fai tu nella finestra che si apre: lo script non vede password.
# La prima volta fai il login; le volte successive il profilo lo ricorda.
open -na "Google Chrome" --args --user-data-dir="$HOME/.mak-ebook-chrome" \
  --remote-debugging-port=9333 "https://sites.google.com/view/makebookagente/home-page"
echo "Chrome aperto sul sito agenti. Fai il login con il tuo account Google e aspetta di vedere la home del sito."

# Apre un Chrome separato da quello di tutti i giorni (profilo %USERPROFILE%\.mak-ebook-chrome) sul sito
# agenti MAK, con la porta 9333 aperta perché ebook_pagine.py ed ebook_file.py possano leggerlo.
# Il login Google lo fai tu nella finestra che si apre: lo script non vede password.
$chrome = @("$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
            "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
            "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe") | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $chrome) { Write-Host "Non trovo Google Chrome: installalo da google.com/chrome e riprova."; exit 1 }
Start-Process $chrome -ArgumentList "--user-data-dir=`"$env:USERPROFILE\.mak-ebook-chrome`"", "--remote-debugging-port=9333", "https://sites.google.com/view/makebookagente/home-page"
Write-Host "Chrome aperto sul sito agenti. Fai il login con il tuo account Google e aspetta di vedere la home del sito."

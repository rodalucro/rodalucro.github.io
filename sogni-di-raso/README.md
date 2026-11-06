# Sogni di Raso — landing page lenzuola in seta 22 momme

Pagina unica (in italiano) per sognidiraso.com, con struttura ispirata a notturnnomilano.com e identità visiva di Sogni di Raso.

- `index.html` — la landing page. Prezzi, misure, colori, link Stripe e recensioni si cambiano nel blocco `CONFIGURAZIONE` in fondo al file.
- `img/` — logo, favicon e immagini di seta (generate da `tools/seta.py`, una per colore).
- `tools/seta.py` — rigenera le immagini di seta: `python3 tools/seta.py` (richiede numpy e Pillow).
- `plano/` — plano de conversão em português (jornada, comparação lado a lado, revisões de copy, prompts de fotos).

## Prima di pubblicare
1. Crea i Payment Link su Stripe (uno per misura + uno per 2 set) e incollali in `STRIPE_LINKS`. Finché sono vuoti il pulsante apre un'e-mail d'ordine.
2. Conferma prezzi, colori, misure e contenuto del set.
3. Sostituisci le immagini di seta con foto reali del prodotto appena possibile.

## Pubblicare su Netlify
Carica il contenuto di questa cartella (`index.html` + `img/`) come sito, oppure trascinala su app.netlify.com/drop.

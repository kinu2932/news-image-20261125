# news-image-20261125 — The World in One Page

One image that sums up the world's news of **Wednesday 25 November 2026**:
34 stories, one day, on a single front page.

## What it is

A hand-drawn newspaper front page, 1024x1024, rendered by a pure-stdlib
Python program (`main.py`, no Pillow, no network, no randomness):

- **Masthead** — "THE WORLD IN ONE PAGE", Wednesday 25 November 2026.
- **Hero** — Ukraine's drone boats sink a Russian warship off Benghazi,
  Libya; a Russian cargo ship is also hit in the Gulf of Finland, and
  Putin vows revenge.
- **Map** — "Where it happened": eight numbered hotspots (Benghazi,
  Finland, Antalya, Riyadh, Gaza, DR Congo, Seoul, Washington).
- **30 story cells** — COP31 collapses in Antalya; the CIA and ODNI are
  breached; Huawei is convicted by a US jury; Houthi strike on Riyadh's
  tallest tower; Trump pardons turkeys Freedom and Feathers; Giuliani
  receives the Medal of Freedom; NATO early-warning jets for Poland;
  700,000+ Russian troops dead; WHO flees DR Congo amid Ebola; Gaza
  death toll 74,746; and 20 more, across every region and beat.
- **Callout 34** — Iowa lead blast on hold: Trump orders the Army to
  wait for a court ruling.

## Run it

```sh
mkdir -p out
MAKEFUN_OUTPUT_DIR=out python3 main.py   # writes out/entry.png
```

The program writes `/output/entry.png` by default (set
`MAKEFUN_OUTPUT_DIR` to override). It is deterministic: repeated runs
produce byte-identical output.

## Sources

Reuters, AP, BBC, The New York Times, The Guardian, Middle East Eye,
The Conversation, Meduza/Mediazona — all stories first reported on
25 November 2026 (or in that day's news cycle).

## License

MIT — see LICENSE.

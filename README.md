# Anakalang Uma Atlas

Infinite-canvas workspace for re-reading the eight adat houses of Kampung Marapu Anakalang (Sumba Tengah): modular floor plans, vertical level stacks, access graphs and cross-house pattern boards.

The meso layer (kampung and desa) adds Handini, *Pola Pemukiman Kampung Adat Anakalang: Keberlanjutan Budaya Megalitik di Sumba Tengah*, KALPATARU 28(2), 2019: site plans of five kampung, the Desa Anakalang map, and settlement data.

The micro layer is based on Solissa & Pekulimu, *Tipologi Tata Ruang Dalam Rumah Adat Kampung Marapu Anakalang*, Langkau Betang: Jurnal Arsitektur 13(1), DOI 10.26418/lantang.v13i1.104857 (CC BY 4.0). Plans and sections are derived from that paper's figures.

## Layout

- `src/atlas.template.html` — the app (HTML/CSS/JS, no build dependencies)
- `data/meta.json` — house attributes and the room-type codebook
- `data/plans.json`, `data/upper.json` — traced geometry, normalised to the column module
- `data/p10_*.png` — section drawings (Tabel 3)
- `data/meso.json`, `data/meso/*.jpg` — kampung data, footprint signatures, site-plan figures
- `tools/` — extraction scripts (PyMuPDF) used to produce the data from the paper PDF
- `dist/` — built app (`index.html` opens locally)

## Build

```bash
python3 tools/build_app.py
```

Then open `dist/index.html`, or serve `dist/` with `python3 -m http.server --directory dist`.

## Notes on the data

- Room outlines were traced from the paper's vector drawings; each plan is warped onto a common grid (column lines at 0, 1, 2, 3.2, 4.2, 5.2 modules). The paper gives no metric scale.
- Doors come from door arcs in the drawings; bale-bale floors and terraces are treated as open. A few connections are manual (see `OV` in `tools/build.py`).
- Gender and sacredness coding is interpretive and editable in the app's Codebook.
- The extraction scripts expect the paper PDF as `paper.pdf` in the working directory; it is not included.

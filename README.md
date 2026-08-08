# Stars

Soft-SF 4X starmap prototype: galaxy generation, trade/homeworld seeding, Plotly
system views, and a Godot 4 client.

## Quick start (local)

```bash
python -m venv .venv
source .venv/bin/activate   # Windows WSL / macOS / Linux
pip install -r requirements.txt
python starmap.py           # generate galaxy → starmap.html
python starmap.py --serve   # click stars to open systems
```

Godot data:

```bash
python export_godot.py
# then open godot/ in Godot 4
```

## Publish online (GitHub Pages)

This repo includes a static export + Actions workflow.

1. Push to GitHub (`main` or `master`).
2. Repo **Settings → Pages → Build and deployment → Source: GitHub Actions**.
3. The workflow [`.github/workflows/deploy-pages.yml`](.github/workflows/deploy-pages.yml)
   runs `python export_web.py` and deploys the `site/` folder.

After the first successful run, the site is at:

`https://<user>.github.io/<repo>/`

### What the static site includes

- Full interactive **galaxy map** (`starmap.html`)
- Pre-built **featured systems**: named lore homeworlds (Sol, Brightstep / Neverdark, …)
- Other stars show a short note that the full on-demand render needs local `--serve`

### Build the site locally

```bash
python export_web.py
python -m http.server -d site 8080
# open http://127.0.0.1:8080/
```

## Layout

| Path | Role |
|------|------|
| `starmap.py` | Galaxy generation + Plotly map |
| `system_gen.py` / `system_view.py` | Per-system contents + HTML views |
| `export_godot.py` | JSON for the Godot client |
| `export_web.py` | Static site for GitHub Pages |
| `godot/` | Godot 4 project |
| `spec.txt` | Agent-maintained design spec |
| `instructions.txt` | Freeform scratchpad |

## License

Add a license before making the repo public if you care about reuse terms.
# space_thingie

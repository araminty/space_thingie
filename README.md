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

Pages serves the **Godot Web** export (not the Plotly `export_web.py` site).

1. Push to GitHub (`main` or `master`).
2. Repo **Settings → Pages → Build and deployment → Source: GitHub Actions**.
3. The workflow [`.github/workflows/deploy-pages.yml`](.github/workflows/deploy-pages.yml):
   - runs `python export_godot.py` (refreshes `godot/data/`)
   - installs Godot **4.7.1** + export templates
   - exports preset **Web** → `build/web/`
   - deploys that folder with `actions/deploy-pages`

After the first successful run, the site is at:

`https://<user>.github.io/<repo>/`

Godot’s default relative asset URLs work under a project-pages subpath (`/repo/`).
Web export keeps `variant/thread_support=false` so Pages does not need COOP/COEP headers.

### Build / test the Godot Web export locally

Requires Godot 4.7.x with the Web export template installed.

```bash
python export_godot.py
mkdir -p build/web
godot --headless --path godot --export-release "Web" build/web/index.html
python -m http.server -d build/web 8080
# open http://127.0.0.1:8080/
```

(`export_web.py` still builds the optional Plotly static site into `site/` for local use; it is not what Pages deploys.)

## Layout

| Path | Role |
|------|------|
| `starmap.py` | Galaxy generation + Plotly map |
| `system_gen.py` / `system_view.py` | Per-system contents + HTML views |
| `export_godot.py` | JSON/NPZ for the Godot client (`godot/data/`) |
| `export_web.py` | Optional Plotly static site (`site/`; not Pages) |
| `godot/` | Godot 4.7 project (Web preset → `../build/web/`) |
| `build/web/` | Godot Web export output (CI / local; gitignored) |
| `spec.txt` | Agent-maintained design spec |
| `instructions.txt` | Freeform scratchpad |

## License

Add a license before making the repo public if you care about reuse terms.
# space_thingie

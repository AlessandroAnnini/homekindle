# HomeKindle

HACS custom integration that renders a 600x800 grayscale PNG for a jailbroken Kindle Touch and serves it at:

`http://homeassistant.local:8123/api/homekindle/dashboard.png`

No auth. ETag / If-None-Match so the screensaver can skip an unchanged frame.

## Install with HACS

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=AlessandroAnnini&repository=homekindle&category=integration)

1. HACS is already installed.
2. Open the link above, or HACS → ⋮ → **Custom repositories** → `https://github.com/AlessandroAnnini/homekindle` → type **Integration**.
3. Download **HomeKindle** (pick a GitHub Release, not a raw branch).
4. Restart Home Assistant.
5. Settings → Devices & services → Add integration → **HomeKindle**.
6. Set location (or use HA home), Kindle model, weather model, secret ICS URL, and refresh minutes. Submit.
7. Check: `curl -I http://homeassistant.local:8123/api/homekindle/dashboard.png`

Manual install: copy `custom_components/homekindle/` into `/config/custom_components/homekindle/` and restart.

## Versioning

HACS shows the GitHub **Release** tag. After install, Home Assistant shows `version` from `custom_components/homekindle/manifest.json`. Those two numbers stay the same (`v0.1.1` tag, `"0.1.1"` in the manifest).

## Settings

| Field | Default | Notes |
| --- | --- | --- |
| Use HA home | on | Fills lat/lon from Home Assistant |
| Kindle model | Touch 600×800 | Paperwhite 1 is 758×1024 |
| Weather model | ICON-2I | Or Best match / ICON-EU / ECMWF / GFS |
| Calendar ICS URL | empty | Password field. Never put this in git |
| Refresh minutes | 15 | How often HA refetches. Set the **same** number on the Kindle screensaver |

Weather is Open-Meteo. Calendar is the ICS URL on the config entry (or `HOMEKINDLE_ICAL_URL` for local tests). If a fetch fails, the last good PNG is served. Tests use `tests/fixtures/sample.ics`.

## Kindle client

Jailbreak and restore for this Touch (serial prefix B011, firmware 5.3.7.3) live in the studio docs, not this git tree.

Point Online Screensaver at the HTTP URL above. Airplane mode except when fetching. Do not use HTTPS on this device.

## Local preview

```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/python scripts/serve_local.py 8129
# GET http://127.0.0.1:8129/api/homekindle/dashboard.png
.venv/bin/pytest tests -q
./scripts/e2e-dashboard.sh
```

## Layout

Lovelace sections YAML is shipped as `custom_components/homekindle/kindle.yaml`. Same keys as a Home Assistant YAML dashboard (`type: sections`, `max_columns: 2`).

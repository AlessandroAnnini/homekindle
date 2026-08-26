# HomeKindle

HACS custom integration that renders a 600x800 grayscale PNG for a jailbroken Kindle Touch and serves it at:

`http://homeassistant.fritz.box:8123/api/homekindle/dashboard.png`

No auth. ETag / If-None-Match so the screensaver can skip an unchanged frame.

## Install

1. Copy `custom_components/homekindle/` into `/config/custom_components/homekindle/` on HAOS, or add this repo in HACS.
2. Restart Home Assistant.
3. Add `homekindle:` to `configuration.yaml` (empty mapping is enough for fixtures).
4. Confirm: `curl -I http://homeassistant.local:8123/api/homekindle/dashboard.png`

This slice uses fixture weather and events. Live Open-Meteo / iCal / HA entities are the next feature.

## Kindle client

Jailbreak and restore steps for this Touch (serial prefix B011, firmware 5.3.7.3) live in the studio, not in this git tree:

- `gf-program/research/device/JAILBREAK.md`
- `gf-program/research/device/RESTORE.md`

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

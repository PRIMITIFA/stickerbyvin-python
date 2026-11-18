# stickerbyvin (Python)

Python client for the [StickerByVIN window sticker API](https://stickerbyvin.com/developers). Give it a VIN and it returns the **original Monroney window sticker** as JSON: total MSRP, base price, every option and package with its price, colours, fuel economy, standard equipment, the factory paint code and a link to the original PDF. It has no dependencies and uses only the standard library.

**Get a free API key (50 calls a month) at [stickerbyvin.com/developers](https://stickerbyvin.com/developers).**

```bash
pip install stickerbyvin
# until the PyPI release is live:
pip install git+https://github.com/PRIMITIFA/stickerbyvin-python
export SBV_KEY=sbv_live_...
```

```python
from stickerbyvin import StickerByVIN, StickerByVINError

sbv = StickerByVIN()  # or StickerByVIN(api_key="sbv_live_...")
vin = "1FTFW5L85TKD66889"

avail = sbv.availability(vin)          # all plans
v = avail["vehicle"]
print(v["year"], v["make"], v["model"], v["trim"])
print("Original sticker on file:", avail["originalSticker"]["onFile"])

if avail["originalSticker"]["onFile"]:
    try:
        s = sbv.sticker(vin)           # Starter plan and above
        print("Total MSRP:", s["sticker"]["totalMsrp"])
        for o in s["sticker"]["options"]:
            print(f'  {o["name"]}: {o["priceText"]}')
        sbv.sticker_pdf(vin, "window-sticker.pdf")
    except StickerByVINError as e:
        print(e.code, e.message)       # e.g. plan_required, sticker_not_available

print("Calls left this month:", sbv.quota_remaining)
```

Output for that real 2026 Ford F-150 Lariat:

```
2026 FORD F-150 Lariat
Original sticker on file: True
Total MSRP: 72550
  Equipment Group 501A: $2,670
  3.55 Electronic Lock Rr Axle: No charge
  7100# GVWR Package: Included
  Lariat Black Appearance Pkg: $1,475
  Tow/Haul Package: $1,010
  ...
```

## Methods

| Method | Endpoint | Plans |
|---|---|---|
| `availability(vin)` | `GET /api/v1/availability`: decode + whether the original sticker is on file | All |
| `decode(vin)` | `GET /api/v1/decode`: year, make, model, trim, engine, plant | All |
| `sticker(vin)` | `GET /api/v1/sticker`: parsed original sticker + paint code + 1-hour PDF link | Starter+ |
| `sticker_pdf(vin, path)` | Same as `sticker`, then saves the PDF | Starter+ |

Errors raise `StickerByVINError` with `.status`, `.code` and `.message`. Plans, coverage and the full response format: **https://stickerbyvin.com/developers**. OpenAPI spec: https://stickerbyvin.com/openapi.json.

## Coverage

Original stickers come straight from the carmaker for Ford and Lincoln, GM (Chevrolet, GMC, Buick, Cadillac) 2022 and newer, most Jeep, Ram, Dodge and Chrysler from 2017 on, and Subaru 2021 and newer. Call `availability()` first.

## License

MIT

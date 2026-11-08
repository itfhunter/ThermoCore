"""Baut frontend/thermocore-cards.js: Icons aus assets/icons als Masken einbetten.
Aufruf: python3 tools/build_cards.py"""
import base64, io, json, pathlib
from PIL import Image, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = {"radiator": "radiator_red", "minus_circle": "minus_circle_blue", "minus": "minus_white",
       "plus_circle": "plus_circle_blue", "plus": "plus_white", "power": "power_blue", "pump": "pump_yellow",
       "summer": "summer_white", "winter": "winter_white", "thermometer": "thermometer_blue",
       "manual": "manual_white", "home": "home_white"}

def mask(path):
    a = Image.open(path).convert("RGBA").getchannel("A").point(lambda v: 255 if v > 110 else 0)
    a = a.filter(ImageFilter.MedianFilter(9)).crop(a.getbbox() or (0, 0, 1, 1))
    s = max(a.size); pad = int(s * 0.06); c = Image.new("L", (s + 2 * pad,) * 2, 0)
    c.paste(a, ((s - a.size[0]) // 2 + pad, (s - a.size[1]) // 2 + pad))
    m = Image.new("RGBA", (96, 96), (255, 255, 255, 0)); m.putalpha(c.resize((96, 96), Image.LANCZOS))
    b = io.BytesIO(); m.save(b, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()

icons = {k: mask(ROOT / "assets/icons" / f"{v}.png") for k, v in SRC.items()}
fe = ROOT / "custom_components/thermocore/frontend"
(fe / "thermocore-cards.js").write_text((fe / "thermocore-cards.src.js").read_text().replace("__ICONS__", json.dumps(icons)))
print("ok", (fe / "thermocore-cards.js").stat().st_size, "bytes")

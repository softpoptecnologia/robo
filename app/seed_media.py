"""Gera imagens e gráficos de demonstração para evidências do seed."""

import os

from PIL import Image, ImageDraw, ImageFont


def _font(size=14, bold=False):
    candidates = [
        "arialbd.ttf" if bold else "arial.ttf",
        "segoeui.ttf",
        "DejaVuSans.ttf",
    ]
    for name in candidates:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _save(img, upload_dir, filename):
    os.makedirs(upload_dir, exist_ok=True)
    path = os.path.join(upload_dir, filename)
    img.save(path, quality=92)
    return filename


def _draw_station_photo():
    w, h = 900, 620
    img = Image.new("RGB", (w, h), "#e8f4fc")
    draw = ImageDraw.Draw(img)

    draw.rectangle((0, h - 120, w, h), fill="#8fbc8f")
    draw.rectangle((0, h - 120, w, h - 118), fill="#5a8f5a")
    draw.ellipse((120, 40, 780, 180), fill="#fff8dc")

    pole_x = 420
    draw.rectangle((pole_x + 28, 180, pole_x + 42, h - 120), fill="#64748b")
    box = (pole_x - 70, 250, pole_x + 110, 430)
    draw.rounded_rectangle(box, radius=12, fill="#1e293b", outline="#0f172a", width=3)
    draw.rounded_rectangle((box[0] + 12, box[1] + 12, box[2] - 12, box[1] + 70), radius=8, fill="#0ea5e9")
    draw.text((box[0] + 24, box[1] + 24), "BME280", fill="#fff", font=_font(22, True))
    draw.text((box[0] + 24, box[1] + 92), "T / UR / P", fill="#cbd5e1", font=_font(16))
    draw.rounded_rectangle((box[0] + 12, box[1] + 130, box[2] - 12, box[3] - 12), radius=8, fill="#111827")
    draw.text((box[0] + 28, box[1] + 155), "22.1 C", fill="#22c55e", font=_font(28, True))
    draw.text((box[0] + 28, box[1] + 205), "61 % UR", fill="#38bdf8", font=_font(22))
    draw.text((box[0] + 28, box[1] + 245), "1013 hPa", fill="#fbbf24", font=_font(20))

    draw.text((40, 24), "Estacao Meteorologica Escolar — Patio Central", fill="#0f172a", font=_font(24, True))
    draw.text((40, 56), "Encapsulamento IP54 | Altura 1,5 m | Orientacao Norte", fill="#475569", font=_font(16))
    draw.text((40, h - 90), "Clube de Robotica — demonstracao seed", fill="#334155", font=_font(14))
    return img


def _draw_calibration_photo():
    w, h = 900, 620
    img = Image.new("RGB", (w, h), "#f8fafc")
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, w, 70), fill="#1e3a5f")
    draw.text((30, 18), "Calibracao BME280 — 48 pontos de referencia", fill="#fff", font=_font(22, True))

    table_top = 110
    cols = ["Referencia", "Medido", "Erro", "Unidade"]
    xs = [60, 260, 460, 620]
    for i, label in enumerate(cols):
        draw.text((xs[i], table_top), label, fill="#0f172a", font=_font(16, True))
    draw.line((40, table_top + 28, w - 40, table_top + 28), fill="#cbd5e1", width=2)

    rows = [
        ("20.0", "20.4", "+0.4", "C"),
        ("25.0", "25.3", "+0.3", "C"),
        ("30.0", "30.2", "+0.2", "C"),
        ("50 %", "52.1 %", "+2.1", "UR"),
        ("70 %", "71.5 %", "+1.5", "UR"),
    ]
    y = table_top + 45
    for ref, med, err, unit in rows:
        draw.text((xs[0], y), ref, fill="#334155", font=_font(15))
        draw.text((xs[1], y), med, fill="#334155", font=_font(15))
        draw.text((xs[2], y), err, fill="#16a34a", font=_font(15, True))
        draw.text((xs[3], y), unit, fill="#64748b", font=_font(15))
        y += 34

    draw.rounded_rectangle((60, 360, 420, 560), radius=10, fill="#fff", outline="#94a3b8", width=2)
    draw.text((80, 380), "Regressao linear", fill="#0f172a", font=_font(16, True))
    draw.text((80, 415), "R2 = 0,97", fill="#2563eb", font=_font(28, True))
    draw.text((80, 465), "Offset aplicado no firmware", fill="#475569", font=_font(14))

    draw.rounded_rectangle((480, 360, 860, 560), radius=10, fill="#eff6ff", outline="#93c5fd", width=2)
    pts = [(500, 520), (560, 480), (620, 440), (680, 410), (740, 390), (800, 370), (840, 360)]
    draw.line(pts, fill="#2563eb", width=3)
    for x, yp in pts:
        draw.ellipse((x - 5, yp - 5, x + 5, yp + 5), fill="#1d4ed8")
    draw.text((500, 380), "T medida x T referencia", fill="#1e40af", font=_font(14, True))
    return img


def _draw_temp_bars():
    w, h = 900, 560
    img = Image.new("RGB", (w, h), "#ffffff")
    draw = ImageDraw.Draw(img)
    draw.text((30, 20), "Temperatura media — manha vs tarde (30 dias)", fill="#0f172a", font=_font(22, True))
    draw.text((30, 52), "n = 8.640 amostras | IC95%: 2,9–3,7 C", fill="#64748b", font=_font(14))

    chart = (120, 110, w - 80, h - 90)
    draw.rectangle(chart, outline="#cbd5e1", width=2)
    draw.line((chart[0], chart[3], chart[2], chart[3]), fill="#94a3b8", width=2)

    bar_w = 120
    morning_h = 180
    afternoon_h = 250
    base = chart[3]
    mx = chart[0] + 180
    ax = chart[0] + 480
    draw.rectangle((mx, base - morning_h, mx + bar_w, base), fill="#38bdf8")
    draw.rectangle((ax, base - afternoon_h, ax + bar_w, base), fill="#f97316")
    draw.text((mx + 10, base - morning_h - 28), "22,1 C", fill="#0369a1", font=_font(18, True))
    draw.text((ax + 10, base - afternoon_h - 28), "25,4 C", fill="#c2410c", font=_font(18, True))
    draw.text((mx + 8, base + 12), "Manha (6h–12h)", fill="#334155", font=_font(14))
    draw.text((ax + 8, base + 12), "Tarde (12h–18h)", fill="#334155", font=_font(14))
    draw.text((mx + 30, base + 36), "Delta T = 3,3 C", fill="#16a34a", font=_font(16, True))
    return img


def _draw_scatter():
    w, h = 900, 560
    img = Image.new("RGB", (w, h), "#ffffff")
    draw = ImageDraw.Draw(img)
    draw.text((30, 20), "Dispersao Temperatura x Umidade Relativa", fill="#0f172a", font=_font(22, True))
    draw.text((30, 52), "Pearson r = -0,68 (p < 0,01)", fill="#64748b", font=_font(14))

    chart = (100, 100, w - 60, h - 70)
    draw.rectangle(chart, outline="#cbd5e1", width=2)
    draw.text((chart[0] + 10, chart[3] + 8), "T (C)", fill="#475569", font=_font(13))
    draw.text((chart[2] - 50, chart[1] - 24), "UR (%)", fill="#475569", font=_font(13))

    import random
    random.seed(42)
    for _ in range(90):
        t = random.uniform(20, 28)
        ur = 78 - (t - 20) * 3.5 + random.uniform(-6, 6)
        ur = max(35, min(75, ur))
        x = chart[0] + (t - 20) / 8 * (chart[2] - chart[0])
        y = chart[3] - (ur - 35) / 40 * (chart[3] - chart[1])
        draw.ellipse((x - 4, y - 4, x + 4, y + 4), fill="#6366f1")

    x1, y1 = chart[0] + 40, chart[1] + 40
    x2, y2 = chart[2] - 40, chart[3] - 40
    draw.line((x1, y1, x2, y2), fill="#dc2626", width=2)
    return img


def _draw_pressure_series():
    w, h = 900, 560
    img = Image.new("RGB", (w, h), "#ffffff")
    draw = ImageDraw.Draw(img)
    draw.text((30, 20), "Pressao atmosferica — serie temporal (30 dias)", fill="#0f172a", font=_font(22, True))
    draw.text((30, 52), "Media 1012,8 hPa | sigma = 2,1", fill="#64748b", font=_font(14))

    chart = (90, 100, w - 50, h - 80)
    draw.rectangle(chart, outline="#cbd5e1", width=2)

    import math
    pts = []
    days = 30
    for i in range(days * 4):
        base = 1013 + math.sin(i / 8) * 2
        if 18 <= i <= 22:
            base -= 4
        x = chart[0] + i / (days * 4 - 1) * (chart[2] - chart[0])
        y = chart[3] - (base - 1008) / 10 * (chart[3] - chart[1])
        pts.append((x, y))
    draw.line(pts, fill="#0d9488", width=2)
    draw.text((chart[0] + 20, chart[1] + 10), "Queda ~4 hPa (chuva)", fill="#0f766e", font=_font(13, True))
    return img


def _draw_poster_photo():
    w, h = 900, 620
    img = Image.new("RGB", (w, h), "#f1f5f9")
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((80, 50, w - 80, h - 50), radius=16, fill="#fff", outline="#cbd5e1", width=3)
    draw.rectangle((80, 50, w - 80, 130), fill="#1e40af")
    draw.text((110, 72), "Feira de Ciencias 2025 — Menção Honrosa", fill="#fff", font=_font(24, True))
    draw.text((110, 170), "Microclima escolar medido com BME280", fill="#0f172a", font=_font(20, True))
    draw.text((110, 220), "• 8.640 registros em 30 dias", fill="#334155", font=_font(16))
    draw.text((110, 252), "• r = -0,68 entre T e UR", fill="#334155", font=_font(16))
    draw.text((110, 284), "• Delta T manha/tarde = 3,3 C", fill="#334155", font=_font(16))
    draw.rounded_rectangle((110, 340, 420, 520), radius=8, fill="#dbeafe")
    draw.text((130, 400), "Poster A0", fill="#1d4ed8", font=_font(28, True))
    draw.rounded_rectangle((480, 340, 820, 520), radius=8, fill="#dcfce7")
    draw.text((520, 390), "Nota banca: 9,2/10", fill="#15803d", font=_font(24, True))
    return img


def ensure_seed_media(upload_dir):
    """Cria PNGs de demonstracao se ainda nao existirem. Retorna mapa nome -> filename."""
    specs = {
        "seed_clima_estacao.jpg": _draw_station_photo,
        "seed_clima_calibracao.jpg": _draw_calibration_photo,
        "seed_clima_temp_barras.png": _draw_temp_bars,
        "seed_clima_scatter_t_ur.png": _draw_scatter,
        "seed_clima_pressao_serie.png": _draw_pressure_series,
        "seed_clima_poster_feira.jpg": _draw_poster_photo,
    }
    created = {}
    for filename, factory in specs.items():
        path = os.path.join(upload_dir, filename)
        if not os.path.exists(path):
            _save(factory(), upload_dir, filename)
        created[filename] = filename
    return created

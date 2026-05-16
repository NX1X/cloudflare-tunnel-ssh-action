"""One-off generator for the GitHub social preview (1280x640 PNG).

Renders assets/social-preview.svg via PySide6/QtSvg so the output is
crisp. Not part of the action; safe to delete after the PNG is produced.

Usage:
    pip install PySide6
    python scripts/_gen_social_preview.py
"""
import sys
from pathlib import Path

from PySide6.QtCore import QByteArray
from PySide6.QtGui import QGuiApplication, QImage, QPainter
from PySide6.QtSvg import QSvgRenderer

W, H = 1280, 640

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "social-preview.svg"
OUT = ROOT / "assets" / "social-preview.png"

svg = SRC.read_bytes()

app = QGuiApplication(sys.argv)
renderer = QSvgRenderer(QByteArray(svg))
image = QImage(W, H, QImage.Format_RGB32)
image.fill(0xFFF2740A)  # base brand orange, in case the SVG leaves gaps
painter = QPainter(image)
renderer.render(painter)
painter.end()

if not image.save(str(OUT), "PNG"):
    raise SystemExit("failed to write " + str(OUT))
print("wrote", OUT, image.width(), "x", image.height())

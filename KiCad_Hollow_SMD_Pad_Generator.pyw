#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KiCad Hollow SMD Pad Generator 2.8.3 — Tkinter GUI with optional STEP 3D preview.

One custom electrically connected SMD pad made from four adjacent copper
polygons forming an actual hollow rounded rectangular ring. The inner and
outer corner radii can be set independently. Files use .kicad_mod format.

Optional two closed solid F.Fab shield outlines (wall thickness selectable).
GUI languages: Ukrainian, English, German. Last GUI settings are stored in
KiCad_Hollow_SMD_Pad_Generator.settings.json next to this program.

Examples:
    python KiCad_Hollow_SMD_Pad_Generator.py
    python KiCad_Hollow_SMD_Pad_Generator.py --generate My_Shield.kicad_mod \
       --horizontal 19 --vertical 10.2 --radius 1.15 --inner-radius 0.4 --rim 1.5
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import ctypes
import ctypes.util
import json
import math
import os
from pathlib import Path
import re
import sys
import webbrowser

APP_VERSION = "2.8.3"
PROJECT_URL = "https://github.com/ozzysv/KiCad_Hollow_SMD_Pad_Generator"
APP_KEY = "KiCad_Hollow_SMD_Pad_Generator"
SETTINGS_FILENAME = APP_KEY + ".settings.json"
DEFAULT_FILENAME = "Shield_Centerline_19x10p2_R1p15_Ri0p3_W1p5.kicad_mod"
ANGLE_STEP = 5.0

I18N = {
    "uk": {
        'preview_3d': '3D Preview',
        'models_3d': '3D-модель (лише STEP / STP)',
        'add_3d': 'Додати модель…',
        'remove_3d': 'Видалити',
        'show_model': 'Показати',
        'embed_3d': 'Вбудувати STEP у файл футпринта',
        'opacity_3d': 'Непрозорість',
        'scale_3d': 'Масштаб',
        'rotation_3d': 'Поворот',
        'offset_3d': 'Зміщення (мм)',
        'model_missing': 'Спочатку виберіть файл STEP або STP.',
        'preview_requires': 'Для 3D-перегляду потрібні бібліотеки cadquery-ocp та vtk. Встановіть їх:\npython -m pip install cadquery-ocp vtk',
        'embedding_requires': 'Для вбудовування STEP потрібна бібліотека zstandard (або системна libzstd). Встановіть:\npython -m pip install zstandard',
        'failed_to_load_step': 'Не вдалося прочитати STEP-модель:\n{error}',
        'failed_3d': 'Помилка 3D-перегляду: {error}',
        'view_top': 'Зверху',
        'view_iso': 'Ізометрія',
        'view_side': 'Збоку',
        'view_bottom': 'Знизу',
        'fit_3d': 'Підігнати',
        'show_board': 'Показати плату',
        'status_no_model': 'Модель не вибрана',
        'auto_courtyard': 'Створити F.CrtYd автоматично',
        'paste_segmented': 'Сегментувати F.Paste',
        'paste_length': 'Макс. довжина апертури',
        'paste_gap': 'Проміжок між апертурами',
        'paste_inset': 'Відступ пасти від країв міді',
        'err_paste_params': 'Параметри апертур мають бути допустимими: довжина > 0, проміжок ≥ 0, відступ ≥ 0 та менше половини обідка.',
        'err_paste_span': 'Мало місця для сегментованої пасти. Зменште відступ, проміжок чи змініть радіуси.',
        "window_title": "KiCad Hollow SMD Pad Generator",
        "title": "KiCad Hollow SMD Pad Generator",
        "language": "Мова інтерфейсу",
        "dimension_mode": "Як задавати габарити",
        "centerline": "За середніми лініями мідного обідка",
        "outer": "За зовнішніми габаритами міді",
        "horizontal": "Горизонтальний розмір",
        "vertical": "Вертикальний розмір",
        "outer_radius": "Радіус зовнішніх кутів",
        "inner_radius": "Радіус внутрішніх кутів",
        "rim": "Ширина мідного обідка",
        "courtyard": "Відступ F.CrtYd",
        "pad_number": "Номер контакту",
        "mm": "мм",
        "mask": "F.Mask (відкрита мідь)",
        "paste": "F.Paste (паяльна паста)",
        "fab_shield": "Контури екрана F.Fab",
        "shield_thickness": "Товщина",
        "err_shield_thickness": "Товщина стінки має бути більшою за нуль і меншою за половину меншого габариту екрана.",
        "err_shield_radius": "Для однакового радіуса обох контурів F.Fab потрібно зменшити зовнішній радіус або товщину стінки.",
        "fab_enabled_legend": "Суцільні бірюзова й зелена лінії — два контури F.Fab з однаковим радіусом.",
        "fab_disabled_legend": "Блакитний пунктир — середня лінія мідного обідка.",
        "paste_note": "Для пайки екрана паяльну пасту іноді потрібно поділити на сегменти.",
        "filename": "Ім'я файлу",
        "folder": "Каталог збереження",
        "save": "Зберегти футпринт (.kicad_mod)",
        "preview": "Попередній перегляд (геометрія у масштабі)",
        "legend": "Червоний — F.Cu; темний центр — без міді; пурпуровий — Courtyard.",
        "outside": "Зовнішній розмір",
        "centerline_label": "По середній лінії",
        "rim_short": "Обідок",
        "outer_r_short": "R зовн.",
        "inner_r_short": "R внутр.",
        "inside": "Отвір",
        "one_pad": "Файл міститиме один електричний контакт із чотирьох суміжних полігонів міді.",
        "invalid_geometry": "Неправильні параметри геометрії",
        "check_geometry": "Перевірте розміри та радіуси",
        "invalid_number": "Неправильне число",
        "err_nonpositive": "Розміри й ширина обідка мають бути більшими за нуль.",
        "err_negative_courtyard": "Відступ Courtyard не може бути від'ємним.",
        "err_negative_radius": "Радіуси не можуть бути від'ємними.",
        "err_outer_radius": "Зовнішній радіус перевищує половину меншого зовнішнього габариту.",
        "err_inner_radius": "Внутрішній радіус перевищує половину меншого розміру отвору.",
        "err_no_hole": "Обідок надто широкий — внутрішній отвір відсутній.",
        "err_mode": "Невідомий спосіб вимірювання.",
        "err_filename": "Вкажіть допустиме ім'я файлу без заборонених символів.",
        "err_pad": "Неправильний номер контакту.",
        "err_folder": "Каталог збереження не існує.",
        "confirm": "Підтвердження",
        "overwrite": "Файл уже існує:\n{path}\n\nПерезаписати його?",
        "done": "Готово",
        "saved": "Збережено: {path}",
        "saved_message": "Футпринт створено:\n{path}\n\nДодайте .kicad_mod у власну бібліотеку .pretty.",
        "error": "Помилка",
        "settings_error": "Не вдалося зберегти налаштування поряд із програмою:\n{reason}",
        "settings_warning": "Налаштування",
    },
    "en": {
        'preview_3d': '3D Preview',
        'models_3d': '3D Model(s) — STEP / STP only',
        'add_3d': 'Add model…',
        'remove_3d': 'Remove',
        'show_model': 'Show',
        'embed_3d': 'Embed STEP in footprint file',
        'opacity_3d': 'Opacity',
        'scale_3d': 'Scale',
        'rotation_3d': 'Rotation',
        'offset_3d': 'Offset (mm)',
        'model_missing': 'Select a STEP or STP model first.',
        'preview_requires': '3D preview requires cadquery-ocp and vtk. Install:\npython -m pip install cadquery-ocp vtk',
        'embedding_requires': 'Embedding a STEP file requires zstandard or a system libzstd. Install:\npython -m pip install zstandard',
        'failed_to_load_step': 'Could not load STEP model:\n{error}',
        'failed_3d': '3D preview error: {error}',
        'view_top': 'Top',
        'view_iso': 'Isometric',
        'view_side': 'Side',
        'view_bottom': 'Bottom',
        'fit_3d': 'Fit',
        'show_board': 'Show PCB',
        'status_no_model': 'No model selected',
        'auto_courtyard': 'Generate F.CrtYd automatically',
        'paste_segmented': 'Segment F.Paste apertures',
        'paste_length': 'Max aperture length',
        'paste_gap': 'Gap between apertures',
        'paste_inset': 'Paste inset from copper edges',
        'err_paste_params': 'Invalid aperture parameters: length > 0, gap ≥ 0, inset ≥ 0 and less than half the rim.',
        'err_paste_span': 'Not enough straight copper for segmented paste. Reduce inset/gap or adjust radii.',
        "window_title": "KiCad Hollow SMD Pad Generator",
        "title": "KiCad Hollow SMD Pad Generator",
        "language": "Interface language",
        "dimension_mode": "Dimension reference",
        "centerline": "Centerlines of copper strips",
        "outer": "Outside copper dimensions",
        "horizontal": "Horizontal dimension",
        "vertical": "Vertical dimension",
        "outer_radius": "Outer corner radius",
        "inner_radius": "Inner corner radius",
        "rim": "Copper rim width",
        "courtyard": "F.CrtYd clearance",
        "pad_number": "Pad number",
        "mm": "mm",
        "mask": "F.Mask (exposed copper)",
        "paste": "F.Paste (solder paste)",
        "fab_shield": "F.Fab shield outlines",
        "shield_thickness": "Wall",
        "err_shield_thickness": "Shield wall thickness must be positive and smaller than half the shield's smallest dimension.",
        "err_shield_radius": "Equal corner radii on both F.Fab contours require a smaller outer radius or wall thickness.",
        "fab_enabled_legend": "Solid cyan and green: F.Fab outlines with equal corner radii.",
        "fab_disabled_legend": "Dashed cyan: centerline of the copper rim.",
        "paste_note": "For reflow soldering of shields, split paste openings may be preferable.",
        "filename": "File name",
        "folder": "Save folder",
        "save": "Save footprint (.kicad_mod)",
        "preview": "Live preview (scaled geometry)",
        "legend": "Red: F.Cu; dark: no copper; purple: Courtyard.",
        "outside": "Outer dimensions",
        "centerline_label": "Strip centerlines",
        "rim_short": "Rim",
        "outer_r_short": "Outer R",
        "inner_r_short": "Inner R",
        "inside": "Opening",
        "one_pad": "The file contains ONE electrical pad built from four adjacent copper polygons.",
        "invalid_geometry": "Invalid geometry",
        "check_geometry": "Check sizes and radii",
        "invalid_number": "Invalid number",
        "err_nonpositive": "Dimensions and rim width must be positive.",
        "err_negative_courtyard": "Courtyard clearance cannot be negative.",
        "err_negative_radius": "Corner radii cannot be negative.",
        "err_outer_radius": "Outer radius exceeds half the smaller outer dimension.",
        "err_inner_radius": "Inner radius exceeds half the smaller opening dimension.",
        "err_no_hole": "The copper rim is too wide: there is no opening.",
        "err_mode": "Unknown measurement mode.",
        "err_filename": "Please enter a valid file name (no forbidden characters).",
        "err_pad": "Invalid pad number.",
        "err_folder": "Save folder does not exist.",
        "confirm": "Confirmation",
        "overwrite": "The file already exists:\n{path}\n\nOverwrite?",
        "done": "Done",
        "saved": "Saved: {path}",
        "saved_message": "Footprint created:\n{path}\n\nPlace the .kicad_mod file in your .pretty library.",
        "error": "Error",
        "settings_error": "Could not save settings next to the program:\n{reason}",
        "settings_warning": "Settings",
    },
    "de": {
        'preview_3d': '3D-Vorschau',
        'models_3d': '3D-Modelle – nur STEP / STP',
        'add_3d': 'Modell hinzufügen…',
        'remove_3d': 'Entfernen',
        'show_model': 'Anzeigen',
        'embed_3d': 'STEP in Footprint einbetten',
        'opacity_3d': 'Deckkraft',
        'scale_3d': 'Skalierung',
        'rotation_3d': 'Drehung',
        'offset_3d': 'Versatz (mm)',
        'model_missing': 'Bitte zuerst eine STEP- oder STP-Datei auswählen.',
        'preview_requires': 'Für die 3D-Vorschau werden cadquery-ocp und vtk benötigt. Installieren:\npython -m pip install cadquery-ocp vtk',
        'embedding_requires': 'Zum Einbetten wird zstandard oder eine Systembibliothek libzstd benötigt. Installieren:\npython -m pip install zstandard',
        'failed_to_load_step': 'STEP-Datei kann nicht geladen werden:\n{error}',
        'failed_3d': 'Fehler in der 3D-Vorschau: {error}',
        'view_top': 'Oben',
        'view_iso': 'Isometrisch',
        'view_side': 'Seite',
        'view_bottom': 'Unten',
        'fit_3d': 'Anpassen',
        'show_board': 'Platine anzeigen',
        'status_no_model': 'Kein Modell ausgewählt',
        'auto_courtyard': 'F.CrtYd automatisch erzeugen',
        'paste_segmented': 'F.Paste-Ausschnitte segmentieren',
        'paste_length': 'Max. Schablonenlänge',
        'paste_gap': 'Abstand zwischen Ausschnitten',
        'paste_inset': 'Pastenabstand zum Kupferrand',
        'err_paste_params': 'Ungültige Werte: Länge > 0, Abstand ≥ 0 und Randabstand ≥ 0 und kleiner als halbe Randbreite.',
        'err_paste_span': 'Zu wenig gerade Kupferfläche. Randabstand/Lücke verringern oder Radien ändern.',
        "window_title": "KiCad Hollow SMD Pad Generator",
        "title": "KiCad Hollow SMD Pad Generator",
        "language": "Sprache",
        "dimension_mode": "Bezugsmaß",
        "centerline": "Mittellinien der Kupferstreifen",
        "outer": "Äußere Kupferabmessungen",
        "horizontal": "Horizontales Maß",
        "vertical": "Vertikales Maß",
        "outer_radius": "Äußerer Eckenradius",
        "inner_radius": "Innerer Eckenradius",
        "rim": "Breite des Kupferrands",
        "courtyard": "F.CrtYd-Abstand",
        "pad_number": "Pad-Nummer",
        "mm": "mm",
        "mask": "F.Mask (freiliegendes Kupfer)",
        "paste": "F.Paste (Lotpaste)",
        "fab_shield": "F.Fab-Schirmkonturen",
        "shield_thickness": "Wandstärke",
        "err_shield_thickness": "Die Wandstärke muss positiv und kleiner als die halbe kürzere Schirmabmessung sein.",
        "err_shield_radius": "Für gleiche Radien beider F.Fab-Konturen muss der Außenradius oder die Wandstärke kleiner sein.",
        "fab_enabled_legend": "Türkis und Grün: zwei F.Fab-Konturen mit gleichem Eckenradius.",
        "fab_disabled_legend": "Türkis gestrichelt: Mittellinie des Kupferrands.",
        "paste_note": "Für Reflow-Lötung von Schirmgehäusen ist eine segmentierte Pastenschablone oft besser.",
        "filename": "Dateiname",
        "folder": "Speicherordner",
        "save": "Footprint speichern (.kicad_mod)",
        "preview": "Vorschau (maßstäbliche Geometrie)",
        "legend": "Rot: F.Cu; dunkel: kupferfrei; violett: Courtyard.",
        "outside": "Außenmaße",
        "centerline_label": "Randmittellinien",
        "rim_short": "Rand",
        "outer_r_short": "R außen",
        "inner_r_short": "R innen",
        "inside": "Öffnung",
        "one_pad": "Die Datei enthält EIN elektrisches Pad aus vier angrenzenden Kupferpolygonen.",
        "invalid_geometry": "Ungültige Geometrie",
        "check_geometry": "Maße und Radien prüfen",
        "invalid_number": "Ungültige Zahl",
        "err_nonpositive": "Abmessungen und Randbreite müssen größer als null sein.",
        "err_negative_courtyard": "Courtyard-Abstand darf nicht negativ sein.",
        "err_negative_radius": "Eckenradien dürfen nicht negativ sein.",
        "err_outer_radius": "Außenradius ist größer als die Hälfte des kleineren Außenmaßes.",
        "err_inner_radius": "Innenradius ist größer als die Hälfte des kleineren Öffnungsmaßes.",
        "err_no_hole": "Kupferrand ist zu breit: es bleibt keine Öffnung.",
        "err_mode": "Unbekannter Bemaßungsmodus.",
        "err_filename": "Bitte einen gültigen Dateinamen ohne unzulässige Zeichen eingeben.",
        "err_pad": "Ungültige Pad-Nummer.",
        "err_folder": "Speicherordner existiert nicht.",
        "confirm": "Bestätigung",
        "overwrite": "Datei ist bereits vorhanden:\n{path}\n\nÜberschreiben?",
        "done": "Fertig",
        "saved": "Gespeichert: {path}",
        "saved_message": "Footprint erstellt:\n{path}\n\nDie .kicad_mod-Datei in eine .pretty-Bibliothek legen.",
        "error": "Fehler",
        "settings_error": "Einstellungen konnten nicht im Programmordner gespeichert werden:\n{reason}",
        "settings_warning": "Einstellungen",
    },
}
LANGUAGES = {"Українська": "uk", "English": "en", "Deutsch": "de"}
LANGUAGE_NAMES = {v: k for k, v in LANGUAGES.items()}


def tr(language: str, key: str, **kwargs) -> str:
    return I18N.get(language, I18N["en"]).get(key, key).format(**kwargs)


class GeometryError(ValueError):
    """Message is an i18n key, not an end-user sentence."""


def as_float(value) -> float:
    """Accept 1.25 and 1,25; reject non-finite values."""
    try:
        result = float(str(value).strip().replace(" ", "").replace(",", "."))
    except (ValueError, TypeError) as exc:
        raise GeometryError("invalid_number") from exc
    if not math.isfinite(result):
        raise GeometryError("invalid_number")
    return result


class RingGeometry:
    """Hollow round-corner rectangle in millimeters.

    centerline mode: W/H between the centers of OPPOSITE straight strips.
    outer mode: W/H are the overall copper dimensions.

    Corner radii are independent: the inner radius is NOT automatically
    outer_radius - rim_width. Thus corner copper width may vary if the radii
    are not offset-compatible; the straight sections stay exactly rim wide.
    """

    def __init__(self, horizontal=19.0, vertical=10.2, radius=1.15,
                 rim=1.5, mode="centerline", courtyard=0.25, inner_radius=0.0):
        numbers = (horizontal, vertical, radius, rim, courtyard, inner_radius)
        if any(not math.isfinite(v) for v in numbers):
            raise GeometryError("invalid_number")
        if horizontal <= 0 or vertical <= 0 or rim <= 0:
            raise GeometryError("err_nonpositive")
        if radius < 0 or inner_radius < 0:
            raise GeometryError("err_negative_radius")
        if courtyard < 0:
            raise GeometryError("err_negative_courtyard")

        if mode == "centerline":
            self.centerline_w, self.centerline_h = horizontal, vertical
            self.ow, self.oh = horizontal + rim, vertical + rim
        elif mode == "outer":
            self.ow, self.oh = horizontal, vertical
            self.centerline_w = horizontal - rim
            self.centerline_h = vertical - rim
        else:
            raise GeometryError("err_mode")

        self.iw, self.ih = self.ow - 2 * rim, self.oh - 2 * rim
        if min(self.iw, self.ih) <= 0:
            raise GeometryError("err_no_hole")
        if radius > min(self.ow, self.oh) / 2 + 1e-9:
            raise GeometryError("err_outer_radius")
        if inner_radius > min(self.iw, self.ih) / 2 + 1e-9:
            raise GeometryError("err_inner_radius")

        self.radius = radius
        self.ir = inner_radius
        self.rim = rim
        self.mode = mode
        self.courtyard = courtyard
        self.cx, self.cy = self.ow / 2 - radius, self.oh / 2 - radius
        self.icx, self.icy = self.iw / 2 - inner_radius, self.ih / 2 - inner_radius
        self.corners = {
            "TL": (-self.cx, -self.cy), "TR": (self.cx, -self.cy),
            "BR": (self.cx, self.cy), "BL": (-self.cx, self.cy),
        }
        self.inner_corners = {
            "TL": (-self.icx, -self.icy), "TR": (self.icx, -self.icy),
            "BR": (self.icx, self.icy), "BL": (-self.icx, self.icy),
        }

    def arc(self, corner: str, a0: float, a1: float, inner=False):
        r = self.ir if inner else self.radius
        cx, cy = self.inner_corners[corner] if inner else self.corners[corner]
        if r <= 1e-12:
            return [(cx, cy)]
        count = max(1, math.ceil(abs(a1 - a0) / ANGLE_STEP))
        return [(cx + r * math.cos(math.radians(a0 + (a1-a0)*i/count)),
                 cy + r * math.sin(math.radians(a0 + (a1-a0)*i/count)))
                for i in range(count + 1)]

    @staticmethod
    def _dedupe(points):
        result = []
        for p in points:
            if not result or math.dist(result[-1], p) > 1e-9:
                result.append(p)
        if len(result) > 1 and math.dist(result[0], result[-1]) < 1e-9:
            result.pop()
        return result

    def contour(self, inner=False):
        points = []
        for corner, a0, a1 in (("TL", 180, 270), ("TR", 270, 360),
                               ("BR", 0, 90), ("BL", 90, 180)):
            points.extend(self.arc(corner, a0, a1, inner=inner))
        return self._dedupe(points)

    def centerline_contour(self):
        """Guide line only; straight parts reflect exactly centerline W/H."""
        r = max(0.0, self.radius - self.rim / 2)
        cw, ch = self.centerline_w, self.centerline_h
        cx, cy = cw / 2 - r, ch / 2 - r
        if cx < 0 or cy < 0:
            r = max(0.0, min(cw, ch) / 2)
            cx, cy = cw / 2-r, ch / 2-r
        pts = []
        for x, y, start, finish in ((-cx, -cy, 180, 270), (cx, -cy, 270, 360),
                                     (cx, cy, 0, 90), (-cx, cy, 90, 180)):
            count = max(1, math.ceil((finish-start)/ANGLE_STEP))
            for i in range(count+1):
                a = math.radians(start+(finish-start)*i/count)
                pts.append((x+r*math.cos(a), y+r*math.sin(a)))
        return self._dedupe(pts)

    def shield_geometry(self, wall_thickness=0.3):
        """Two F.Fab outlines using EXACTLY THE SAME corner radius.

        Outer F.Fab is on the copper strip centerline. Inner F.Fab is
        smaller by 2*t in width and height, but has the SAME radius as
        the outer F.Fab (not r-t). Consequently wall thickness is t along
        straight edges but varies in corner areas, as explicitly requested.
        """
        t = as_float(wall_thickness)
        w, h = self.centerline_w, self.centerline_h
        if t <= 0 or 2*t >= min(w, h):
            raise GeometryError("err_shield_thickness")
        r = max(0.0, min(max(0.0, self.radius - self.rim/2), min(w, h)/2))
        inner_w, inner_h = w - 2*t, h - 2*t
        # Do not silently clamp the inner radius, which would produce
        # unequal rounds despite the user's requested equal-radius design.
        if r > min(inner_w, inner_h)/2 + 1e-9:
            raise GeometryError("err_shield_radius")
        return (w, h, r), (inner_w, inner_h, r)

    @staticmethod
    def rounded_contour(w, h, radius):
        r = min(max(0.0, radius), w/2, h/2)
        pts = []
        for cx, cy, a0, a1 in (
                (-w/2+r, -h/2+r, 180, 270),
                ( w/2-r, -h/2+r, 270, 360),
                ( w/2-r,  h/2-r, 0, 90),
                (-w/2+r,  h/2-r, 90, 180)):
            if r < 1e-12:
                pts.append((cx, cy))
            else:
                n = max(1, math.ceil((a1-a0)/ANGLE_STEP))
                for k in range(n+1):
                    a = math.radians(a0+(a1-a0)*k/n)
                    pts.append((cx+r*math.cos(a), cy+r*math.sin(a)))
        return RingGeometry._dedupe(pts)

    def primitives(self):
        """Four touching polygons, union is an annulus, no filled center."""
        specs = [
            (("TL",225,270), ("TR",270,315), ("TR",315,270), ("TL",270,225)),
            (("TR",315,360), ("BR",0,45), ("BR",45,0), ("TR",360,315)),
            (("BR",45,90), ("BL",90,135), ("BL",135,90), ("BR",90,45)),
            (("BL",135,180), ("TL",180,225), ("TL",225,180), ("BL",180,135)),
        ]
        result = []
        for oa, ob, ib, ia in specs:
            p = self._dedupe(self.arc(*oa) + self.arc(*ob) +
                             self.arc(*ib, inner=True) + self.arc(*ia, inner=True))
            if len(p) < 3:
                raise GeometryError("invalid_geometry")
            result.append(p)
        return result



def segmented_paste_rectangles(g: RingGeometry, max_length=2.5, gap=0.35, inset=0.15):
    """Return F.Paste-only rectangular openings inside the straight copper strips.

    Corners are intentionally left paste-free (stencil bridges / lower solder
    volume). Each rectangle is entirely inside copper, no electrical pad number.
    """
    max_length, gap, inset = map(as_float, (max_length, gap, inset))
    if max_length <= 0 or gap < 0 or inset < 0 or 2 * inset >= g.rim:
        raise GeometryError("err_paste_params")
    # Both the inner and outer boundaries must be straight along each rectangle.
    xhalf = min(g.ow/2 - g.radius, g.iw/2 - g.ir) - inset
    yhalf = min(g.oh/2 - g.radius, g.ih/2 - g.ir) - inset
    if xhalf <= 0 or yhalf <= 0:
        raise GeometryError("err_paste_span")
    span_w = g.rim - 2 * inset
    result = []
    def pieces(total):
        n = max(1, math.ceil((total + gap) / (max_length + gap)))
        if n > 1000 or total - (n-1)*gap <= 1e-6:
            raise GeometryError("err_paste_span")
        size = (total - (n-1)*gap) / n
        return [(-total/2 + i*(size+gap) + size/2, size) for i in range(n)]
    # upper and lower bars
    for cy in (-g.centerline_h/2, g.centerline_h/2):
        for cx, ww in pieces(2*xhalf):
            result.append((cx,cy,ww,span_w))
    # left and right bars
    for cx in (-g.centerline_w/2, g.centerline_w/2):
        for cy, hh in pieces(2*yhalf):
            result.append((cx,cy,span_w,hh))
    return result


def kicad_name(filename: str) -> str:
    raw = Path(filename).name
    if raw.lower().endswith(".kicad_mod"):
        raw = raw[:-10]
    if not raw or raw in (".", ".."):
        raise ValueError("err_filename")
    if re.search(r'[<>:"/\\|?*\x00-\x1F]', raw) or raw.endswith((".", " ")):
        raise ValueError("err_filename")
    if raw.upper().split(".")[0] in ("CON", "PRN", "AUX", "NUL") or re.fullmatch(
            r"(?:COM|LPT)[1-9]", raw.upper().split(".")[0]):
        raise ValueError("err_filename")
    return raw


def qtext(s: str) -> str:
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


def fab_rounded_rect(w: float, h: float, r: float) -> list[str]:
    """Return 4 straight segments and 4 true quarter-circle arcs (or square)."""
    f = lambda n: f"{n:.6f}"
    result = []
    stroke = '(stroke (width 0.10) (type solid)) (layer "F.Fab")'
    def line(a, b):
        if math.dist(a,b) > 1e-9:
            result.append(
                f'  (fp_line (start {f(a[0])} {f(a[1])}) '
                f'(end {f(b[0])} {f(b[1])}) {stroke})'
            )
    def arc(cx, cy, start, mid, end):
        def point(deg):
            angle=math.radians(deg)
            return cx+r*math.cos(angle), cy+r*math.sin(angle)
        a, m, b = point(start),point(mid),point(end)
        result.append(
            f'  (fp_arc (start {f(a[0])} {f(a[1])}) '
            f'(mid {f(m[0])} {f(m[1])}) '
            f'(end {f(b[0])} {f(b[1])}) {stroke})'
        )
    if r < 1e-9:
        corners = [(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)]
        for a,b in zip(corners, corners[1:]+corners[:1]):
            line(a,b)
        return result
    # Clockwise closed loop; tangent joins are exactly coincident.
    line((-w/2+r, -h/2), (w/2-r, -h/2))
    arc(w/2-r, -h/2+r, 270,315,360)
    line((w/2, -h/2+r), (w/2, h/2-r))
    arc(w/2-r, h/2-r, 0,45,90)
    line((w/2-r, h/2),(-w/2+r, h/2))
    arc(-w/2+r, h/2-r, 90,135,180)
    line((-w/2, h/2-r),(-w/2,-h/2+r))
    arc(-w/2+r,-h/2+r,180,225,270)
    return result


def make_footprint(g: RingGeometry, filename: str, pad_number="1", paste=True, mask=True,
                   fab_shield=False, shield_thickness=0.3, generate_courtyard=True,
                   paste_segmented=False, paste_length=2.5, paste_gap=0.35,
                   paste_inset=0.15, model_file=None, model_transform=None, embed_model=True):
    name = kicad_name(filename)
    number = pad_number.strip()
    if not number or len(number) > 32 or re.search(r'["\\\n\r]', number):
        raise ValueError("err_pad")
    # Anchor must be physically on a copper strip, not in the center void.
    origin_x = 0.0
    origin_y = -g.oh/2 + g.rim/2
    anchor = min(0.2, g.rim*0.4)
    layers = ['"F.Cu"']
    if paste and not paste_segmented:
        layers.append('"F.Paste"')
    if mask:
        layers.append('"F.Mask"')
    descr = (f"Hollow single pad; centerlines {g.centerline_w:.3f}x{g.centerline_h:.3f} mm; "
             f"outer {g.ow:.3f}x{g.oh:.3f} mm; R_outer {g.radius:.3f} mm; "
             f"R_inner {g.ir:.3f} mm; rim {g.rim:.3f} mm")
    f = lambda x: f"{x:.6f}"
    lines = [
        f'(footprint {qtext(name)}',
        '  (version 20240706)',
        '  (generator "KiCad_Hollow_SMD_Pad_Generator")',
        '  (layer "F.Cu")',
        f'  (descr {qtext(descr)})',
        '  (tags "EMI shield hollow rounded copper ring custom SMD pad")',
        '  (attr smd)',
        f'  (property "Reference" "REF**" (at 0 {f(-g.oh/2-1.5)}) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))',
        f'  (property "Value" {qtext(name)} (at 0 {f(g.oh/2+1.5)}) (layer "F.Fab") (effects (font (size 0.8 0.8) (thickness 0.12))))',
    ]
    if generate_courtyard:
        # Snap outward to 0.05 mm and include the 0.05 mm stroke outside edge.
        outward = lambda v: math.ceil((v+0.0000001)/0.05)*0.05
        x = outward(g.ow/2 + g.courtyard + 0.025)
        y = outward(g.oh/2 + g.courtyard + 0.025)
        rect = [(-x, -y), (x, -y), (x, y), (-x, y)]
        for a, b in zip(rect, rect[1:] + rect[:1]):
            lines.append(f'  (fp_line (start {f(a[0])} {f(a[1])}) (end {f(b[0])} {f(b[1])}) '
                         '(stroke (width 0.05) (type default)) (layer "F.CrtYd"))')
    if fab_shield:
        outer_shield, inner_shield = g.shield_geometry(shield_thickness)
        lines.extend(fab_rounded_rect(*outer_shield))
        lines.extend(fab_rounded_rect(*inner_shield))
    lines.extend([
        f'  (pad {qtext(number)} smd custom',
        f'    (at {f(origin_x)} {f(origin_y)})',
        f'    (size {f(anchor)} {f(anchor)})',
        f'    (layers {" ".join(layers)})',
        '    (options (clearance outline) (anchor rect))',
        '    (primitives',
    ])
    for primitive in g.primitives():
        points = ' '.join(f'(xy {f(px-origin_x)} {f(py-origin_y)})' for px, py in primitive)
        lines.append(f'      (gr_poly (pts {points}) (width 0) (fill yes))')
    lines.extend(['    )', '  )'])
    paste_rects = []
    if paste and paste_segmented:
        paste_rects = segmented_paste_rectangles(g, paste_length, paste_gap, paste_inset)
        for px,py,pw,ph in paste_rects:
            lines.append(f'  (pad "" smd rect (at {f(px)} {f(py)}) '
                         f'(size {f(pw)} {f(ph)}) (layers "F.Paste"))')
    if model_file:
        lines.append(embed_model_block(model_file, model_transform or {}, embed_model).rstrip())
    lines.append(')')
    result = '\n'.join(lines) + '\n'
    return result



def _zstd_compress(payload: bytes) -> bytes:
    """Use python-zstandard if installed, or libzstd via ctypes (where available)."""
    try:
        import zstandard
        return zstandard.ZstdCompressor(level=15).compress(payload)
    except ImportError:
        pass
    candidates = [ctypes.util.find_library('zstd'), 'libzstd.so.1', 'libzstd.dll', 'zstd.dll']
    if sys.platform == 'win32':
        for base in (Path(os.environ.get('ProgramFiles','C:/Program Files')) / 'KiCad',
                     Path(os.environ.get('ProgramFiles','C:/Program Files')) / 'KiCad' / '10.0'):
            for dll in ('bin/libzstd.dll', 'bin/zstd.dll', '10.0/bin/libzstd.dll',
                        '10.0/bin/zstd.dll', '9.0/bin/libzstd.dll'):
                candidates.append(str(base / dll))
    lib = None
    for candidate in candidates:
        if not candidate:
            continue
        try:
            lib = ctypes.CDLL(str(candidate))
            break
        except OSError:
            pass
    if lib is None:
        raise RuntimeError('embedding_requires')
    lib.ZSTD_compressBound.argtypes = [ctypes.c_size_t]
    lib.ZSTD_compressBound.restype = ctypes.c_size_t
    lib.ZSTD_compress.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p,
                                   ctypes.c_size_t, ctypes.c_int]
    lib.ZSTD_compress.restype = ctypes.c_size_t
    lib.ZSTD_isError.argtypes = [ctypes.c_size_t]
    lib.ZSTD_isError.restype = ctypes.c_uint
    src=ctypes.create_string_buffer(payload)
    bound=lib.ZSTD_compressBound(len(payload))
    dest=ctypes.create_string_buffer(bound)
    length=lib.ZSTD_compress(dest, bound, src, len(payload), 15)
    if lib.ZSTD_isError(length):
        raise RuntimeError('ZSTD compression failed')
    return dest.raw[:length]


def embed_model_block(model_file: str, transforms: dict, embed=True) -> str:
    """KiCad >=9 embedded model format: zstd + Base64, SHA256 legacy checksum.

    SHA256 is explicitly supported by the KiCad embedded-file parser, alongside
    newer Murmur3 checksums. The encoded data is wrapped in vertical bars.
    """
    source=Path(model_file).expanduser().resolve()
    if not source.is_file() or source.suffix.lower() not in ('.step', '.stp'):
        raise ValueError('model_missing')
    coords = [as_float(transforms.get(key, 0 if key[0]!='s' else 1))
              for key in ('sx','sy','sz','rx','ry','rz','ox','oy','oz')]
    if any(v<=0 for v in coords[:3]):
        raise ValueError('3D model scale must be positive')
    sx,sy,sz,rx,ry,rz,ox,oy,oz=coords
    link = f'kicad-embed://{source.name}' if embed else source.as_posix()
    f=lambda n: f'{0.0 if abs(n) < 0.0000005 else n:.6f}'
    # KiCad stores 3D rotation as clockwise-positive in .kicad_mod, while
    # KiCad 10's 3D Model GUI shows counterclockwise-positive angles.
    # Our GUI and VTK preview use the GUI convention, so negate on export.
    model_text = (f'  (model {qtext(link)}\n'
                  f'    (offset (xyz {f(ox)} {f(oy)} {f(oz)}))\n'
                  f'    (scale (xyz {f(sx)} {f(sy)} {f(sz)}))\n'
                  f'    (rotate (xyz {f(-rx)} {f(-ry)} {f(-rz)}))\n'
                  f'  )\n')
    if not embed:
        return model_text
    raw=source.read_bytes()
    if not raw:
        raise ValueError('STEP file is empty')
    zipped = _zstd_compress(raw)
    encoded = base64.b64encode(zipped).decode('ascii')
    # KiCad accepts SHA-256 checksums (64 characters) as the legacy format.
    checksum=hashlib.sha256(raw).hexdigest()
    wrapped='\n'.join('      '+encoded[n:n+76] for n in range(0,len(encoded),76))
    embedded=(f'  (embedded_files\n    (file (name {qtext(source.name)}) (type model)\n'
              f'      (data |\n{wrapped}\n      |)\n'
              f'      (checksum {qtext(checksum)}))\n  )\n')
    return model_text+embedded


def app_directory() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def settings_path() -> Path:
    return app_directory() / SETTINGS_FILENAME


def load_settings():
    # Read v2.3 settings if the renamed v2.4 settings file is absent.
    primary = settings_path()
    previous = app_directory() / 'KiCad_Hollow_SMD_Generator.settings.json'
    for path in (primary, previous):
        try:
            obj = json.loads(path.read_text(encoding='utf-8'))
            if isinstance(obj, dict):
                return obj
        except (OSError, ValueError, UnicodeError):
            continue
    return {}


def save_settings(values):
    """Atomic replacement; remains in the PROGRAM DIRECTORY as requested."""
    dst = settings_path()
    temp = dst.with_name(dst.name + ".tmp")
    payload = json.dumps({"version": 4, **values}, ensure_ascii=False, indent=2)
    try:
        temp.write_text(payload + "\n", encoding="utf-8")
        os.replace(temp, dst)
    finally:
        try:
            temp.unlink(missing_ok=True)
        except OSError:
            pass


def desktop_work_area(root):
    """Desktop's usable rectangle in Tk coordinates (taskbar excluded on Windows)."""
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    if sys.platform == "win32":
        try:
            class RECT(ctypes.Structure):
                _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long),
                           ("right", ctypes.c_long), ("bottom", ctypes.c_long)]
            rect = RECT()
            user32 = ctypes.windll.user32
            # SPI_GETWORKAREA: primary monitor area excluding the taskbar.
            if user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(rect), 0):
                physical_w = user32.GetSystemMetrics(0)
                physical_h = user32.GetSystemMetrics(1)
                sx = sw / physical_w if physical_w else 1.0
                sy = sh / physical_h if physical_h else 1.0
                x = round(rect.left * sx)
                y = round(rect.top * sy)
                w = round((rect.right - rect.left) * sx)
                h = round((rect.bottom - rect.top) * sy)
                if w > 0 and h > 0:
                    return x, y, w, h
        except (OSError, AttributeError, ValueError):
            pass
    return 0, 0, sw, sh


class StepPreviewWindow:
    """Tk + VTK 3D scene backed by an actual OpenCascade STEP solid.

    Only this optional window imports VTK/OCP. The footprint generator itself
    stays usable with standard Python/Tkinter installed.
    """

    def __init__(self, parent, geometry):
        import tkinter as tk
        from tkinter import ttk, filedialog, messagebox
        try:
            import vtk
            from OCP.STEPControl import STEPControl_Reader
        except ImportError as ex:
            raise ImportError('preview_requires') from ex

        self.parent, self.g = parent, geometry
        self.tk, self.ttk = tk, ttk
        self.filedialog, self.messagebox = filedialog, messagebox
        self.vtk = vtk
        self.STEPControl_Reader = STEPControl_Reader
        self.window = tk.Toplevel(parent)
        self.window.withdraw()
        self.window.title(parent.t('preview_3d')+' — '+parent.t('title'))
        self.window.minsize(720, 440)
        self.window.protocol('WM_DELETE_WINDOW', self.close)
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(1, weight=1)
        top = ttk.LabelFrame(self.window, text=parent.t('models_3d'), padding=5)
        top.grid(row=0, column=0, sticky='ew', padx=9, pady=(6,4))
        top.columnconfigure(0,weight=1)
        ttk.Entry(top, textvariable=parent.vars['model_file'], state='readonly').grid(
            row=0,column=0,sticky='ew',padx=(0,8),ipady=3)
        self.visible=tk.BooleanVar(value=True)
        ttk.Checkbutton(top,text=parent.t('show_model'),
                        variable=self.visible).grid(row=0,column=1,padx=5)
        ttk.Button(top,text=parent.t('add_3d'),command=self.select_model).grid(
            row=0,column=2,padx=(0,5))
        ttk.Button(top,text=parent.t('remove_3d'),command=self.remove_model).grid(
            row=0,column=3,padx=(0,2))
        content=ttk.Frame(self.window)
        content.grid(row=1,column=0,sticky='nsew',padx=9,pady=(0,7))
        content.columnconfigure(1, weight=1)
        content.rowconfigure(0, weight=1)
        left_canvas=tk.Canvas(content,highlightthickness=0,width=218)
        left_scroll=ttk.Scrollbar(content,orient='vertical',command=left_canvas.yview)
        left_canvas.configure(yscrollcommand=left_scroll.set)
        left_canvas.grid(row=0,column=0,sticky='ns')
        left_scroll.grid(row=0,column=0,sticky='nse',padx=(218,0))
        controls=ttk.Frame(left_canvas,padding=(2,2,9,4))
        content_window=left_canvas.create_window((0,0),window=controls,anchor='nw')
        controls.bind('<Configure>',lambda _: left_canvas.configure(scrollregion=left_canvas.bbox('all')))
        left_canvas.bind('<Configure>',lambda ev:left_canvas.itemconfigure(content_window,width=max(210,ev.width)))

        for title,keys in ((parent.t('scale_3d'),('sx','sy','sz')),
                           (parent.t('rotation_3d'),('rx','ry','rz')),
                           (parent.t('offset_3d'),('ox','oy','oz'))):
            group=ttk.LabelFrame(controls,text=title,padding=(7,6))
            group.pack(fill='x',pady=(0,8))
            group.columnconfigure(1,weight=1)
            for index,key in enumerate(keys):
                ttk.Label(group,text=('X','Y','Z')[index]+':').grid(row=index,column=0,sticky='w',pady=3)
                spin=ttk.Spinbox(group,textvariable=parent.vars['model_'+key],
                                 width=10,from_=-360 if key.startswith('r') else -10000,
                                 to=360 if key.startswith('r') else 10000,
                                 increment=90 if key.startswith('r') else 0.25)
                spin.grid(row=index,column=1,sticky='ew',padx=(4,0),pady=3)
        opacity=ttk.LabelFrame(controls,text=parent.t('opacity_3d'),padding=7)
        opacity.pack(fill='x',pady=(0,7))
        ttk.Scale(opacity,from_=0,to=100,orient='horizontal',
                  command=self.update_opacity, variable=parent.vars['model_opacity']).pack(fill='x')
        self.board_visible=tk.BooleanVar(value=True)
        ttk.Checkbutton(controls,text=parent.t('show_board'),variable=self.board_visible,
                        command=self.update_model_visibility).pack(anchor='w',pady=4)
        ttk.Checkbutton(controls,text=parent.t('embed_3d'),
                        variable=parent.vars['embed_model']).pack(anchor='w',pady=(6,8))
        ttk.Label(controls,text='.step / .stp',foreground='#677386').pack(anchor='w')
        right=ttk.LabelFrame(content,text=parent.t('preview'),padding=4)
        right.grid(row=0,column=1,sticky='nsew',padx=(10,0))
        right.columnconfigure(0,weight=1)
        right.rowconfigure(0,weight=1)
        self.view_canvas = tk.Canvas(right, bg="#666b86", highlightthickness=0,
                                     width=720, height=550)
        self.view_canvas.grid(row=0,column=0,sticky='nsew')
        self.view_canvas.bind('<Configure>',self._queue_render)
        self.view_canvas.bind('<ButtonPress-1>',self._start_drag)
        self.view_canvas.bind('<B1-Motion>',self._drag_rotate)
        self.view_canvas.bind('<ButtonPress-3>',self._start_drag)
        self.view_canvas.bind('<B3-Motion>',self._drag_pan)
        self.view_canvas.bind('<MouseWheel>',self._wheel_zoom)
        self.view_canvas.bind('<Button-4>',lambda ev:self._zoom(1.12))
        self.view_canvas.bind('<Button-5>',lambda ev:self._zoom(1/1.12))
        self._photo=None
        self._image_item=None
        self._render_queued=False
        self._drag_start=None
        cam_controls=ttk.Frame(right)
        cam_controls.grid(row=0,column=1,sticky='ns',padx=(5,0))
        for text_key,direction in [('view_iso','iso'),('view_top','top'),
                                    ('view_side','side'),('view_bottom','bottom')]:
            ttk.Button(cam_controls,text=parent.t(text_key),width=11,
                       command=lambda d=direction:self.set_camera(d)).pack(fill='x',pady=3)
        ttk.Button(cam_controls,text=parent.t('fit_3d'),width=11,
                   command=self.fit_camera).pack(fill='x',pady=(14,0))

        self.renderer=vtk.vtkRenderer()
        self.renderer.SetBackground(0.41, 0.42, 0.54)
        self.renderer.SetBackground2(0.72,0.73,0.83)
        self.renderer.GradientBackgroundOn()
        self.render_window=vtk.vtkRenderWindow()
        self.render_window.SetOffScreenRendering(1)
        self.render_window.SetMultiSamples(0)
        self.render_window.AddRenderer(self.renderer)
        self.render_window.SetSize(720,550)
        self._image_filter=vtk.vtkWindowToImageFilter()
        self._image_filter.SetInput(self.render_window)
        self._image_filter.SetInputBufferTypeToRGB()
        self._image_filter.ReadFrontBufferOff()
        self._writer=vtk.vtkPNGWriter()
        self._writer.SetWriteToMemory(True)
        self._writer.SetInputConnection(self._image_filter.GetOutputPort())
        self.model_actor=None
        self.board_actor=None
        self.copper_actor=None
        self._make_pcb()
        for key in ('sx','sy','sz','rx','ry','rz','ox','oy','oz'):
            parent.vars['model_'+key].trace_add('write', lambda *_:self.update_transform())
        self.visible.trace_add('write',lambda *_:self.update_model_visibility())
        self._set_window_geometry()
        self.window.deiconify()
        self.window.after_idle(self._load_initial)

    def _set_window_geometry(self):
        x,y,w,h=desktop_work_area(self.parent)
        width=min(1190,max(720,w-80))
        height=min(810,max(440,h-85))
        self.window.geometry(f'{width}x{height}+{x+(w-width)//2}+{y+(h-height)//2}')

    def _make_pcb(self):
        vtk=self.vtk
        board=vtk.vtkCubeSource()
        board.SetXLength(self.g.ow+3.5)
        board.SetYLength(self.g.oh+3.5)
        board.SetZLength(1.6)
        board.SetCenter(0,0,-0.82)
        mapper=vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(board.GetOutputPort())
        self.board_actor=vtk.vtkActor()
        self.board_actor.SetMapper(mapper)
        prop=self.board_actor.GetProperty()
        prop.SetColor(.038,.20,.12)
        prop.SetAmbient(.38)
        self.renderer.AddActor(self.board_actor)
        pts=vtk.vtkPoints()
        cells=vtk.vtkCellArray()
        for polygon in self.g.primitives():
            start=pts.GetNumberOfPoints()
            for xx,yy in polygon:
                pts.InsertNextPoint(xx,-yy,.012)
            item=vtk.vtkPolygon()
            item.GetPointIds().SetNumberOfIds(len(polygon))
            for i in range(len(polygon)):
                item.GetPointIds().SetId(i,start+i)
            cells.InsertNextCell(item)
        poly=vtk.vtkPolyData()
        poly.SetPoints(pts)
        poly.SetPolys(cells)
        filter=vtk.vtkTriangleFilter()
        filter.SetInputData(poly)
        filter.Update()
        mapper=vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(filter.GetOutputPort())
        self.copper_actor=vtk.vtkActor()
        self.copper_actor.SetMapper(mapper)
        self.copper_actor.GetProperty().SetColor(0.90,0.62,0.15)
        self.copper_actor.GetProperty().SetAmbient(.5)
        self.renderer.AddActor(self.copper_actor)
        self.set_camera('iso')

    def _load_initial(self):
        file=self.parent.vars['model_file'].get()
        if file and Path(file).is_file():
            try:
                self.load_model(file)
            except Exception as exc:
                self.messagebox.showerror(self.parent.t('error'),
                    self.parent.t('failed_to_load_step',error=str(exc)),parent=self.window)

    def select_model(self):
        file=self.filedialog.askopenfilename(
            parent=self.window, title=self.parent.t('models_3d'),
            initialdir=str(Path(self.parent.vars['model_file'].get()).parent)
                         if self.parent.vars['model_file'].get() else str(Path.home()),
            filetypes=[('STEP (*.step, *.stp)', '*.step *.stp')])
        if file:
            try:
                self.load_model(file)
                self.parent.vars['model_file'].set(str(Path(file).resolve()))
            except Exception as exc:
                self.messagebox.showerror(self.parent.t('error'),
                        self.parent.t('failed_to_load_step',error=str(exc)),parent=self.window)

    def remove_model(self):
        self.parent.vars['model_file'].set('')
        if self.model_actor:
            self.renderer.RemoveActor(self.model_actor)
            self.model_actor=None
        self._render()

    @staticmethod
    def _step_polydata(path):
        import vtk
        from OCP.STEPControl import STEPControl_Reader
        from OCP.BRepMesh import BRepMesh_IncrementalMesh
        from OCP.TopExp import TopExp_Explorer
        from OCP.TopAbs import TopAbs_FACE, TopAbs_REVERSED
        from OCP.TopoDS import TopoDS
        from OCP.BRep import BRep_Tool
        from OCP.TopLoc import TopLoc_Location
        reader=STEPControl_Reader()
        status=reader.ReadFile(str(path))
        if status != 1 or reader.TransferRoots()<1:
            raise ValueError('STEPControl_Reader could not read solid')
        shape=reader.OneShape()
        mesher=BRepMesh_IncrementalMesh(shape, 0.10, False, 0.35, True)
        mesher.Perform()
        points=vtk.vtkPoints()
        polys=vtk.vtkCellArray()
        exp=TopExp_Explorer(shape, TopAbs_FACE)
        ntris=0
        # OCP 8 renamed TopoDS.Face_s to TopoDS.Face.
        # The newer alias also exists in OCP 7.9; support both.
        downcast_face = getattr(TopoDS, "Face", None) or getattr(TopoDS, "Face_s")
        while exp.More():
            face=downcast_face(exp.Current())
            location=TopLoc_Location()
            tri=BRep_Tool.Triangulation_s(face,location)
            if tri is not None:
                first=points.GetNumberOfPoints()
                loc=location.Transformation()
                for i in range(1,tri.NbNodes()+1):
                    node=tri.Node(i).Transformed(loc)
                    points.InsertNextPoint(node.X(),node.Y(),node.Z())
                reversed_face=face.Orientation()==TopAbs_REVERSED
                for i in range(1,tri.NbTriangles()+1):
                    indices=list(tri.Triangle(i).Get())
                    if reversed_face:
                        indices[1],indices[2]=indices[2],indices[1]
                    triangle=vtk.vtkTriangle()
                    for j,index in enumerate(indices):
                        triangle.GetPointIds().SetId(j,first+index-1)
                    polys.InsertNextCell(triangle)
                    ntris+=1
            exp.Next()
        if ntris==0:
            raise ValueError('STEP model contains no triangulated surfaces')
        mesh=vtk.vtkPolyData()
        mesh.SetPoints(points)
        mesh.SetPolys(polys)
        normals=vtk.vtkPolyDataNormals()
        normals.SetInputData(mesh)
        normals.ConsistencyOn()
        normals.AutoOrientNormalsOn()
        normals.SplittingOff()
        normals.Update()
        return normals.GetOutput()

    def load_model(self,path):
        mesh=self._step_polydata(path)
        mapper=self.vtk.vtkPolyDataMapper()
        mapper.SetInputData(mesh)
        actor=self.vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(.77,.79,.81)
        actor.GetProperty().SetSpecular(.7)
        actor.GetProperty().SetSpecularPower(35)
        actor.GetProperty().SetDiffuse(.70)
        if self.model_actor is not None:
            self.renderer.RemoveActor(self.model_actor)
        self.model_actor=actor
        self.renderer.AddActor(actor)
        self.update_transform()
        self.update_model_visibility()
        self.fit_camera()

    def update_transform(self):
        if self.model_actor is None:
            return
        v=self.parent.vars
        try:
            sx,sy,sz=(as_float(v['model_'+k].get()) for k in ('sx','sy','sz'))
            rx,ry,rz=(as_float(v['model_'+k].get()) for k in ('rx','ry','rz'))
            ox,oy,oz=(as_float(v['model_'+k].get()) for k in ('ox','oy','oz'))
            if min(sx,sy,sz)<=0: return
        except (ValueError,KeyError):
            return
        t=self.vtk.vtkTransform()
        t.PostMultiply()
        t.Scale(sx,sy,sz)
        t.RotateX(rx)
        t.RotateY(ry)
        t.RotateZ(rz)
        # Match the KiCad footprint convention: +Y points down on the 2D PCB.
        # The STEP model uses a conventional 3D +Y axis.
        t.Translate(ox,-oy,oz)
        self.model_actor.SetUserTransform(t)
        self.renderer.ResetCameraClippingRange()
        self._queue_render()

    def update_opacity(self,*_):
        if self.model_actor is None:
            return
        try:
            alpha=max(0,min(100,as_float(self.parent.vars['model_opacity'].get())))/100
        except ValueError:
            alpha=1
        self.model_actor.GetProperty().SetOpacity(alpha)
        self._queue_render()

    def update_model_visibility(self):
        if self.model_actor is not None:
            self.model_actor.SetVisibility(bool(self.visible.get()))
        if self.board_actor is not None:
            self.board_actor.SetVisibility(bool(self.board_visible.get()))
        if self.copper_actor is not None:
            self.copper_actor.SetVisibility(bool(self.board_visible.get()))
        self.update_opacity()
        self._queue_render()

    def set_camera(self,direction):
        size=max(self.g.ow,self.g.oh)*1.75
        cam=self.renderer.GetActiveCamera()
        if direction=='top':
            cam.SetPosition(0,0,size*2)
            cam.SetViewUp(0,1,0)
        elif direction=='bottom':
            cam.SetPosition(0,0,-size*2)
            cam.SetViewUp(0,-1,0)
        elif direction=='side':
            cam.SetPosition(0,-size*2,size*.4)
            cam.SetViewUp(0,0,1)
        else:
            cam.SetPosition(size,-size,size*1.15)
            cam.SetViewUp(0,0,1)
        cam.SetFocalPoint(0,0,0)
        cam.ParallelProjectionOn()
        self.fit_camera()

    def fit_camera(self):
        self.renderer.ResetCamera()
        self.renderer.ResetCameraClippingRange()
        self._render()

    def _render(self):
        """Render actual VTK geometry to an in-memory PNG and show it in Tk.

        Works without vtkRenderingTk / libvtkRenderingTk, which is absent from
        many standard VTK pip wheels, including on Windows.
        """
        if not self.window.winfo_exists():
            return
        try:
            width=max(160,self.view_canvas.winfo_width())
            height=max(160,self.view_canvas.winfo_height())
            self.render_window.SetSize(width,height)
            self.render_window.Render()
            self._image_filter.Modified()
            self._image_filter.Update()
            self._writer.Write()
            png_bytes=bytes(memoryview(self._writer.GetResult()))
            self._photo=self.tk.PhotoImage(data=base64.b64encode(png_bytes), format='png')
            if self._image_item is None:
                self._image_item=self.view_canvas.create_image(0,0,anchor='nw',image=self._photo)
            else:
                self.view_canvas.itemconfigure(self._image_item,image=self._photo)
        except Exception as exc:
            self.view_canvas.delete('all')
            self._image_item=None
            self.view_canvas.create_text(20,25,anchor='nw',fill='white',
                                         text='3D render: '+str(exc),width=400)

    def _queue_render(self,event=None):
        if self._render_queued:
            return
        self._render_queued=True
        self.window.after(70,self._run_queued_render)

    def _run_queued_render(self):
        self._render_queued=False
        self._render()

    def _start_drag(self,event):
        self._drag_start=(event.x,event.y)

    def _drag_rotate(self,event):
        if self._drag_start is None:
            return
        dx=event.x-self._drag_start[0]
        dy=event.y-self._drag_start[1]
        self._drag_start=(event.x,event.y)
        cam=self.renderer.GetActiveCamera()
        cam.Azimuth(-dx*0.55)
        cam.Elevation(-dy*0.55)
        cam.OrthogonalizeViewUp()
        self.renderer.ResetCameraClippingRange()
        self._queue_render()

    def _drag_pan(self,event):
        if self._drag_start is None:
            return
        dx=event.x-self._drag_start[0]
        dy=event.y-self._drag_start[1]
        self._drag_start=(event.x,event.y)
        cam=self.renderer.GetActiveCamera()
        up=list(cam.GetViewUp())
        direction=list(cam.GetDirectionOfProjection())
        right=[direction[1]*up[2]-direction[2]*up[1],
               direction[2]*up[0]-direction[0]*up[2],
               direction[0]*up[1]-direction[1]*up[0]]
        length=max(1,self.view_canvas.winfo_height())
        scale=2*cam.GetParallelScale()/length
        motion=[(-dx*right[i]+dy*up[i])*scale for i in range(3)]
        cam.SetPosition(*[x+y for x,y in zip(cam.GetPosition(),motion)])
        cam.SetFocalPoint(*[x+y for x,y in zip(cam.GetFocalPoint(),motion)])
        self._queue_render()

    def _wheel_zoom(self,event):
        self._zoom(1.12 if event.delta>0 else 1/1.12)

    def _zoom(self,amount):
        cam=self.renderer.GetActiveCamera()
        cam.SetParallelScale(max(.02,cam.GetParallelScale()/amount))
        self._queue_render()

    def winfo_exists(self):
        return self.window.winfo_exists()

    def lift(self):
        self.window.lift()
        self.window.focus_force()

    def close(self):
        try:
            self.parent.write_settings()
        except OSError:
            pass
        try:
            self.render_window.Finalize()
        except Exception:
            pass
        self.window.destroy()
        self.parent._3d_window=None


def run_gui():
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox

    class GeneratorApp(tk.Tk):
        def __init__(self):
            super().__init__()
            saved = load_settings()
            self.withdraw()  # Do not flash at 0,0 before centering.
            self.minsize(600, 350)
            initial_dir = Path.home() / "Documents"
            if not initial_dir.is_dir():
                initial_dir = Path.home()
            defaults = {
                "horizontal": "19,0", "vertical": "10,2", "radius": "1,15",
                "inner_radius": "0,3", "rim": "1,5", "courtyard": "0,25",
                "pad_number": "1", "mode": "centerline", "paste": True,
                "mask": True, "fab_shield": True, "shield_thickness": "0,3",
                "paste_segmented": True, "paste_length": "2,5", "paste_gap": "0,35",
                "paste_inset": "0,15", "generate_courtyard": True,
                "filename": DEFAULT_FILENAME,
                "folder": str(initial_dir), "language": "uk",
                "model_file": "", "embed_model": True,
                "model_sx": "1", "model_sy": "1", "model_sz": "1",
                "model_rx": "0", "model_ry": "0", "model_rz": "0",
                "model_ox": "0", "model_oy": "0", "model_oz": "0",
                "model_opacity": "100",
            }
            for key, default in defaults.items():
                value = saved.get(key, default)
                if isinstance(default, bool):
                    defaults[key] = value if isinstance(value, bool) else default
                elif isinstance(value, (str, int, float)):
                    defaults[key] = str(value)
            if defaults["language"] not in LANGUAGE_NAMES:
                defaults["language"] = "uk"
            # When unpacked on another computer, an old save directory may not exist.
            if not Path(defaults["folder"]).expanduser().is_dir():
                defaults["folder"] = str(initial_dir)
            if defaults["mode"] not in ("outer", "centerline"):
                defaults["mode"] = "centerline"
            self.vars = {key: (tk.BooleanVar(value=val) if isinstance(val, bool)
                               else tk.StringVar(value=val))
                         for key, val in defaults.items()}
            self.lang_label = tk.StringVar(value=LANGUAGE_NAMES[defaults["language"]])
            self.status_var = tk.StringVar(value="")
            self.summary_var = tk.StringVar(value="")
            self._frame = None
            self.canvas = None
            self._3d_window = None
            self._make_widgets()
            self._center_and_fit_window()
            self.lang_label.trace_add("write", self._change_language)
            self.bind_all("<MouseWheel>", self._on_form_wheel, add="+")
            self.bind_all("<Button-4>", self._on_form_wheel, add="+")
            self.bind_all("<Button-5>", self._on_form_wheel, add="+")
            for key in ("horizontal", "vertical", "radius", "inner_radius", "rim", "courtyard", "mode",
                        "fab_shield", "shield_thickness", "paste", "paste_segmented",
                        "paste_length", "paste_gap", "paste_inset", "generate_courtyard"):
                self.vars[key].trace_add("write", lambda *_: self.redraw())
            self.protocol("WM_DELETE_WINDOW", self.on_close)
            self.deiconify()
            self.redraw()

        def _center_and_fit_window(self):
            """Always open centered; account for a Windows taskbar and window chrome."""
            self.update_idletasks()
            left, top, width, height = desktop_work_area(self)
            # Leave some room for the title bar and outer window decorations.
            width = min(1200, max(320, width - 32))
            height = min(800, max(240, height - 60))
            work_x, work_y, work_w, work_h = desktop_work_area(self)
            x = work_x + max(0, (work_w - width) // 2)
            y = work_y + max(0, (work_h - height) // 2)
            self.minsize(min(800, width), min(450, height))
            self.geometry(f"{width}x{height}+{x}+{y}")
            self.update_idletasks()

        def _on_form_wheel(self, event):
            """Scroll settings with wheel only when pointer is over settings pane."""
            canvas = getattr(self, "form_canvas", None)
            column = getattr(self, "form_column", None)
            if canvas is None or column is None or not canvas.winfo_exists():
                return
            x, y = self.winfo_pointerxy()
            pointer_widget = self.winfo_containing(x, y)
            if pointer_widget is None:
                return
            target = str(pointer_widget)
            prefix = str(column)
            if target != prefix and not target.startswith(prefix + "."):
                return
            if getattr(event, "num", None) == 4:
                delta = -3
            elif getattr(event, "num", None) == 5:
                delta = 3
            else:
                wheel = getattr(event, "delta", 0)
                if not wheel:
                    return
                delta = -int(wheel / 120) if abs(wheel) >= 120 else (-1 if wheel > 0 else 1)
            canvas.yview_scroll(delta, "units")

        @property
        def lang(self):
            return self.vars["language"].get()

        def t(self, key, **kwargs):
            return tr(self.lang, key, **kwargs)

        def _change_language(self, *_):
            selected = LANGUAGES.get(self.lang_label.get())
            if selected and selected != self.lang:
                self.vars["language"].set(selected)
                self._make_widgets()
                self.redraw()
                try:
                    self.write_settings()
                except OSError:
                    pass  # shown when saving/closing

        def _make_widgets(self):
            if self._frame is not None:
                self._frame.destroy()
            self.title(self.t("window_title"))
            style = ttk.Style()
            try:
                style.theme_use("clam")
            except tk.TclError:
                pass
            style.configure("Title.TLabel", font=("Segoe UI", 15, "bold"))
            style.configure("Sub.TLabel", font=("Segoe UI", 10, "bold"))
            frame = ttk.Frame(self, padding=11)
            frame.pack(fill="both", expand=True)
            self._frame = frame
            header = ttk.Frame(frame)
            header.pack(fill="x", pady=(0, 10))
            ttk.Label(header, text=self.t("title"), style="Title.TLabel").pack(side="left")
            ttk.Combobox(header, textvariable=self.lang_label, values=list(LANGUAGES),
                         state="readonly", width=13).pack(side="right")
            ttk.Label(header, text=self.t("language")).pack(side="right", padx=(10, 5))
            content = ttk.Frame(frame)
            content.pack(fill="both", expand=True)
            self.form_column = ttk.Frame(content, width=450)
            self.form_column.pack(side="left", fill="y", padx=(0, 12))
            self.form_column.pack_propagate(False)
            form_scroll_area = ttk.Frame(self.form_column)
            form_scroll_area.pack(side="top", fill="both", expand=True)
            self.form_canvas = tk.Canvas(form_scroll_area, highlightthickness=0,
                                         borderwidth=0, width=420, bg=style.lookup("TFrame", "background"))
            form_scrollbar = ttk.Scrollbar(form_scroll_area, orient="vertical",
                                           command=self.form_canvas.yview)
            self.form_canvas.configure(yscrollcommand=form_scrollbar.set)
            form_scrollbar.pack(side="right", fill="y")
            self.form_canvas.pack(side="left", fill="both", expand=True)
            form_holder = ttk.Frame(self.form_canvas)
            form_window = self.form_canvas.create_window((0, 0), window=form_holder,
                                                         anchor="nw")
            # A regular frame saves the vertical space previously taken up by
            # the decorative "Geometry and export" label frame caption.
            form = ttk.Frame(form_holder, padding=(10, 2, 10, 8))
            form.pack(fill="x")
            form.columnconfigure(1, weight=1)
            def update_form_scrollregion(_event=None):
                self.form_canvas.configure(scrollregion=self.form_canvas.bbox("all"))
            def update_form_width(event):
                self.form_canvas.itemconfigure(form_window, width=event.width)
            form_holder.bind("<Configure>", update_form_scrollregion)
            self.form_canvas.bind("<Configure>", update_form_width)
            row = 0
            ttk.Label(form, text=self.t("dimension_mode"), style="Sub.TLabel").grid(
                row=row, column=0, columnspan=3, sticky="w", pady=(0, 5))
            row += 1
            for mode in ("centerline", "outer"):
                ttk.Radiobutton(form, text=self.t(mode), variable=self.vars["mode"], value=mode).grid(
                    row=row, column=0, columnspan=3, sticky="w")
                row += 1

            def add_entry(label_key, variable_key, unit_key="mm"):
                nonlocal row
                ttk.Label(form, text=self.t(label_key)).grid(row=row, column=0, sticky="w", pady=3)
                ttk.Entry(form, width=14, textvariable=self.vars[variable_key]).grid(
                    row=row, column=1, sticky="ew", padx=8, pady=3)
                if unit_key:
                    ttk.Label(form, text=self.t(unit_key)).grid(row=row, column=2, sticky="w", pady=3)
                row += 1

            for title, name in (("horizontal", "horizontal"), ("vertical", "vertical"),
                                ("outer_radius", "radius"), ("inner_radius", "inner_radius"),
                                ("rim", "rim")):
                add_entry(title, name)
            add_entry("pad_number", "pad_number", unit_key=None)
            ttk.Checkbutton(form, text=self.t("auto_courtyard"),
                            variable=self.vars["generate_courtyard"]).grid(
                row=row, column=0, columnspan=3, sticky="w", pady=(5, 0))
            row += 1
            add_entry("courtyard", "courtyard")
            ttk.Separator(form).grid(row=row, column=0, columnspan=3, sticky="ew", pady=6)
            row += 1
            # Put F.Mask and F.Paste on the SAME row in every GUI language.
            # A frame avoids squeezing the long localized labels into cells.
            layer_options = ttk.Frame(form)
            layer_options.grid(row=row, column=0, columnspan=3, sticky="w", pady=3)
            ttk.Checkbutton(layer_options, text=self.t("mask"),
                            variable=self.vars["mask"]).pack(side="left", padx=(0, 14))
            ttk.Checkbutton(layer_options, text=self.t("paste"),
                            variable=self.vars["paste"]).pack(side="left")
            row += 1
            ttk.Checkbutton(form, text=self.t("paste_segmented"),
                            variable=self.vars["paste_segmented"]).grid(
                row=row, column=0, columnspan=3, sticky="w", pady=(2, 3))
            row += 1
            for label, name in (("paste_length", "paste_length"),
                                ("paste_gap", "paste_gap"), ("paste_inset", "paste_inset")):
                add_entry(label, name)
            fab_control = ttk.Frame(form)
            fab_control.grid(row=row, column=0, columnspan=3, sticky="ew", pady=(5, 4))
            ttk.Checkbutton(fab_control, text=self.t("fab_shield"),
                            variable=self.vars["fab_shield"]).pack(side="left")
            ttk.Label(fab_control, text=self.t("shield_thickness")).pack(
                side="left", padx=(9, 4))
            ttk.Entry(fab_control, width=6,
                      textvariable=self.vars["shield_thickness"]).pack(side="left")
            ttk.Label(fab_control, text=self.t("mm")).pack(side="left", padx=(4, 0))
            row += 1
            ttk.Separator(form).grid(row=row, column=0, columnspan=3, sticky="ew", pady=6)
            row += 1
            ttk.Label(form, text=self.t("filename"), style="Sub.TLabel").grid(
                row=row, column=0, columnspan=3, sticky="w", pady=3)
            row += 1
            ttk.Entry(form, width=45, textvariable=self.vars["filename"]).grid(
                row=row, column=0, columnspan=3, sticky="ew", pady=4)
            row += 1
            ttk.Label(form, text=self.t("folder"), style="Sub.TLabel").grid(
                row=row, column=0, columnspan=3, sticky="w", pady=(5, 2))
            row += 1
            ttk.Entry(form, textvariable=self.vars["folder"]).grid(
                row=row, column=0, columnspan=2, sticky="ew", pady=3)
            ttk.Button(form, text="…", width=4, command=self.choose_folder).grid(
                row=row, column=2, sticky="e", padx=(4, 0))
            row += 1
            # Save remains visible even on a short display; only the parameters scroll.
            form_footer = ttk.Frame(self.form_column, padding=(0, 8, 0, 0))
            form_footer.pack(side="bottom", fill="x")
            ttk.Button(form_footer, text=self.t("save"), command=self.save).pack(
                fill="x", ipady=5)
            ttk.Label(form_footer, textvariable=self.status_var, wraplength=390).pack(
                anchor="w", pady=(4, 0))
            right = ttk.Frame(content)
            right.pack(side="left", fill="both", expand=True)
            # Persistent clickable credit at bottom right, independent of the
            # resizable preview and the left settings' scrolling position.
            style.configure("ProjectLink.TLabel", font=("Segoe UI", 8, "underline"),
                            foreground="#286aab")
            project_link = ttk.Label(right, text=PROJECT_URL, style="ProjectLink.TLabel",
                                     cursor="hand2", anchor="e")
            project_link.pack(side="bottom", anchor="e", pady=(2, 0))
            project_link.bind("<Button-1>", lambda _event: webbrowser.open(PROJECT_URL, new=2))
            self.project_link = project_link
            preview_frame = ttk.LabelFrame(right, text=self.t("preview"), padding=8)
            preview_frame.pack(fill="both", expand=True)
            self.canvas = tk.Canvas(preview_frame, bg="#111a29", highlightthickness=0)
            self.canvas.pack(fill="both", expand=True)
            self.canvas.bind("<Configure>", lambda _: self.redraw())
            preview_actions = ttk.Frame(right)
            preview_actions.pack(fill="x", pady=(6, 0))
            ttk.Button(preview_actions, text=self.t("preview_3d"),
                       command=self.open_3d_preview).pack(side="right")
            summary_label = ttk.Label(right, textvariable=self.summary_var,
                                      justify="left", wraplength=500)
            summary_label.pack(anchor="w", pady=(10, 0), fill="x")
            self.legend_var = tk.StringVar()
            legend_label = ttk.Label(right, textvariable=self.legend_var,
                                     foreground="#697386", wraplength=500)
            legend_label.pack(anchor="w", pady=5, fill="x")
            def wrap_preview_text(event):
                line_width = max(120, event.width - 20)
                summary_label.configure(wraplength=line_width)
                legend_label.configure(wraplength=line_width)
                # Keep the link entirely visible on narrow screens while the
                # click action continues to open the full canonical URL.
                project_link.configure(text=(PROJECT_URL if event.width >= 335
                                             else PROJECT_URL.removeprefix("https://")))
            right.bind("<Configure>", wrap_preview_text)

        def geometry_from_fields(self):
            return RingGeometry(
                horizontal=as_float(self.vars["horizontal"].get()),
                vertical=as_float(self.vars["vertical"].get()),
                radius=as_float(self.vars["radius"].get()),
                rim=as_float(self.vars["rim"].get()),
                mode=self.vars["mode"].get(),
                courtyard=as_float(self.vars["courtyard"].get()),
                inner_radius=as_float(self.vars["inner_radius"].get()),
            )

        def choose_folder(self):
            folder = self.vars["folder"].get()
            chosen = filedialog.askdirectory(
                initialdir=folder if os.path.isdir(folder) else str(Path.home()))
            if chosen:
                self.vars["folder"].set(chosen)

        def redraw(self):
            if self.canvas is None:
                return
            canvas = self.canvas
            canvas.delete("all")
            w, h = canvas.winfo_width(), canvas.winfo_height()
            if w < 50 or h < 50:
                return
            try:
                g = self.geometry_from_fields()
            except (ValueError, GeometryError) as exc:
                key = str(exc)
                self.summary_var.set(self.t("invalid_geometry") + ": " + self.t(key))
                canvas.create_text(w/2, h/2, text=self.t("check_geometry"), fill="#ffb4b4",
                                   font=("Segoe UI", 13))
                return
            outer_screen = inner_screen = None
            try:
                if self.vars["fab_shield"].get():
                    outer_screen, inner_screen = g.shield_geometry(
                        as_float(self.vars["shield_thickness"].get()))
            except (ValueError, GeometryError) as exc:
                key = str(exc)
                self.summary_var.set(self.t("invalid_geometry") + ": " + self.t(key))
                canvas.create_text(w/2, h/2, text=self.t(key), fill="#ffb4b4",
                                   font=("Segoe UI", 12), width=w-60)
                return
            self.legend_var.set(self.t("legend") + " " +
                self.t("fab_enabled_legend" if outer_screen is not None else "fab_disabled_legend"))
            scale = min(max(5, w-70) / max(g.ow+2*g.courtyard, .1),
                        max(5, h-110) / max(g.oh+2*g.courtyard, .1))
            scale = max(.2, scale)
            xf = lambda x: w/2 + x*scale
            yf = lambda y: h/2 + y*scale
            def flatten(pts):
                return [v for x, y in pts for v in (xf(x), yf(y))]
            canvas.create_line(0, h/2, w, h/2, fill="#263347", dash=(4,6))
            canvas.create_line(w/2, 0, w/2, h, fill="#263347", dash=(4,6))
            canvas.create_polygon(flatten(g.contour()), fill="#c93735", outline="#e77d55", width=1.2)
            canvas.create_polygon(flatten(g.contour(inner=True)), fill="#111a29", outline="#f0b355", width=1.3)
            if self.vars["paste"].get() and self.vars["paste_segmented"].get():
                try:
                    paste_rects = segmented_paste_rectangles(
                        g, as_float(self.vars["paste_length"].get()),
                        as_float(self.vars["paste_gap"].get()),
                        as_float(self.vars["paste_inset"].get()))
                    for px, py, pw, ph in paste_rects:
                        canvas.create_rectangle(xf(px-pw/2), yf(py-ph/2),
                                                xf(px+pw/2), yf(py+ph/2),
                                                fill="#efa26e", outline="#ffe0a8", width=0.4)
                except (ValueError, GeometryError) as exc:
                    self.summary_var.set(self.t(str(exc)))
            if outer_screen is None:
                cp = g.centerline_contour()
                canvas.create_line(*flatten(cp), *flatten(cp[:1]),
                                   fill="#54e2e8", dash=(5,5), width=1.3)
            else:
                for outline, color in ((outer_screen, "#5be3e7"),
                                       (inner_screen, "#a8ef89")):
                    pts = g.rounded_contour(*outline)
                    canvas.create_line(*flatten(pts), *flatten(pts[:1]),
                                       fill=color, width=2.1)
            margin = g.courtyard
            if self.vars["generate_courtyard"].get():
                canvas.create_rectangle(xf(-g.ow/2-margin), yf(-g.oh/2-margin),
                                        xf(g.ow/2+margin), yf(g.oh/2+margin),
                                        outline="#dd44ca", width=1.3)
            narrow = w < 360
            top_line = (f'{g.ow:.2f} × {g.oh:.2f} {self.t("mm")}' if narrow
                        else f'{self.t("outside")}: {g.ow:.2f} × {g.oh:.2f} {self.t("mm")}')
            mid_line = (f'{g.centerline_w:.2f} × {g.centerline_h:.2f} {self.t("mm")}' if narrow
                        else f'{self.t("centerline_label")}: {g.centerline_w:.2f} × {g.centerline_h:.2f} {self.t("mm")}')
            bottom_line = (f'W {g.rim:.2f}  •  R {g.radius:.2f}/{g.ir:.2f}' if narrow
                           else f'{self.t("rim_short")}: {g.rim:.2f}   •   '
                                f'{self.t("outer_r_short")}: {g.radius:.2f}   •   '
                                f'{self.t("inner_r_short")}: {g.ir:.2f} {self.t("mm")}')
            font_size = 10 if narrow else 12
            canvas.create_text(w/2, 23, text=top_line,
                               fill="white", font=("Segoe UI", font_size, "bold"), width=w-12)
            canvas.create_text(w/2, h-43, text=mid_line,
                               fill="#70d6ea", font=("Segoe UI", 9 if narrow else 10), width=w-12)
            canvas.create_text(w/2, h-23, text=bottom_line,
                               fill="white", font=("Segoe UI", 9 if narrow else 10), width=w-12)
            if self.winfo_height() < 650 or w < 360:
                self.summary_var.set(
                    f'{self.t("outside")}: {g.ow:.2f} × {g.oh:.2f}   |   '
                    f'{self.t("inside")}: {g.iw:.2f} × {g.ih:.2f} {self.t("mm")}\n'
                    f'{self.t("outer_r_short")}: {g.radius:.2f}   |   '
                    f'{self.t("inner_r_short")}: {g.ir:.2f}   |   '
                    f'{self.t("shield_thickness")}: {as_float(self.vars["shield_thickness"].get()):.2f} {self.t("mm")}'
                    if outer_screen is not None else
                    f'{self.t("outside")}: {g.ow:.2f} × {g.oh:.2f}   |   '
                    f'{self.t("inside")}: {g.iw:.2f} × {g.ih:.2f} {self.t("mm")}\n'
                    f'{self.t("outer_r_short")}: {g.radius:.2f}   |   '
                    f'{self.t("inner_r_short")}: {g.ir:.2f}   |   '
                    f'{self.t("rim_short")}: {g.rim:.2f} {self.t("mm")}'
                )
                self.legend_var.set("F.Cu   •   F.Fab" if outer_screen is not None else "F.Cu   •   F.CrtYd")
                return
            self.summary_var.set(
                f'{self.t("centerline_label")}: {g.centerline_w:.3f} × {g.centerline_h:.3f} {self.t("mm")}   |   '
                f'{self.t("outside")}: {g.ow:.3f} × {g.oh:.3f} {self.t("mm")}\n'
                f'{self.t("inside")}: {g.iw:.3f} × {g.ih:.3f} {self.t("mm")}   |   '
                f'{self.t("outer_r_short")}: {g.radius:.3f}   |   {self.t("inner_r_short")}: {g.ir:.3f}\n'
                + (f'{self.t("shield_thickness")}: {as_float(self.vars["shield_thickness"].get()):.3f} {self.t("mm")}   |   F.Fab: 2\n'
                   if outer_screen is not None else '')
                + self.t("one_pad")
            )

        def model_transforms(self):
            return {k: self.vars['model_'+k].get() for k in
                    ('sx','sy','sz','rx','ry','rz','ox','oy','oz')}

        def open_3d_preview(self):
            if self._3d_window is not None:
                try:
                    if self._3d_window.winfo_exists():
                        self._3d_window.lift()
                        return
                except Exception:
                    pass
            try:
                g=self.geometry_from_fields()
                self._3d_window=StepPreviewWindow(self, g)
            except (ImportError, RuntimeError) as exc:
                key=str(exc)
                messagebox.showerror(self.t('error'),
                                     self.t(key) if key in I18N[self.lang] else key)
            except Exception as exc:
                messagebox.showerror(self.t('error'),self.t('failed_3d',error=str(exc)))

        def write_settings(self):
            save_settings({k: v.get() for k, v in self.vars.items()})

        def on_close(self):
            if self._3d_window is not None:
                try:
                    if self._3d_window.winfo_exists():
                        self._3d_window.close()
                except Exception:
                    pass
            try:
                self.write_settings()
            except OSError as exc:
                messagebox.showwarning(self.t("settings_warning"),
                                       self.t("settings_error", reason=str(exc)))
            self.destroy()

        def save(self):
            try:
                g = self.geometry_from_fields()
                name = kicad_name(self.vars["filename"].get())
                folder = Path(self.vars["folder"].get()).expanduser()
                if not folder.is_dir():
                    raise ValueError("err_folder")
                path = folder / (name + ".kicad_mod")
                if path.exists() and not messagebox.askyesno(
                        self.t("confirm"), self.t("overwrite", path=path)):
                    return
                footprint = make_footprint(g, name, pad_number=self.vars["pad_number"].get(),
                                           paste=self.vars["paste"].get(),
                                           mask=self.vars["mask"].get(),
                                           fab_shield=self.vars["fab_shield"].get(),
                                           shield_thickness=(as_float(self.vars["shield_thickness"].get())
                                               if self.vars["fab_shield"].get() else 0.3),
                                           generate_courtyard=self.vars["generate_courtyard"].get(),
                                           paste_segmented=self.vars["paste_segmented"].get(),
                                           paste_length=as_float(self.vars["paste_length"].get()),
                                           paste_gap=as_float(self.vars["paste_gap"].get()),
                                           paste_inset=as_float(self.vars["paste_inset"].get()),
                                           model_file=self.vars['model_file'].get().strip() or None,
                                           model_transform=self.model_transforms(),
                                           embed_model=self.vars['embed_model'].get())
                path.write_text(footprint, encoding="utf-8")
                self.status_var.set(self.t("saved", path=path))
                try:
                    self.write_settings()
                except OSError as exc:
                    messagebox.showwarning(self.t("settings_warning"),
                                           self.t("settings_error", reason=str(exc)))
                messagebox.showinfo(self.t("done"), self.t("saved_message", path=path))
            except (ValueError, OSError, RuntimeError) as exc:
                key = str(exc)
                text = self.t(key) if key in I18N[self.lang] else key
                self.status_var.set(self.t("error") + ": " + text)
                messagebox.showerror(self.t("error"), text)

    app = GeneratorApp()
    app.mainloop()


def main():
    parser = argparse.ArgumentParser(description="Generate a single hollow custom SMD pad for KiCad")
    parser.add_argument("--generate", metavar="FILE", help="Write a .kicad_mod footprint without opening GUI")
    parser.add_argument("--horizontal", type=float, default=19.0, help="Horizontal dimension, mm")
    parser.add_argument("--vertical", type=float, default=10.2, help="Vertical dimension, mm")
    parser.add_argument("--radius", type=float, default=1.15, help="Outer corner radius in mm")
    parser.add_argument("--inner-radius", type=float, default=0.3, help="Inner corner radius in mm")
    parser.add_argument("--rim", type=float, default=1.5, help="Copper strip width in mm")
    parser.add_argument("--courtyard", type=float, default=0.25, help="Courtyard margin in mm")
    parser.add_argument("--mode", choices=("centerline", "outer"), default="centerline")
    parser.add_argument("--no-paste", action="store_true", help="Omit F.Paste")
    parser.add_argument("--segmented-paste", action="store_true", help="Use segmented paste openings")
    parser.add_argument("--paste-length", type=float, default=2.5)
    parser.add_argument("--paste-gap", type=float, default=0.35)
    parser.add_argument("--paste-inset", type=float, default=0.15)
    parser.add_argument("--no-courtyard", action="store_true", help="Disable automatic F.CrtYd")
    parser.add_argument("--no-mask", action="store_true", help="Omit F.Mask")
    parser.add_argument("--pad-number", default="1")
    parser.add_argument("--fab-shield", action="store_true",
                        help="Draw outer and inner shield wall outlines on F.Fab")
    parser.add_argument("--shield-thickness", type=float, default=0.3,
                        help="Shield wall thickness inward from copper centerline, mm")
    parser.add_argument("--3d-model", help="Optional STEP/STP model to attach")
    parser.add_argument("--no-embed-model", action="store_true", help="Link STEP file instead of embedding")
    parser.add_argument("--3d-rotate", nargs=3, type=float, default=[0,0,0], metavar=("RX","RY","RZ"))
    parser.add_argument("--3d-offset", nargs=3, type=float, default=[0,0,0], metavar=("X","Y","Z"))
    args = parser.parse_args()
    if args.generate:
        try:
            g = RingGeometry(args.horizontal, args.vertical, args.radius, args.rim,
                             args.mode, args.courtyard, args.inner_radius)
            path = Path(args.generate)
            path.write_text(make_footprint(g, path.name, pad_number=args.pad_number,
                                           paste=not args.no_paste, mask=not args.no_mask,
                                           fab_shield=args.fab_shield,
                                           shield_thickness=args.shield_thickness,
                                           generate_courtyard=not args.no_courtyard,
                                           paste_segmented=args.segmented_paste,
                                           paste_length=args.paste_length,
                                           paste_gap=args.paste_gap,
                                           paste_inset=args.paste_inset,
                                           model_file=args.__dict__['3d_model'],
                                           embed_model=not args.no_embed_model,
                                           model_transform=dict(zip(('rx','ry','rz','ox','oy','oz'),
                                                     args.__dict__['3d_rotate']+args.__dict__['3d_offset']))),
                            encoding="utf-8")
            print(f"Created {path} | outer {g.ow:.3f} × {g.oh:.3f} mm; "
                  f"opening {g.iw:.3f} × {g.ih:.3f} mm; inner radius {g.ir:.3f} mm")
        except (ValueError, OSError, RuntimeError) as exc:
            print("Error:", tr("en", str(exc)), file=sys.stderr)
            return 1
        return 0
    try:
        run_gui()
    except ImportError:
        print("Tkinter missing. Install Python with Tcl/Tk support.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())

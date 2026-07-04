<div align="center">

# JustKeep (JKeep)

**Legacy notes app — Tkinter, SQLite, Windows releases.**

[![Python](https://img.shields.io/badge/python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Releases](https://img.shields.io/badge/releases-1.1.0%20Moonstone-34c759?style=flat-square)](https://github.com/krwg/j-keep/releases)
[![Successor](https://img.shields.io/badge/successor-j--keep--desktop-0071e3?style=flat-square)](https://github.com/krwg/j-keep-desktop)

</div>

---

**JustKeep** was an early **single-file** notes application (CustomTkinter + SQLite). It shipped Windows builds on [GitHub Releases](https://github.com/krwg/j-keep/releases) through **v1.1.0 Moonstone**.

Development continues in the modular repo **[j-keep-desktop](https://github.com/krwg/j-keep-desktop)** (v1.5.0+). This repository stays online for history, downloads, and the original codebase.

---

## Features (v1.1 era)

- Dark CustomTkinter UI
- Notes stored in **SQLite** (`notes.db`)
- Pin, format, copy notes
- Settings with update check
- Bundled `icon.ico` for Windows builds

---

## Run from source (legacy tree)

```bash
git clone https://github.com/krwg/j-keep.git
cd j-keep
pip install customtkinter Pillow requests
python note.py
```

For the current split codebase, use **j-keep-desktop** instead.

---

## Downloads

Prebuilt **Windows** `.exe` builds: **[Releases](https://github.com/krwg/j-keep/releases)** (latest tag **1.1.0 Moonstone**).

---

## Repository layout

```
j-keep/
├── note.py       # entire app (legacy monolith)
├── icon.ico
├── version.txt
└── README.md
```

---

## Related

| Repo | Role |
|------|------|
| **[j-keep](https://github.com/krwg/j-keep)** | Legacy JustKeep + release artifacts |
| **[j-keep-desktop](https://github.com/krwg/j-keep-desktop)** | Active JKeep desktop source |

---

<div align="center">

By [krwg](https://github.com/krwg) · archived lineage, living successor

</div>

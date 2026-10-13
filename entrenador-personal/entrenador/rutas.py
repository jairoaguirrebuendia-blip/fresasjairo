"""Ubicación de los datos del usuario.

Windows: %APPDATA%/PersonalTrainer
Otros:   ~/.personaltrainer
Se puede forzar con la variable de entorno ENTRENADOR_DATA.
"""
import os
from pathlib import Path


def data_dir() -> Path:
    override = os.environ.get("ENTRENADOR_DATA")
    if override:
        base = Path(override)
    elif os.name == "nt" and os.environ.get("APPDATA"):
        base = Path(os.environ["APPDATA"]) / "PersonalTrainer"
    else:
        base = Path.home() / ".personaltrainer"
    for sub in ("media/photos", "media/exports", "backups"):
        (base / sub).mkdir(parents=True, exist_ok=True)
    return base


def db_path() -> Path:
    return data_dir() / "db.sqlite"


def photos_dir() -> Path:
    return data_dir() / "media" / "photos"


def exports_dir() -> Path:
    return data_dir() / "media" / "exports"


def backups_dir() -> Path:
    return data_dir() / "backups"

import sqlite3

from datetime import datetime
from pathlib import Path

from django.conf import settings


def get_database_path():

    database_name = (
        settings.DATABASES[
            "default"
        ]["NAME"]
    )

    return Path(database_name)


def get_backup_directory():

    backup_dir = (
        Path(settings.BASE_DIR)
        / "backups"
    )

    backup_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    return backup_dir


def create_database_backup(
    prefix="sedulur_backup"
):

    db_path = get_database_path()

    if not db_path.exists():
        raise FileNotFoundError(
            "Database utama tidak ditemukan."
        )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    backup_path = (
        get_backup_directory()
        / (
            f"{prefix}_"
            f"{timestamp}.sqlite3"
        )
    )

    source = sqlite3.connect(
        str(db_path)
    )

    destination = sqlite3.connect(
        str(backup_path)
    )

    try:

        source.backup(
            destination
        )

    finally:

        destination.close()
        source.close()

    return backup_path


def validate_sqlite_database(
    file_path
):

    connection = None

    try:

        connection = sqlite3.connect(
            str(file_path)
        )

        cursor = connection.cursor()

        result = cursor.execute(
            "PRAGMA integrity_check;"
        ).fetchone()

        if not result:

            return (
                False,
                "Database tidak dapat diperiksa."
            )

        if result[0].lower() != "ok":

            return (
                False,
                (
                    "Database rusak atau "
                    "tidak valid."
                )
            )

        tables = cursor.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            """
        ).fetchall()

        table_names = {
            row[0]
            for row in tables
        }

        if (
            "django_migrations"
            not in table_names
        ):

            return (
                False,
                (
                    "File bukan database "
                    "aplikasi Sedulur yang valid."
                )
            )

        return True, "OK"

    except sqlite3.DatabaseError:

        return (
            False,
            "File bukan database SQLite yang valid."
        )

    finally:

        if connection:

            connection.close()
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect


from .models import CompanySetting
import os
import tempfile

from pathlib import Path

from django.conf import settings
from django.db import connections
from django.http import FileResponse

from .backup_service import (
    create_database_backup,
    get_backup_directory,
    get_database_path,
    validate_sqlite_database,
)

from .forms import (
    CompanySettingForm,
    DatabaseRestoreForm,
)

@login_required
def company_settings(request):

    company = CompanySetting.objects.first()

    if not company:

        company = CompanySetting.objects.create(
            company_name="PT Seduur Berkarys Grove"
        )

    if request.method == "POST":

        form = CompanySettingForm(
            request.POST,
            request.FILES,
            instance=company,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Profil perusahaan berhasil disimpan."
            )

            return redirect(
                "company:settings"
            )

    else:

        form = CompanySettingForm(
            instance=company
        )

    return render(
        request,
        "company/settings.html",
        {
            "form": form,
            "company": company,
        }
    )
@login_required
def database_backup_page(request):

    backup_dir = (
        get_backup_directory()
    )

    backups = sorted(
        backup_dir.glob(
            "*.sqlite3"
        ),
        key=lambda item:
            item.stat().st_mtime,
        reverse=True,
    )

    backup_list = []

    for backup in backups[:10]:

        backup_list.append(
            {
                "name": backup.name,
                "size": backup.stat().st_size,
                "modified":
                    backup.stat().st_mtime,
            }
        )

    restore_form = (
        DatabaseRestoreForm()
    )

    return render(
        request,
        "company/backup.html",
        {
            "restore_form":
                restore_form,

            "backups":
                backup_list,
        },
    )


@login_required
def database_backup_download(
    request
):

    try:

        backup_path = (
            create_database_backup()
        )

    except Exception as exc:

        messages.error(
            request,
            (
                "Backup gagal dibuat: "
                f"{exc}"
            ),
        )

        return redirect(
            "company:backup"
        )

    return FileResponse(
        open(
            backup_path,
            "rb"
        ),
        as_attachment=True,
        filename=backup_path.name,
        content_type=(
            "application/"
            "octet-stream"
        ),
    )


@login_required
def database_restore(
    request
):

    if request.method != "POST":

        return redirect(
            "company:backup"
        )

    form = DatabaseRestoreForm(
        request.POST,
        request.FILES,
    )

    if not form.is_valid():

        messages.error(
            request,
            (
                "File restore tidak valid. "
                "Periksa file dan konfirmasi."
            ),
        )

        return redirect(
            "company:backup"
        )

    uploaded_file = (
        form.cleaned_data[
            "database_file"
        ]
    )

    temp_path = None

    try:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".sqlite3",
        ) as temporary:

            for chunk in (
                uploaded_file.chunks()
            ):

                temporary.write(
                    chunk
                )

            temp_path = Path(
                temporary.name
            )

        valid, error_message = (
            validate_sqlite_database(
                temp_path
            )
        )

        if not valid:

            messages.error(
                request,
                error_message,
            )

            temp_path.unlink(
                missing_ok=True
            )

            return redirect(
                "company:backup"
            )

        # Backup keamanan sebelum restore
        create_database_backup(
            prefix="before_restore"
        )

        db_path = (
            get_database_path()
        )

        # Hapus session login saat ini
        # agar setelah restore login ulang.
        request.session.flush()

        # Tutup semua koneksi SQLite Django.
        connections.close_all()

        # Hapus file WAL/SHM jika ada.
        wal_file = Path(
            f"{db_path}-wal"
        )

        shm_file = Path(
            f"{db_path}-shm"
        )

        wal_file.unlink(
            missing_ok=True
        )

        shm_file.unlink(
            missing_ok=True
        )

        # Ganti database utama.
        os.replace(
            str(temp_path),
            str(db_path),
        )

        return redirect(
            "login"
        )

    except Exception as exc:

        if (
            temp_path
            and temp_path.exists()
        ):

            temp_path.unlink(
                missing_ok=True
            )

        messages.error(
            request,
            (
                "Restore database gagal: "
                f"{exc}"
            ),
        )

        return redirect(
            "company:backup"
        )
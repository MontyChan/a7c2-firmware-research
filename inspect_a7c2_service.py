"""Read-only A7C II 2.01 Service USB inventory.

Install requirements with ``python -m pip install -r requirements.txt`` and run
``python inspect_a7c2_service.py`` from the repository directory. The script
authenticates into Service USB, reads allowlisted data, and exits the session.
It contains no camera write operations. Generated dumps may contain private
camera data and are excluded from version control.
"""
import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

from camera_runtime import core, transport

PROGRAMS = {
    "appFw.so": "/usr/lib/appFw.so",
    "cpapp-b.bin": "/cp/cpapp-b.bin",
}
CP_KEYS = (0x02A40001, 0x02A4000D)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def write_bytes(folder, relative, data):
    path = folder / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def read_camera_file(session, camera_path):
    """Translate a camera path to the low-level Jiritsu selector namespace."""
    internal = "/tmp/jiritsu/../../" + camera_path.lstrip("/")
    return session.read(internal)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("a7c2-service-readonly"),
                        help="directory for read-only dumps and JSON report")
    args = parser.parse_args()

    if sys.platform != "win32":
        parser.error("This version supports Windows hosts only")

    if core.MODEL != "ILCE-7CM2" or core.VERSION != "2.01":
        raise RuntimeError("This inspector is pinned to ILCE-7CM2 firmware 2.01")

    out = args.out.resolve() / datetime.now().strftime("%Y%m%d-%H%M%S")
    out.mkdir(parents=True, exist_ok=False)
    report = {
        "schema": "a7c2-service-readonly-inventory/1",
        "model_target": core.MODEL,
        "firmware_assumption": core.VERSION,
        "started_local": datetime.now().astimezone().isoformat(),
        "read_only": True,
        "files": {},
        "settings": {},
        "errors": [],
    }

    print("Connecting through the normal Sony USB identity and requesting Service USB (0336)...", flush=True)
    with transport.Session() as session:
        report["identity"] = {"model": session.identity["model"]}
        for name, camera_path in PROGRAMS.items():
            print(f"Reading {camera_path} (read-only)", flush=True)
            data = read_camera_file(session, camera_path)
            path = write_bytes(out, f"programs/{name}", data)
            report["files"][camera_path] = {
                "bytes": len(data), "sha256": sha256(data),
                "dump": str(path.relative_to(out)),
            }

        for label, live in (("ram", True), ("saved", False)):
            settings_raw = session.call(session.camera.getBackupPresetData, live)
            records = core.backup_records(settings_raw)
            settings_path = write_bytes(out, f"settings/settings-{label}.bin", settings_raw)
            snapshot = {
                "bytes": len(settings_raw),
                "dump": str(settings_path.relative_to(out)),
                "chips": [],
            }
            report["settings"][label] = snapshot
            for chip_index, chip in enumerate(records):
                rows = []
                for key, record in sorted(chip.items()):
                    rows.append({
                        "key": f"0x{key:08x}", "attribute": record.attr,
                        "bytes": len(record.data), "value_hex": record.data.hex(),
                    })
                snapshot["chips"].append({
                    "index": chip_index, "record_count": len(rows), "records": rows,
                })

        for key in CP_KEYS:
            print(f"Reading CP unit 0x{key:08x} (read-only)", flush=True)
            data = session.cp_read(key)
            relative = f"settings/cp-{key:08x}.bin"
            path = write_bytes(out, relative, data)
            report["settings"][f"cp-0x{key:08x}"] = {
                "bytes": len(data), "sha256": sha256(data), "dump": relative,
            }

        for filename in core.RESOURCE_FILES:
            camera_path = "/usr/share/app/" + filename
            try:
                data = read_camera_file(session, camera_path)
            except Exception as exc:
                report["errors"].append({"path": camera_path, "error": str(exc)})
                continue
            relative = f"resources/{filename}"
            path = write_bytes(out, relative, data)
            report["files"][camera_path] = {
                "bytes": len(data), "sha256": sha256(data), "dump": relative,
            }

    report["finished_local"] = datetime.now().astimezone().isoformat()
    report_path = out / "report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
    print("\nRead-only collection completed. The Service session has ended and the camera has left 0336.", flush=True)
    print(f"Report: {report_path}")
    print(f"Data directory: {out}")
    print("Read data does not imply that the corresponding values are safe to write.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

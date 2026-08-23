import subprocess
import sys
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests


def download_if_not_present(url: str, filename: str):
    file = Path(filename)
    if not file.exists():
        print(f"Downloading {url}")

        with requests.get(url, stream=True) as response:
            response.raise_for_status()

            total = int(response.headers.get("content-length", 0))
            downloaded = 0
            start = time.monotonic()

            with file.open("wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        elapsed = time.monotonic() - start
                        speed = downloaded / elapsed if elapsed else 0

                        if total:
                            percent = downloaded / total * 100
                            eta = (total - downloaded) / speed if speed else 0

                            sys.stdout.write(
                                f"\r{percent:6.2f}% | "
                                f"{downloaded / 1024**2:.1f}/{total / 1024**2:.1f} MB | "
                                f"{speed / 1024**2:.1f} MB/s | "
                                f"ETA {eta:.0f}s"
                            )
                        else:
                            sys.stdout.write(
                                f"\r{downloaded / 1024**2:.1f} MB | "
                                f"{speed / 1024**2:.1f} MB/s"
                            )

                        sys.stdout.flush()

        print(f"\nFinished downloading {url}")

def download_generic(url: str, filename: str):
    file = Path(filename)
    print(f"Downloading {url}")

    with requests.get(url, stream=True) as response:
        response.raise_for_status()

        total = int(response.headers.get("content-length", 0))
        downloaded = 0
        start = time.monotonic()

        with file.open("wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    elapsed = time.monotonic() - start
                    speed = downloaded / elapsed if elapsed else 0

                    if total:
                        percent = downloaded / total * 100
                        eta = (total - downloaded) / speed if speed else 0

                        sys.stdout.write(
                            f"\r{percent:6.2f}% | "
                            f"{downloaded / 1024**2:.1f}/{total / 1024**2:.1f} MB | "
                            f"{speed / 1024**2:.1f} MB/s | "
                            f"ETA {eta:.0f}s"
                        )
                    else:
                        sys.stdout.write(
                            f"\r{downloaded / 1024**2:.1f} MB | "
                            f"{speed / 1024**2:.1f} MB/s"
                        )

                    sys.stdout.flush()

    print(f"\nFinished downloading {url}")

def extract_archive(file: Path, out_dir: str):
    with zipfile.ZipFile(file) as z:
        print(f"Extracting {file}")
        total: int = len(z.infolist())
        for num, info in enumerate(z.infolist(), start=1):
            path = Path(info.filename)

            # Skip the inner folder itself
            if len(path.parts) < 2:
                continue

            # Remove the first directory component
            relative_path = Path(*path.parts[1:])
            destination = out_dir / relative_path

            if info.is_dir():
                destination.mkdir(parents=True, exist_ok=True)
            else:
                destination.parent.mkdir(parents=True, exist_ok=True)
                with z.open(info) as src, open(destination, "wb") as dst:
                    while chunk := src.read(1024 * 1024):
                        dst.write(chunk)

                sys.stdout.write(f"\r{num}/{total} files extracted")
                sys.stdout.flush()

        print(f"\nExtracted {file}")

def convert_wmv_file(wmv_file):
    mp4_file = wmv_file.with_suffix(".mp4")

    subprocess.run([
        "ffmpeg",
        "-i", str(wmv_file),
        "-c:v", "libx264",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "192k",
        "-y",
        str(mp4_file)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    wmv_file.unlink()


def convert_wmv_directory(directory, workers=4):
    directory = Path(directory)
    wmv_files = list(directory.glob("*.wmv"))
    total = len(wmv_files)

    if not wmv_files:
        sys.stdout.write("No WMV files found.\n")
        sys.stdout.flush()
        return

    completed = 0

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(convert_wmv_file, wmv_file): wmv_file
            for wmv_file in wmv_files
        }

        for future in as_completed(futures):
            wmv_file = futures[future]
            completed += 1

            try:
                future.result()
                message = f"\r{completed}/{total} processed"
            except TimeoutError as e:
                print(f"{completed}/{total} FAILED: {wmv_file.name} — {e}")

            sys.stdout.write(message)
            sys.stdout.flush()

    sys.stdout.write("\n")
    sys.stdout.flush()
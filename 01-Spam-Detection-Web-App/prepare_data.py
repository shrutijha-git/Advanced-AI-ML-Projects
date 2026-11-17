
from pathlib import Path
from urllib.request import urlopen
import csv
import io
import zipfile

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_PATH = DATA_DIR / "spam.csv"

DATASET_URL = (
    "https://archive.ics.uci.edu/static/public/228/"
    "sms+spam+collection.zip"
)


def prepare_data():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if DATA_PATH.exists():
        print("Dataset already exists:", DATA_PATH)
        return

    print("Downloading the UCI SMS Spam Collection...")

    with urlopen(DATASET_URL, timeout=60) as response:
        archive_bytes = response.read()

    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        # Some dataset distributions contain a nested ZIP.
        if "SMSSpamCollection" in archive.namelist():
            raw_data = archive.read("SMSSpamCollection")
        else:
            nested_names = [
                name for name in archive.namelist()
                if name.lower().endswith(".zip")
            ]

            if not nested_names:
                raise FileNotFoundError(
                    "SMSSpamCollection not found in dataset archive."
                )

            with zipfile.ZipFile(
                io.BytesIO(archive.read(nested_names[0]))
            ) as nested:
                raw_data = nested.read("SMSSpamCollection")

    lines = raw_data.decode("utf-8-sig").splitlines()

    with DATA_PATH.open(
        "w", newline="", encoding="utf-8"
    ) as output:
        writer = csv.writer(output)
        writer.writerow(["label", "message"])

        count = 0

        for line in lines:
            if not line.strip():
                continue

            label, message = line.split("\t", 1)
            writer.writerow([label, message])
            count += 1

    print(f"Dataset prepared: {count} messages")
    print("Saved to:", DATA_PATH)


if __name__ == "__main__":
    prepare_data()

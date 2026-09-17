from pathlib import Path
from bs4 import BeautifulSoup


def parse_clinical_record(record):
    file_path = Path(__file__).parent / "patients" / record

    with open(file_path, "r", encoding="utf-8") as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, "html.parser")

    return soup.get_text(separator=" ", strip=True)


def parse_all_patients():
    patients_folder = Path(__file__).parent / "patients"

    records = {}

    for file_path in sorted(patients_folder.glob("*.html")):
        patient_id = file_path.stem

        records[patient_id] = parse_clinical_record(file_path.name)

    return records


if __name__ == "__main__":
    records = parse_all_patients()

    print("Patients processed:", len(records))

    for patient_id, text in records.items():
        print("\n" + "=" * 60)
        print(patient_id)
        print("=" * 60)
        print(text)
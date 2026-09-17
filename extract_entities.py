from bs4 import BeautifulSoup
import os
import pandas as pd

INPUT_FOLDER = "patients"

all_entities = []

# Read all HTML patient files
for filename in sorted(os.listdir(INPUT_FOLDER)):

    if not filename.endswith(".html"):
        continue

    patient_id = filename.replace(".html", "")

    filepath = os.path.join(INPUT_FOLDER, filename)

    # Read HTML
    with open(filepath, "r", encoding="utf-8") as file:
        html = file.read()

    # DOM parsing
    soup = BeautifulSoup(html, "html.parser")

    # Extract all <p> elements
    paragraphs = soup.find_all("p")

    for paragraph in paragraphs:

        text = paragraph.get_text(" ", strip=True)

        if ":" not in text:
            continue

        label, value = text.split(":", 1)

        label = label.strip()
        value = value.strip()

        # Determine semantic entity type
        if label == "Patient ID":
            entity_type = "Patient"

        elif label == "Age":
            entity_type = "Age"

        elif label == "Gender":
            entity_type = "Gender"

        elif label == "Race":
            entity_type = "Demographic"

        elif label == "Diagnosis":
            entity_type = "Disease"

        elif label == "Medications":
            entity_type = "Medication"

        elif label == "Diabetes Medication":
            entity_type = "Medication Status"

        elif label == "Time in Hospital":
            entity_type = "Hospitalization"

        elif label == "Number of Diagnoses":
            entity_type = "Clinical Information"

        elif label == "Readmission":
            entity_type = "Outcome"

        else:
            entity_type = "Clinical Entity"

        all_entities.append({
            "Patient ID": patient_id,
            "Entity": value,
            "Entity Type": entity_type,
            "Source Field": label
        })


# Convert to DataFrame
df = pd.DataFrame(all_entities)

# Save extraction result
df.to_csv("entity_extraction_results.csv", index=False)

print("\n====================================")
print("DOM ENTITY EXTRACTION COMPLETE")
print("====================================")

print("Patients processed:", df["Patient ID"].nunique())
print("Entities extracted:", len(df))

print("\nEntity Type Summary:")
print(df["Entity Type"].value_counts())

print("\nFirst 20 extracted entities:")
print(df.head(20).to_string(index=False))
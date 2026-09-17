import pandas as pd
import os

df = pd.read_csv("diabetic_data.csv")
df = df.head(100)

os.makedirs("patients", exist_ok=True)

for index, row in df.iterrows():

    patient_id = f"P{index + 1:03d}"

    diagnosis = str(row["diag_1"])

    medications = []

    medication_columns = [
        "metformin",
        "repaglinide",
        "nateglinide",
        "chlorpropamide",
        "glimepiride",
        "glipizide",
        "glyburide",
        "pioglitazone",
        "rosiglitazone",
        "acarbose",
        "insulin"
    ]

    for med in medication_columns:
        value = str(row[med])

        if value not in ["No", "nan", "?"]:
            medications.append(f"{med}: {value}")

    medication_text = ", ".join(medications)

    if not medication_text:
        medication_text = "No medication information"

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Clinical Record - {patient_id}</title>
</head>
<body>

    <h1>Clinical Record</h1>

    <p><b>Patient ID:</b> {patient_id}</p>
    <p><b>Age:</b> {row["age"]}</p>
    <p><b>Gender:</b> {row["gender"]}</p>
    <p><b>Race:</b> {row["race"]}</p>
    <p><b>Diagnosis:</b> {diagnosis}</p>
    <p><b>Time in Hospital:</b> {row["time_in_hospital"]} days</p>
    <p><b>Number of Diagnoses:</b> {row["number_diagnoses"]}</p>
    <p><b>Medications:</b> {medication_text}</p>
    <p><b>Diabetes Medication:</b> {row["diabetesMed"]}</p>
    <p><b>Readmission:</b> {row["readmitted"]}</p>

</body>
</html>
"""

    filename = f"patients/{patient_id}.html"

    with open(filename, "w", encoding="utf-8") as file:
        file.write(html)

print("Successfully created 100 patient HTML records.")
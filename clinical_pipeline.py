from pathlib import Path
import os
import re

import pandas as pd
import spacy
from bs4 import BeautifulSoup
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).parent

INPUT_CSV = BASE_DIR / "diabetic_data.csv"
PATIENTS_DIR = BASE_DIR / "patients"
OUTPUT_DIR = BASE_DIR / "output"

PATIENTS_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)


# ============================================================
# NAMESPACES
# ============================================================

EX = Namespace("http://example.org/diabetes/")
PATIENT = Namespace("http://example.org/diabetes/patient/")
ENCOUNTER = Namespace("http://example.org/diabetes/encounter/")


# ============================================================
# 1. CREATE 100 PATIENT HTML RECORDS
# ============================================================

def generate_patient_html():

    print("\n[1/7] Creating 100 patient HTML records...")

    df = pd.read_csv(INPUT_CSV)

    patients = df.head(100).copy()

    # Save selected 100 records
    patients.to_csv(
        OUTPUT_DIR / "100_patients.csv",
        index=False
    )

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

    for index, row in patients.iterrows():

        patient_id = f"P{index + 1:03d}"

        diagnosis = str(row["diag_1"])

        medications = []

        for med in medication_columns:

            value = str(row[med])

            if value not in ["No", "nan", "?"]:
                medications.append(
                    f"{med}: {value}"
                )

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

        filename = PATIENTS_DIR / f"{patient_id}.html"

        with open(filename, "w", encoding="utf-8") as file:
            file.write(html)

    print(f"Created {len(patients)} patient HTML files.")

    return patients


# ============================================================
# 2. PARSE ALL 100 HTML RECORDS
# ============================================================

def parse_all_patients():

    print("\n[2/7] Parsing all patient HTML records...")

    records = {}

    output_file = OUTPUT_DIR / "all_patients.txt"

    patient_files = sorted(
        PATIENTS_DIR.glob("*.html")
    )

    with open(output_file, "w", encoding="utf-8") as output:

        for file_path in patient_files:

            patient_id = file_path.stem

            with open(
                file_path,
                "r",
                encoding="utf-8"
            ) as file:

                html = file.read()

            soup = BeautifulSoup(
                html,
                "html.parser"
            )

            text = soup.get_text(
                separator=" ",
                strip=True
            )

            records[patient_id] = text

            output.write("=" * 70 + "\n")
            output.write(f"PATIENT: {patient_id}\n")
            output.write("=" * 70 + "\n")
            output.write(text)
            output.write("\n\n")

    print(f"Parsed {len(records)} patients.")
    print(f"Saved: {output_file}")

    return records


# ============================================================
# 3. EXTRACT CLINICAL ENTITIES FROM HTML
# ============================================================

def extract_dom_entities():

    print("\n[3/7] Extracting clinical entities...")

    all_entities = []

    patient_files = sorted(
        PATIENTS_DIR.glob("*.html")
    )

    for file_path in patient_files:

        patient_id = file_path.stem

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            html = file.read()

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        paragraphs = soup.find_all("p")

        for paragraph in paragraphs:

            text = paragraph.get_text(
                " ",
                strip=True
            )

            if ":" not in text:
                continue

            label, value = text.split(
                ":",
                1
            )

            label = label.strip()
            value = value.strip()

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

    df = pd.DataFrame(all_entities)

    output_file = OUTPUT_DIR / "entity_extraction_results.csv"

    df.to_csv(
        output_file,
        index=False
    )

    print(f"Patients processed: {df['Patient ID'].nunique()}")
    print(f"Entities extracted: {len(df)}")
    print(f"Saved: {output_file}")

    return df


# ============================================================
# 4. NLP ENTITY EXTRACTION
# ============================================================

def extract_nlp_entities(records):

    print("\n[4/7] Running NLP entity extraction...")

    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        print(
            "spaCy model not found."
        )
        print(
            "Run: python -m spacy download en_core_web_sm"
        )
        return []

    entities = []

    clinical_terms = [
        ("Type 2 Diabetes", "DISEASE"),
        ("Metformin", "MEDICATION"),
        ("Increased thirst", "SYMPTOM")
    ]

    for patient_id, text in records.items():

        doc = nlp(text)

        found = set()

        # spaCy entities
        for ent in doc.ents:

            key = (
                patient_id,
                ent.text.lower()
            )

            if key not in found:

                entities.append({
                    "Patient ID": patient_id,
                    "Text": ent.text,
                    "Label": ent.label_,
                    "Source": "spaCy"
                })

                found.add(key)

        # Known clinical terms
        for term, label in clinical_terms:

            if term.lower() in text.lower():

                key = (
                    patient_id,
                    term.lower()
                )

                if key not in found:

                    entities.append({
                        "Patient ID": patient_id,
                        "Text": term,
                        "Label": label,
                        "Source": "Clinical Dictionary"
                    })

                    found.add(key)

    print(
        f"NLP entities found: {len(entities)}"
    )

    return entities


# ============================================================
# 5. ONTOLOGY MAPPING
# ============================================================

ONTOLOGY = {

    "Type 2 Diabetes": {
        "type": "Disease",
        "uri": "http://example.org/ontology/Type2Diabetes"
    },

    "Metformin": {
        "type": "Medication",
        "uri": "http://example.org/ontology/Metformin"
    },

    "Increased thirst": {
        "type": "Symptom",
        "uri": "http://example.org/ontology/IncreasedThirst"
    }
}


def map_to_ontology(entities):

    print("\n[5/7] Mapping entities to ontology...")

    mapped = []

    for entity in entities:

        text = entity["Text"]

        if text in ONTOLOGY:

            concept = ONTOLOGY[text]

            mapped.append({
                "Patient ID": entity["Patient ID"],
                "Text": text,
                "Type": concept["type"],
                "URI": concept["uri"]
            })

    print(
        f"Ontology mappings: {len(mapped)}"
    )

    return mapped


# ============================================================
# 6. CREATE RDF GRAPH
# ============================================================

def clean_name(name):

    name = str(name).strip()

    name = re.sub(
        r"[^A-Za-z0-9_]",
        "_",
        name
    )

    return name


def create_rdf(df):

    print("\n[6/7] Creating RDF knowledge graph...")

    g = Graph()

    g.bind("ex", EX)
    g.bind("patient", PATIENT)
    g.bind("encounter", ENCOUNTER)

    special_columns = {
        "encounter_id",
        "patient_nbr"
    }

    for index, row in df.iterrows():

        patient_id = f"P{index + 1:03d}"

        patient_uri = PATIENT[patient_id]

        encounter_id = str(
            row["encounter_id"]
        )

        encounter_uri = ENCOUNTER[
            encounter_id
        ]

        # Patient
        g.add((
            patient_uri,
            RDF.type,
            EX.Patient
        ))

        # Encounter
        g.add((
            encounter_uri,
            RDF.type,
            EX.Encounter
        ))

        # Patient -> Encounter
        g.add((
            patient_uri,
            EX.hasEncounter,
            encounter_uri
        ))

        # Add all other columns
        for column in df.columns:

            if column in special_columns:
                continue

            value = row[column]

            if pd.isna(value):
                continue

            value = str(value).strip()

            if value in ["", "?"]:
                continue

            predicate = EX[
                clean_name(column)
            ]

            g.add((
                encounter_uri,
                predicate,
                Literal(value)
            ))

    output_file = OUTPUT_DIR / "100_patients.rdf"

    g.serialize(
        destination=output_file,
        format="xml"
    )

    print(f"RDF triples: {len(g)}")
    print(f"Saved: {output_file}")

    return g


# ============================================================
# 7. SPARQL QUERIES
# ============================================================

def query_patient_encounters(graph, patient_id):

    query = f"""
    PREFIX ex: <http://example.org/diabetes/>
    PREFIX patient: <http://example.org/diabetes/patient/>

    SELECT ?encounter
    WHERE {{
        patient:{patient_id}
            ex:hasEncounter
            ?encounter .
    }}
    """

    results = graph.query(query)

    return [
        str(row.encounter)
        for row in results
    ]


def query_patient_data(graph, patient_id):

    query = f"""
    PREFIX ex: <http://example.org/diabetes/>
    PREFIX patient: <http://example.org/diabetes/patient/>

    SELECT ?property ?value
    WHERE {{
        patient:{patient_id}
            ex:hasEncounter
            ?encounter .

        ?encounter
            ?property
            ?value .
    }}
    """

    results = graph.query(query)

    return [
        (
            str(row.property),
            str(row.value)
        )
        for row in results
    ]


def run_queries(graph):

    print("\n[7/7] Running SPARQL queries...")

    patient_id = "P001"

    encounters = query_patient_encounters(
        graph,
        patient_id
    )

    print(f"\nPatient: {patient_id}")

    print("\nEncounters:")

    for encounter in encounters:
        print(encounter)

    data = query_patient_data(
        graph,
        patient_id
    )

    print("\nPatient clinical data:")

    for property_name, value in data:
        print(
            f"{property_name} -> {value}"
        )


# ============================================================
# MAIN PIPELINE
# ============================================================

def main():

    print("=" * 70)
    print("CLINICAL SEMANTIC PROCESSING PIPELINE")
    print("=" * 70)

    # Step 1
    patients_df = generate_patient_html()

    # Step 2
    records = parse_all_patients()

    # Step 3
    entity_df = extract_dom_entities()

    # Step 4
    nlp_entities = extract_nlp_entities(
        records
    )

    # Step 5
    mapped_entities = map_to_ontology(
        nlp_entities
    )

    # Step 6
    graph = create_rdf(
        patients_df
    )

    # Step 7
    run_queries(graph)

    print("\n" + "=" * 70)
    print("PIPELINE COMPLETE")
    print("=" * 70)

    print(f"Patients: {len(patients_df)}")
    print(f"HTML records: {len(records)}")
    print(f"DOM entities: {len(entity_df)}")
    print(f"NLP entities: {len(nlp_entities)}")
    print(f"Ontology mappings: {len(mapped_entities)}")
    print(f"RDF triples: {len(graph)}")


if __name__ == "__main__":
    main()
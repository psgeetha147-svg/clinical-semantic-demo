import pandas as pd
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, XSD
import re

# --------------------------------------------------
# 1. Read your CSV
# --------------------------------------------------

df = pd.read_csv("100_patients.csv")

# --------------------------------------------------
# 2. Create RDF graph and namespaces
# --------------------------------------------------

g = Graph()

EX = Namespace("http://example.org/diabetes/")
PATIENT = Namespace("http://example.org/diabetes/patient/")
ENCOUNTER = Namespace("http://example.org/diabetes/encounter/")

g.bind("ex", EX)
g.bind("patient", PATIENT)
g.bind("encounter", ENCOUNTER)

# --------------------------------------------------
# 3. Function to make valid RDF property names
# --------------------------------------------------

def clean_name(name):
    name = str(name).strip()
    name = re.sub(r"[^A-Za-z0-9_]", "_", name)
    return name

# --------------------------------------------------
# 4. Columns that identify resources
# --------------------------------------------------

special_columns = {
    "encounter_id",
    "patient_nbr"
}

# --------------------------------------------------
# 5. Convert every row to RDF
# --------------------------------------------------

for _, row in df.iterrows():

    encounter_id = str(row["encounter_id"])
    patient_id = str(row["patient_nbr"])

    # Patient URI
    patient_uri = PATIENT[patient_id]

    # Encounter URI
    encounter_uri = ENCOUNTER[encounter_id]

    # ------------------------------------------------
    # Patient
    # ------------------------------------------------

    g.add((
        patient_uri,
        RDF.type,
        EX.Patient
    ))

    # ------------------------------------------------
    # Encounter
    # ------------------------------------------------

    g.add((
        encounter_uri,
        RDF.type,
        EX.Encounter
    ))

    # Connect patient -> encounter
    g.add((
        patient_uri,
        EX.hasEncounter,
        encounter_uri
    ))

    # ------------------------------------------------
    # Add all remaining columns
    # ------------------------------------------------

    for column in df.columns:

        if column in special_columns:
            continue

        value = row[column]

        # Missing value
        if pd.isna(value) or str(value).strip() in ["?", ""]:
            continue

        # Clean column name
        property_name = clean_name(column)

        predicate = EX[property_name]

        # Remove the ** markers that appear in your pasted data
        value = str(value).replace("**", "").strip()

        # Add literal
        g.add((
            encounter_uri,
            predicate,
            Literal(value)
        ))

# --------------------------------------------------
# 6. Save RDF
# --------------------------------------------------

g.serialize(
    destination="100_patients.rdf",
    format="xml"
)

print("Rows:", len(df))
print("RDF triples:", len(g))
print("Saved: 100_patients.rdf")
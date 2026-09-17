import streamlit as st
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup
from rdflib import Graph, Namespace, RDF


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Clinical Semantic Dashboard",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# MEDICAL DASHBOARD STYLE
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background: linear-gradient(
            135deg,
            #E8F8F5 0%,
            #F4FBFF 45%,
            #EEF7FF 100%
        );
    }

    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(
            180deg,
            #063970 0%,
            #075985 50%,
            #0E7490 100%
        );
    }

    section[data-testid="stSidebar"] * {
        color: white !important;
    }

    section[data-testid="stSidebar"]
    div[role="radiogroup"] label {
        background-color: rgba(255,255,255,0.10);
        border-radius: 10px;
        padding: 8px 12px;
        margin-bottom: 6px;
    }

    section[data-testid="stSidebar"]
    div[role="radiogroup"] label:hover {
        background-color: rgba(255,255,255,0.20);
    }

    div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.92);
        border-radius: 16px;
        padding: 18px;
        border: 1px solid #D5EAF2;
        box-shadow: 0 5px 15px rgba(0,80,120,0.10);
    }

    div[data-testid="stMetric"] label {
        color: #176B87 !important;
        font-weight: 700 !important;
    }

    div[data-testid="stMetricValue"] {
        color: #063970 !important;
        font-weight: 800 !important;
    }

    h1 {
        color: #063970 !important;
        font-weight: 800 !important;
    }

    h2 {
        color: #075985 !important;
        font-weight: 750 !important;
    }

    h3 {
        color: #0E7490 !important;
        font-weight: 700 !important;
    }

    div[data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #CDE7EF;
        box-shadow: 0 4px 12px rgba(0,80,120,0.08);
    }

    textarea {
        border-radius: 12px !important;
        border: 1px solid #B7DDE8 !important;
    }

    .stButton > button {
        border-radius: 10px;
        border: none;
        background-color: #0E7490;
        color: white;
        font-weight: 700;
    }

    .stButton > button:hover {
        background-color: #075985;
        color: white;
    }

    div[data-testid="stCodeBlock"] {
        border-radius: 12px;
    }

    div[data-testid="stAlert"] {
        border-radius: 12px;
    }

    hr {
        border-color: #B9DDE7;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).parent

CSV_FILE = BASE_DIR / "output" / "100_patients.csv"
ENTITY_FILE = BASE_DIR / "output" / "entity_extraction_results.csv"
RDF_FILE = BASE_DIR / "output" / "100_patients.rdf"
PATIENT_FOLDER = BASE_DIR / "patients"


# ============================================================
# RDF NAMESPACES
# ============================================================

EX = Namespace(
    "http://example.org/diabetes/"
)

PATIENT = Namespace(
    "http://example.org/diabetes/patient/"
)

ENCOUNTER = Namespace(
    "http://example.org/diabetes/encounter/"
)


# ============================================================
# LOAD PATIENT DATA
# ============================================================

@st.cache_data
def load_patient_data():

    if not CSV_FILE.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(CSV_FILE)

    except Exception:
        return pd.DataFrame()


# ============================================================
# LOAD ENTITY DATA
# ============================================================

@st.cache_data
def load_entity_data():

    if not ENTITY_FILE.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(ENTITY_FILE)

    except Exception:
        return pd.DataFrame()


# ============================================================
# LOAD RDF GRAPH
# ============================================================

@st.cache_resource
def load_rdf_graph():

    graph = Graph()

    if not RDF_FILE.exists():
        return graph

    try:

        graph.parse(
            RDF_FILE,
            format="xml"
        )

    except Exception:

        return Graph()

    return graph


df = load_patient_data()

entity_df = load_entity_data()

graph = load_rdf_graph()


# ============================================================
# HELPER: PARSE HTML
# ============================================================

def parse_html(patient_id):

    file_path = (
        PATIENT_FOLDER /
        f"{patient_id}.html"
    )

    if not file_path.exists():

        return "", ""

    try:

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            html = file.read()

    except Exception:

        return "", ""

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    text = soup.get_text(
        separator=" ",
        strip=True
    )

    return text, html


# ============================================================
# HELPER: SHORT URI
# ============================================================

def short_uri(uri):

    text = str(uri)

    if "#" in text:

        return text.split("#")[-1]

    return text.rstrip("/").split("/")[-1]


# ============================================================
# HELPER: GRAPHVIZ ESCAPE
# ============================================================

def escape_graphviz_text(value):

    value = str(value)

    value = value.replace(
        "\\",
        "\\\\"
    )

    value = value.replace(
        '"',
        '\\"'
    )

    value = value.replace(
        "\n",
        " "
    )

    return value


# ============================================================
# HELPER: PATIENT ID
# ============================================================

def get_patient_id(index):

    return f"P{index + 1:03d}"


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title(
    "🩺 Clinical Semantic"
)

st.sidebar.write(
    "Diabetes Patient Knowledge System"
)

st.sidebar.divider()

page = st.sidebar.radio(
    "Navigate to",
    [
        "🏠 Dashboard",
        "📊 Patient Dataset",
        "🌐 HTML Parser",
        "🧠 NLP Entities",
        "🔗 Ontology Mapping",
        "🕸️ RDF Knowledge Graph",
        "🔎 SPARQL Queries"
    ]
)

st.sidebar.divider()

st.sidebar.subheader(
    "Semantic Pipeline"
)

st.sidebar.write("📊 Patient Data")
st.sidebar.write("↓")
st.sidebar.write("🌐 HTML Parser")
st.sidebar.write("↓")
st.sidebar.write("🧠 NLP")
st.sidebar.write("↓")
st.sidebar.write("🔗 Ontology")
st.sidebar.write("↓")
st.sidebar.write("🕸️ RDF")
st.sidebar.write("↓")
st.sidebar.write("🔎 SPARQL")

st.sidebar.divider()

st.sidebar.caption(
    "Clinical Semantic Demo"
)


# ============================================================
# DASHBOARD
# ============================================================

if page == "🏠 Dashboard":

    st.title(
        "🩺 Clinical Semantic Dashboard"
    )

    st.write(
        "A semantic processing dashboard "
        "for diabetes patient records."
    )

    st.write(
        "Patient Data → HTML → NLP → Ontology → RDF → SPARQL"
    )

    st.divider()

    total_patients = len(df)

    total_columns = (
        len(df.columns)
        if not df.empty
        else 0
    )

    total_entities = len(entity_df)

    total_triples = len(graph)

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "👤 Patients",
            total_patients
        )

    with col2:

        st.metric(
            "📊 Data Columns",
            total_columns
        )

    with col3:

        st.metric(
            "🧠 NLP Entities",
            total_entities
        )

    with col4:

        st.metric(
            "🕸️ RDF Triples",
            total_triples
        )

    st.divider()

    st.header(
        "🔄 Semantic Processing Pipeline"
    )

    pipeline = [

        (
            "1. 📊 Patient Dataset",
            "Loads the selected 100 diabetes patient records."
        ),

        (
            "2. 🌐 HTML Parser",
            "Reads patient HTML files and converts them into clean text."
        ),

        (
            "3. 🧠 NLP Entity Extraction",
            "Identifies clinical entities from patient information."
        ),

        (
            "4. 🔗 Ontology Mapping",
            "Connects clinical terms with ontology concepts."
        ),

        (
            "5. 🕸️ RDF Knowledge Graph",
            "Stores patients, encounters and clinical attributes as RDF."
        ),

        (
            "6. 🔎 SPARQL",
            "Queries the semantic knowledge graph."
        )
    ]

    for title, description in pipeline:

        st.subheader(title)

        st.write(description)

        st.divider()

    st.header(
        "🧭 Semantic Journey"
    )

    flow_cols = st.columns(6)

    flow_items = [

        ("📊", "Patient Data"),

        ("🌐", "HTML Parser"),

        ("🧠", "NLP"),

        ("🔗", "Ontology"),

        ("🕸️", "RDF"),

        ("🔎", "SPARQL")
    ]

    for col, (icon, name) in zip(
        flow_cols,
        flow_items
    ):

        with col:

            st.write(icon)

            st.write(name)

    st.divider()

    st.header(
        "📋 Patient Data Preview"
    )

    if not df.empty:

        st.dataframe(
            df.head(10),
            width="stretch",
            hide_index=True
        )

    else:

        st.warning(
            "output/100_patients.csv was not found."
        )


# ============================================================
# PATIENT DATASET
# ============================================================

elif page == "📊 Patient Dataset":

    st.title(
        "📊 Patient Dataset"
    )

    st.write(
        "Explore the 100 selected diabetes patient records."
    )

    if df.empty:

        st.error(
            "Could not find output/100_patients.csv."
        )

    else:

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "👤 Patients",
                len(df)
            )

        with col2:

            st.metric(
                "📊 Columns",
                len(df.columns)
            )

        with col3:

            st.metric(
                "🔢 Data Values",
                df.size
            )

        st.divider()

        st.subheader(
            "Complete Patient Dataset"
        )

        st.dataframe(
            df,
            width="stretch",
            hide_index=True
        )

        st.divider()

        st.subheader(
            "👤 Individual Patient"
        )

        selected_number = st.number_input(
            "Select patient number",
            min_value=1,
            max_value=len(df),
            value=1
        )

        row = df.iloc[
            selected_number - 1
        ]

        patient_id = get_patient_id(
            selected_number - 1
        )

        st.write(
            f"Selected Patient: {patient_id}"
        )

        patient_table = pd.DataFrame(
            {
                "Field": row.index,
                "Value": row.values
            }
        )

        st.dataframe(
            patient_table,
            width="stretch",
            hide_index=True
        )


# ============================================================
# HTML PARSER
# ============================================================

elif page == "🌐 HTML Parser":

    st.title(
        "🌐 HTML Parser"
    )

    st.write(
        "The HTML parser converts patient HTML documents "
        "into clean readable clinical text."
    )

    st.divider()

    if not PATIENT_FOLDER.exists():

        st.error(
            "The patients folder was not found."
        )

    else:

        patient_files = sorted(
            PATIENT_FOLDER.glob("P*.html")
        )

        st.metric(
            "🌐 Patient HTML Files",
            len(patient_files)
        )

        st.divider()

        if patient_files:

            selected_file = st.selectbox(
                "Select Patient",
                patient_files,
                format_func=lambda x: x.stem
            )

            patient_id = selected_file.stem

            clean_text, html_source = parse_html(
                patient_id
            )

            st.subheader(
                f"Parsed Record: {patient_id}"
            )

            if clean_text:

                st.text_area(
                    "Clean Patient Text",
                    clean_text,
                    height=350
                )

            else:

                st.warning(
                    "No readable text was extracted."
                )

            st.divider()

            st.subheader(
                "How the Parser Works"
            )

            st.write(
                "1. Opens the patient HTML file."
            )

            st.write(
                "2. Reads the HTML structure using BeautifulSoup."
            )

            st.write(
                "3. Removes HTML tags."
            )

            st.write(
                "4. Produces clean text for NLP processing."
            )

        else:

            st.warning(
                "No patient HTML files were found."
            )


# ============================================================
# NLP ENTITIES
# ============================================================

elif page == "🧠 NLP Entities":

    st.title(
        "🧠 NLP Entity Extraction"
    )

    st.write(
        "Clinical entities extracted from the patient records."
    )

    if entity_df.empty:

        st.warning(
            "No entity extraction results were found."
        )

    else:

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "🧠 Total Entities",
                len(entity_df)
            )

        with col2:

            if "label" in entity_df.columns:

                st.metric(
                    "🏷️ Entity Types",
                    entity_df["label"].nunique()
                )

            else:

                st.metric(
                    "🏷️ Entity Types",
                    0
                )

        st.divider()

        st.subheader(
            "Extracted Clinical Entities"
        )

        st.dataframe(
            entity_df,
            width="stretch",
            hide_index=True
        )

        st.divider()

        if "label" in entity_df.columns:

            st.subheader(
                "📊 Entity Type Distribution"
            )

            entity_counts = (
                entity_df["label"]
                .value_counts()
            )

            st.bar_chart(
                entity_counts,
                width="stretch"
            )

        st.divider()

        st.subheader(
            "👤 Patient Entity View"
        )

        patient_number = st.number_input(
            "Select Patient",
            min_value=1,
            max_value=100,
            value=1
        )

        selected_patient = (
            f"P{patient_number:03d}"
        )

        possible_columns = [
            "patient_id",
            "Patient ID",
            "patient",
            "Patient"
        ]

        patient_column = None

        for column in possible_columns:

            if column in entity_df.columns:

                patient_column = column

                break

        if patient_column:

            patient_entities = entity_df[
                entity_df[
                    patient_column
                ].astype(str)
                == selected_patient
            ]

        else:

            patient_entities = entity_df.head(0)

        if not patient_entities.empty:

            st.write(
                f"Entities found for {selected_patient}"
            )

            st.dataframe(
                patient_entities,
                width="stretch",
                hide_index=True
            )

        else:

            st.info(
                f"No entity records found for {selected_patient}."
            )


# ============================================================
# ONTOLOGY MAPPING
# ============================================================

elif page == "🔗 Ontology Mapping":

    st.title(
        "🔗 Ontology Mapping"
    )

    st.write(
        "Clinical terms are connected to standardized ontology concepts."
    )

    st.divider()

    ontology = {

        "Type 2 Diabetes": {

            "type": "Disease",

            "uri":
            "http://example.org/ontology/Type2Diabetes"
        },

        "Metformin": {

            "type": "Medication",

            "uri":
            "http://example.org/ontology/Metformin"
        },

        "Increased thirst": {

            "type": "Symptom",

            "uri":
            "http://example.org/ontology/IncreasedThirst"
        }
    }

    st.subheader(
        "📚 Available Ontology Concepts"
    )

    ontology_rows = []

    for concept, data in ontology.items():

        ontology_rows.append(
            {
                "Clinical Term": concept,

                "Concept Type": data["type"],

                "Ontology URI": data["uri"]
            }
        )

    ontology_table = pd.DataFrame(
        ontology_rows
    )

    st.dataframe(
        ontology_table,
        width="stretch",
        hide_index=True
    )

    st.divider()

    st.subheader(
        "🔗 Concept Mapping"
    )

    for concept, data in ontology.items():

        st.write(
            f"Clinical Term: {concept}"
        )

        st.write(
            f"Concept Type: {data['type']}"
        )

        st.code(
            data["uri"]
        )

        st.divider()

    st.subheader(
        "ℹ️ Dataset Mapping Note"
    )

    st.info(
        "The diabetic_data.csv dataset commonly stores "
        "diagnoses as ICD-9 codes such as 250.xx. "
        "Exact matching with terms such as 'Type 2 Diabetes' "
        "requires an ICD-9-to-ontology mapping table."
    )


# ============================================================
# RDF KNOWLEDGE GRAPH
# ============================================================

elif page == "🕸️ RDF Knowledge Graph":

    st.title(
        "🕸️ RDF Knowledge Graph"
    )

    st.write(
        "Patients, encounters and clinical attributes "
        "are represented as RDF triples."
    )

    st.divider()

    patient_count = len(
        list(
            graph.subjects(
                RDF.type,
                EX.Patient
            )
        )
    )

    encounter_count = len(
        list(
            graph.subjects(
                RDF.type,
                EX.Encounter
            )
        )
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "🕸️ RDF Triples",
            len(graph)
        )

    with col2:

        st.metric(
            "👤 RDF Patients",
            patient_count
        )

    with col3:

        st.metric(
            "🏥 Encounters",
            encounter_count
        )

    st.divider()

    if len(graph) == 0:

        st.warning(
            "The RDF graph is empty. "
            "Check output/100_patients.rdf."
        )

    else:

        st.subheader(
            "👤 Select Patient"
        )

        patient_number = st.number_input(
            "Patient Number",
            min_value=1,
            max_value=100,
            value=1
        )

        selected_patient = (
            f"P{patient_number:03d}"
        )

        patient_uri = PATIENT[
            selected_patient
        ]

        st.write(
            f"Selected Patient: {selected_patient}"
        )

        st.code(
            str(patient_uri)
        )

        patient_triples = []

        for subject, predicate, obj in graph:

            if subject == patient_uri:

                patient_triples.append(
                    {
                        "Subject":
                        short_uri(subject),

                        "Predicate":
                        short_uri(predicate),

                        "Object":
                        short_uri(obj)
                    }
                )

        if patient_triples:

            st.subheader(
                "🔗 Patient Relationships"
            )

            st.dataframe(
                pd.DataFrame(
                    patient_triples
                ),
                width="stretch",
                hide_index=True
            )

        else:

            st.info(
                f"No direct triples found for {selected_patient}."
            )

        st.divider()

        # ----------------------------------------------------
        # GRAPHVIZ
        # ----------------------------------------------------

        st.subheader(
            "🕸️ Visual Knowledge Graph"
        )

        dot_lines = [

            "digraph ClinicalGraph {",

            "rankdir=LR;",

            'graph [bgcolor="transparent"];',

            'node [shape=box, style="rounded,filled"];'
        ]

        patient_node = "patient_node"

        dot_lines.append(

            f'{patient_node} '
            f'[label="{escape_graphviz_text(selected_patient)}", '
            f'fillcolor="#DFF6FF"];'
        )

        encounters = list(
            graph.objects(
                patient_uri,
                EX.hasEncounter
            )
        )

        for encounter_index, encounter_uri in enumerate(
            encounters
        ):

            encounter_node = (
                f"encounter_node_{encounter_index}"
            )

            encounter_label = short_uri(
                encounter_uri
            )

            dot_lines.append(

                f'{encounter_node} '
                f'[label="{escape_graphviz_text(encounter_label)}", '
                f'fillcolor="#E8F5E9"];'
            )

            dot_lines.append(

                f'{patient_node} -> '
                f'{encounter_node} '
                f'[label="hasEncounter"];'
            )

            property_index = 0

            for predicate, obj in graph.predicate_objects(
                encounter_uri
            ):

                if property_index >= 15:

                    break

                predicate_name = short_uri(
                    predicate
                )

                object_name = short_uri(
                    obj
                )

                property_node = (
                    f"property_node_"
                    f"{encounter_index}_"
                    f"{property_index}"
                )

                label = (
                    f"{predicate_name}: "
                    f"{object_name}"
                )

                dot_lines.append(

                    f'{property_node} '
                    f'[label="{escape_graphviz_text(label)}", '
                    f'fillcolor="#FFF8E1"];'
                )

                dot_lines.append(

                    f'{encounter_node} -> '
                    f'{property_node} '
                    f'[label="{escape_graphviz_text(predicate_name)}"];'
                )

                property_index += 1

        dot_lines.append(
            "}"
        )

        dot_graph = "\n".join(
            dot_lines
        )

        try:

            st.graphviz_chart(
                dot_graph,
                width="stretch"
            )

        except Exception as error:

            st.error(
                "Graphviz could not be displayed."
            )

            st.write(
                str(error)
            )

            st.info(
                "Check that the Graphviz package is installed."
            )

        st.divider()

        st.subheader(
            "📋 RDF Triple Explorer"
        )

        triple_rows = []

        for subject, predicate, obj in graph:

            triple_rows.append(
                {
                    "Subject":
                    short_uri(subject),

                    "Predicate":
                    short_uri(predicate),

                    "Object":
                    short_uri(obj)
                }
            )

        triple_df = pd.DataFrame(
            triple_rows
        )

        st.dataframe(
            triple_df.head(200),
            width="stretch",
            hide_index=True
        )


# ============================================================
# SPARQL
# ============================================================

elif page == "🔎 SPARQL Queries":

    st.title(
        "🔎 SPARQL Queries"
    )

    st.write(
        "Use SPARQL to retrieve information "
        "from the RDF knowledge graph."
    )

    st.divider()

    patient_number = st.number_input(
        "Select Patient",
        min_value=1,
        max_value=100,
        value=1
    )

    selected_patient = (
        f"P{patient_number:03d}"
    )

    patient_uri = PATIENT[
        selected_patient
    ]

    st.write(
        f"Selected Patient: {selected_patient}"
    )

    st.code(
        str(patient_uri)
    )

    st.divider()

    # --------------------------------------------------------
    # QUERY 1
    # --------------------------------------------------------

    st.subheader(
        "🔎 Query 1: Patient Encounter"
    )

    query_encounter = f"""
PREFIX ex: <http://example.org/diabetes/>
PREFIX patient: <http://example.org/diabetes/patient/>

SELECT ?encounter
WHERE {{
    patient:{selected_patient}
        ex:hasEncounter ?encounter .
}}
"""

    st.code(
        query_encounter,
        language="sparql"
    )

    try:

        results = graph.query(
            query_encounter
        )

        encounter_results = []

        for row in results:

            encounter_results.append(
                {
                    "Encounter":
                    short_uri(row.encounter)
                }
            )

        if encounter_results:

            st.dataframe(
                pd.DataFrame(
                    encounter_results
                ),
                width="stretch",
                hide_index=True
            )

        else:

            st.info(
                "No encounter was found."
            )

    except Exception as error:

        st.error(
            f"SPARQL error: {error}"
        )

    st.divider()

    # --------------------------------------------------------
    # QUERY 2
    # --------------------------------------------------------

    st.subheader(
        "🔎 Query 2: Patient Properties"
    )

    query_properties = f"""
PREFIX patient: <http://example.org/diabetes/patient/>

SELECT ?predicate ?object
WHERE {{
    patient:{selected_patient}
        ?predicate ?object .
}}
"""

    st.code(
        query_properties,
        language="sparql"
    )

    try:

        results = graph.query(
            query_properties
        )

        property_results = []

        for row in results:

            property_results.append(
                {
                    "Predicate":
                    short_uri(row.predicate),

                    "Object":
                    short_uri(row.object)
                }
            )

        if property_results:

            st.dataframe(
                pd.DataFrame(
                    property_results
                ),
                width="stretch",
                hide_index=True
            )

        else:

            st.info(
                "No patient properties were found."
            )

    except Exception as error:

        st.error(
            f"SPARQL error: {error}"
        )

    st.divider()

    # --------------------------------------------------------
    # QUERY 3
    # --------------------------------------------------------

    st.subheader(
        "🔎 Query 3: All Patients"
    )

    query_patients = """
PREFIX ex: <http://example.org/diabetes/>

SELECT ?patient
WHERE {
    ?patient a ex:Patient .
}
"""

    st.code(
        query_patients,
        language="sparql"
    )

    try:

        results = graph.query(
            query_patients
        )

        patient_results = []

        for row in results:

            patient_results.append(
                {
                    "Patient":
                    short_uri(row.patient)
                }
            )

        if patient_results:

            patient_result_df = pd.DataFrame(
                patient_results
            )

            st.metric(
                "👤 Patients Found",
                len(patient_result_df)
            )

            st.dataframe(
                patient_result_df,
                width="stretch",
                hide_index=True
            )

        else:

            st.info(
                "No patients were found."
            )

    except Exception as error:

        st.error(
            f"SPARQL error: {error}"
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🩺 Clinical Semantic Demo | "
    "Patient Data → HTML → NLP → Ontology → RDF → SPARQL"
)

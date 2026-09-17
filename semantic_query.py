from rdflib import Graph, Namespace

PATIENT = Namespace("http://example.org/diabetes/patient/")
EX = Namespace("http://example.org/diabetes/")


def query_patient_encounters(graph, patient_id):

    query = """
    PREFIX ex: <http://example.org/diabetes/>
    PREFIX patient: <http://example.org/diabetes/patient/>

    SELECT ?encounter
    WHERE {
        patient:%s ex:hasEncounter ?encounter .
    }
    """ % patient_id

    results = graph.query(query)

    return [str(row.encounter) for row in results]
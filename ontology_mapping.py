# Simple clinical ontology mapping

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
    mapped_entities = []

    for entity in entities:
        text = entity["text"]

        if text in ONTOLOGY:
            concept = ONTOLOGY[text]

            mapped_entities.append({
                "text": text,
                "type": concept["type"],
                "uri": concept["uri"]
            })

    return mapped_entities


if __name__ == "__main__":

    sample_entities = [
        {
            "text": "Type 2 Diabetes",
            "label": "DISEASE"
        },
        {
            "text": "Metformin",
            "label": "MEDICATION"
        },
        {
            "text": "Increased thirst",
            "label": "SYMPTOM"
        }
    ]

    mapped = map_to_ontology(sample_entities)

    print("Ontology Mapping:")
    print()

    for entity in mapped:
        print(entity)
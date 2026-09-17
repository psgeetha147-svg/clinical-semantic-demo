import spacy


nlp = spacy.load("en_core_web_sm")


def extract_entities(text):

    entities = []

    # Find general entities using spaCy
    doc = nlp(text)

    for ent in doc.ents:
        entities.append({
            "text": ent.text,
            "label": ent.label_
        })

    # Add our known clinical terms
    clinical_terms = [
        ("Type 2 Diabetes", "DISEASE"),
        ("Metformin", "MEDICATION"),
        ("Increased thirst", "SYMPTOM")
    ]

    for term, label in clinical_terms:

        if term.lower() in text.lower():

            already_exists = any(
                entity["text"].lower() == term.lower()
                for entity in entities
            )

            if not already_exists:
                entities.append({
                    "text": term,
                    "label": label
                })

    return entities
import spacy

_MODEL_CACHE = None

def load_model():
    global _MODEL_CACHE
    if _MODEL_CACHE is None:
        _MODEL_CACHE = spacy.load('modelos/modelo_spacy')
    return _MODEL_CACHE
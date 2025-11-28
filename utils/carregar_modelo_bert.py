from transformers import AutoModelForTokenClassification, AutoTokenizer

_MODEL_CACHE_BERT = None
_TOKENIZER_CACHE = None 

def load_model_bert():
    global _MODEL_CACHE_BERT
    if _MODEL_CACHE_BERT is None:
        _MODEL_CACHE_BERT = AutoModelForTokenClassification.from_pretrained('modelos/modelo_bert/bert_model')
    return _MODEL_CACHE_BERT

def load_tokenizer_bert():
    global _TOKENIZER_CACHE
    if _TOKENIZER_CACHE is None:
        _TOKENIZER_CACHE = AutoTokenizer.from_pretrained('modelos/modelo_bert/bert_tokenizer')
    return _TOKENIZER_CACHE
    

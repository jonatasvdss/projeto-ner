class ExtratorEntidades:
    def __init__(self, doc):
        self.doc = doc
    
    def extrair(self):
        return [
            {
                "texto": ent.text,
                "label": ent.label_,
                "posicao_inicio": ent.start_char,
                "posicao_fim": ent.end_char                
            }
            for ent in self.doc.ents
        ]

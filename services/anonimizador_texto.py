import re

class AnonimizadorTexto:
    def __init__(self, texto: str, entidades: list):
        self.texto = texto
        self.entidades = list(set(ent['texto'] for ent in entidades))
    
    def anonimizar(self):
        texto_anonimizado = re.sub(r'\s+', ' ', self.texto)
        texto_anonimizado = re.sub(r'\s*/\s*', '/', texto_anonimizado)
        texto_anonimizado = re.sub(r'\s*-\s*', '-', texto_anonimizado).strip()
        
        entidades_organizadas = [re.sub(r'\s+', ' ', ent) for ent in self.entidades] 
        entidades_organizadas = [re.sub(r'\s*/\s*', '/', ent) for ent in entidades_organizadas]
        entidades_organizadas = [re.sub(r'\s*-\s*', '-', ent.strip()) for ent in entidades_organizadas]
        
        for ent in entidades_organizadas:
            texto_anonimizado = re.sub(re.escape(ent), '[ANONIMIZADO]', texto_anonimizado, flags=re.IGNORECASE)
        
        return texto_anonimizado

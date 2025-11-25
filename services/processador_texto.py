import re

class ProcessadorTexto:
    def __init__(self, modelo, tokenizer):
        self.modelo = modelo
        self.tokenizer = tokenizer
        self.sentencas = []
        
        
    def dividir_texto_em_sentenca(self, texto):
        '''
        Divide o texto original em chunks baseados nos offsets dos tokens do BERT.
        '''
        texto_limpo = texto.strip().upper()

        encoding = self.tokenizer.encode_plus(
            texto_limpo,
            add_special_tokens=False,
            return_offsets_mapping=True
        )

        offsets = encoding['offset_mapping']
        input_ids = encoding['input_ids']

        chunks = []

        for i in range(0, len(input_ids), 512): 
            chunk_offsets = offsets[i:i + 512]
            chunk_start = chunk_offsets[0][0]  
            chunk_end = chunk_offsets[-1][1]  

            chunks.append(texto_limpo[chunk_start:chunk_end])



        self.sentencas = chunks
        
        return self.sentencas
    
    def gerar_docs_spacy(self):
        """
        Processa as sentencas em lote com nlp.pipe.
        """
        for doc in self.modelo.pipe(self.sentencas, batch_size=20):
            yield doc 


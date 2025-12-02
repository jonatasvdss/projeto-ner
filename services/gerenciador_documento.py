from .anonimizador_texto import AnonimizadorTexto
from .processador_texto import ProcessadorTexto
from .extrator_entidades import ExtratorEntidades
from utils.carregar_modelo_ner import load_model
from utils.carregar_modelo_bert import load_model_bert, load_tokenizer_bert
from config.log_config import logger
import torch
import re

class GerenciadorDocumento:
    def __init__(self, texto: str):
        self.texto = texto
        self.modelo = load_model()
        self.modelo_bert = load_model_bert()
        self.tokenizer = load_tokenizer_bert()
        self.processador = ProcessadorTexto(self.modelo, self.tokenizer)
        self.entidades_extrator = None
        self.entidades = []
        self.sentencas = []
        logger.info("Anonimizador de Documento inicializado.")

    def preprocessar(self):
        try:
            print(len(self.texto))
            self.sentencas = self.processador.dividir_texto_em_sentenca(self.texto)
            print(len(self.sentencas))
            docs_generator = self.processador.gerar_docs_spacy()
            
            self.entidades_extrator = []
            for doc in docs_generator:
                extrator = ExtratorEntidades(doc)
                self.entidades_extrator.append(extrator)
            
            logger.info("Texto processado com sucesso.")
        except Exception as e:
            logger.error("Erro ao processar: %s", e)


    def extrair_entidades(self):
        if not self.entidades_extrator:
            logger.warning("Documento não foi processado. Chamando o método preprocessar().")
            self.preprocessar()
        
        for extrator in self.entidades_extrator:
            self.entidades.extend(extrator.extrair())
                    
        logger.info("Entidades extraídas com sucesso.")

    def extrair_entidades_bert(self):
        for input_text in self.sentencas:
            input_text = input_text.title()
            
            inputs = self.tokenizer(input_text, max_length=512, truncation=True, return_tensors="pt", return_offsets_mapping=True)

            offset_mapping = inputs.pop("offset_mapping")[0]
            tokens = inputs.tokens()

            outputs = self.modelo_bert(**inputs).logits
            predictions = torch.argmax(outputs, dim=2)

            entities = []
            current_entity = {"label": None, "texto": ""}
            for idx, (token, prediction, offsets) in enumerate(zip(tokens, predictions[0].numpy(), offset_mapping)):
                label = self.modelo_bert.config.id2label[prediction]
                start, end = offsets.tolist()

                if start == end:
                    continue

                token_text = input_text[start:end] if token == "[UNK]" else token.replace("##", "")
                if token.startswith("##") and current_entity["texto"]:
                    current_entity["texto"] += token_text 
                elif label.startswith("B-"):  
                    if current_entity["texto"]: 
                        entities.append(current_entity)
                    current_entity = {"label": label[2:], "texto": token_text}
                elif label.startswith("I-") and current_entity["label"] == label[2:]:
                    current_entity["texto"] += " " + token_text
                else:
                    if current_entity["texto"]:
                        entities.append(current_entity)
                    current_entity = {"label": None, "texto": ""}

            if current_entity["texto"]:
                entities.append(current_entity)
        
            entidades_adequadas = []
            for ent in entities:
                if (ent['label'] in ['ORGANIZACAO', 'PESSOA'] and len(re.findall(r'[a-zA-Z0-9]', ent['texto'])) > 3) or (ent['label'] == 'LOCAL' and len(ent['texto']) > 5):
                    entidades_adequadas.append(ent)
            self.entidades.extend(entidades_adequadas)
        
        logger.info("Entidades BERT extraídas com sucesso.")

    def get_entidades(self):
        if not self.entidades:
            logger.debug("Entidades não extraídas, chamando extrair_entidades()")
            self.extrair_entidades()
        return self.entidades
    
    def anonimizar_texto(self):
        anonimizar = AnonimizadorTexto(self.texto, self.entidades)
        
        return anonimizar.anonimizar()

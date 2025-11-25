import torch
from transformers import pipeline, AutoTokenizer
import logging

logger = logging.getLogger(__name__)

class ExtratorLGPD:
    def __init__(self):
        self.pipeline = None
        self.model_name = "celiudos/legal-bert-lgpd"
        self._carregar_modelo()

    def _carregar_modelo(self):
        try:
            logger.info(f"Carregando modelo {self.model_name}...")
            
            # Detecta dispositivo (GPU ou CPU)
            device = 0 if torch.cuda.is_available() else -1
            
            tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                model_max_length=512,
            )

            self.pipeline = pipeline(
                "ner",
                model=self.model_name,
                tokenizer=tokenizer,
                stride=100,
                aggregation_strategy="first",
                device=device
            )

            logger.info("Modelo Legal BERT LGPD carregado com sucesso.")
            
        except Exception as e:
            logger.error(f"Erro crítico ao carregar BERT LGPD: {e}")
            self.pipeline = None

    def extrair(self, texto: str) -> list:
        if not self.pipeline or not texto or not texto.strip():
            return []

        entidades_formatadas = []
        
        try:
            # O pipeline com stride lida com textos longos automaticamente
            resultados = self.pipeline(texto)
            
            for resultado in resultados:
                if resultado["label"] in ["CPF", "NOME"]:
                    entidades_formatadas.append({
                        "label": resultado['entity_group'],
                        "texto": resultado['word'],
                        "score": float(resultado['score']),
                        "start": resultado.get('start'),
                        "end": resultado.get('end')
                    })
                
        except Exception as e:
            logger.error(f"Erro na inferência do BERT LGPD: {e}")
            return []
        
        return entidades_formatadas
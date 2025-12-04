
# Projeto de Comparação dos Metadados de uma Petição Inicial com as Entidades Reconhecidas por NER

## Descrição

Este projeto é uma extensão de um framework de anonimização de documentos jurídicos preexistente. Enquanto o projeto original foca na ocultação de dados, este módulo foca na auditoria e validação da extração de entidades. Ele fornece uma interface para comparar os metadados esperados (autores, réus, CPFs/CNPJs) com o que os modelos de Inteligência Artificial (BERT e spaCy) conseguem efetivamente extrair das petições iniciais.

## Objetivo

O objetivo principal é garantir a confiabilidade dos modelos de NER (Named Entity Recognition) utilizados. A ferramenta permite:
- **Validar a Extração:** Verificar automaticamente se os dados sensíveis listados nos metadados do processo estão presentes e sendo reconhecidos corretamente no texto da petição (PDF).
- **Identificar Falhas:** Apontar discrepâncias causadas por erros de OCR, formatação atípica ou falhas nos modelos de IA.
- **Comparação Inteligente:** Utilizar lógica fuzzy e interseção de tokens para reconhecer nomes mesmo com abreviações, erros de digitação ou ausência de sobrenomes.

## Funcionalidades

- **Interface de Teste (Frontend):** Formulário web minimalista para upload de petições (PDF) e inserção manual de metadados para teste.
- **Processamento de PDF:** Conversão e limpeza de arquivos PDF para texto processável.
- **Extração Híbrida:** Utilização conjunta de modelos BERT e spaCy (com regras personalizadas via `EntityRuler`) para maximizar a captura de entidades.
- **Lógica de Comparação Robusta:**
  - Match Exato: Identificação precisa.
  - Match Parcial: Identificação de substrings.
  - Match por Tokens: Reconhecimento de nomes fora de ordem ou incompletos.
  - Similaridade: Identificação baseada na distância de Levenshtein (para erros de digitação).
- **Relatório Visual:** Exibição clara dos status "ENCONTRADO" (verde) ou "AUSENTE" (vermelho) para cada metadado.

## Estrutura do Projeto

Abaixo, a estrutura atualizada com os módulos de comparação e interface:

```
backend/
├── config/                       # Configurações de log e ambiente
├── dados/                        # (Ignorado no Git) Armazenamento temporário de dados
├── modelos/                      # (Ignorado no Git) Binários dos modelos BERT/spaCy
├── routes/                       # Roteamento da API
│   ├── __init__.py
│   ├── anonimizar.py             # Rota original (API JSON)
│   └── comparar.py               # [NOVO] Rota da interface de auditoria
├── services/                     # Lógica de negócio
│   ├── gerenciador_documento.py  # Orquestrador dos modelos
│   ├── comparar_metadados.py     # [NOVO] Lógica de comparação
│   └── ...
├── static/                       # [NOVO] Arquivos CSS e Assets
│   └── style.css
├── templates/                    # [NOVO] Templates HTML (Jinja2)
│   └── index.html
├── utils/                        # Funções auxiliares de carregamento de modelos
├── app.py                        # Ponto de entrada da aplicação Flask
├── docker-compose.yml            # Orquestração dos containers
├── Dockerfile                    # Definição da imagem
├── teste.py                      # Utilizado para testar comparação antes do frontend
└── requirements.txt              # Dependências do projeto
```


### Dependências

- **Flask & Jinja2:** Para o servidor web e renderização da interface.
- **pypdf:** Para extração de texto de arquivos PDF.
- **pandas:** Para manipulação e normalização de dados.
- **transformers & torch:** Para execução do modelo BERT.
- **spaCy:** Para execução de regras de padrão (Regex) e NER complementar.

## Como Executar o Projeto

Este projeto utiliza **Docker** para garantir que todas as dependências e modelos rodem em qualquer ambiente.

1. **Subir o Ambiente**

No terminal, na raiz do projeto, execute:


```bash
docker compose up --build -d
```
*Isso irá construir a imagem, instalar as dependências listadas no `requirements.txt` e iniciar o servidor na porta 5058.*

2. **Acessar a Ferramenta de Auditoria**

Abra o seu navegador e acesse o seguinte endereço:

👉 `http://localhost:5058/auditoria_metadados/comparar_peticao_metadados`

3. **Como Usar**

    1. No campo "Escolher petição inicial", faça o upload de um arquivo .pdf.
    2. Preencha os campos de texto com os nomes e documentos esperados.
    3. Clique em Enviar.
    4. O sistema processará o arquivo e retornará o relatório de comparação na mesma tela.
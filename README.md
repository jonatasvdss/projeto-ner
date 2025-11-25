
# Projeto de Anonimização de Dados Pessoais Utilizando NER com SpaCy no Contexto Jurídico

## Descrição

Este projeto utiliza o modelo de **Reconhecimento de Entidades Nomeadas (NER)** do SpaCy para anonimizar dados pessoais em textos jurídicos. O modelo foi treinado especificamente para o contexto jurídico brasileiro, identificando nomes das partes em documentos legais, como processos, petições e sentenças.
Os dados pessoais anonimizados são:
- Nomes Próprios
- CPF
- CNPJ
- RG
- Logradouro
- CEP
- Telefone
- Email
- Placa de carro

## Objetivo

O principal objetivo deste projeto é proteger a privacidade das partes envolvidas em documentos jurídicos, removendo automaticamente informações pessoais e sensíveis através da anonimização de nomes e outras entidades identificáveis.

## Funcionalidades

- **Treinamento de modelos NER personalizados** com foco no vocabulário jurídico brasileiro.
- **Identificação de nomes de pessoas, empresas e instituições** em textos jurídicos.
- **Anonimização automática das entidades identificadas**, substituindo por identificadores como `[ANONIMIZADO]`.
- **Suporte para textos longos e múltiplos formatos de entrada** (texto, documentos, etc.).

## Estrutura do Projeto

A estrutura do projeto é organizada em diferentes módulos responsáveis por componentes específicos. Abaixo está uma visão geral:

```
backend/
├── bert_ner/             # Modelo BERT para fazer a Identificação de Entidades Nomeadas
├── modelo_spacy/             # Modelo Spacy para utilização do componente Entity_ruler
├── routes/                 # Roteamento da API
│   ├── __init__.py
│   ├── anonimizar.py       # Rota para anonimizar
├── services/               # Lógica de anonimização e processamento
├── utils/                  # Funções auxiliares e configuração de modelo
├── app.py                  # Arquivo principal de execução da API
└── requirements.txt        # Dependências do projeto
├── .gitignore              # Lista de arquivos e pastas ignorados pelo Git 
└── README.md               # Arquivo de texto com informações sobre o projeto
```


### Dependências

- **transformers**: Biblioteca para utilização de modelos de IA, no caso, Bert.
- **spaCy**: Biblioteca para processamento de linguagem natural.
- **Flask**: Framework para criação da API RESTful.
- **Flask-CORS**: Para habilitar o compartilhamento de recursos entre origens.
- **Outras dependências** podem ser encontradas no `requirements.txt`.

## Como Executar o Projeto

### Pré-requisitos
Utilizar o comando do docker:

```bash
docker compose up -d
```

### Requisição para anonimizacao:

#### URL `http://localhost:5058/anonimizacao_docs`.

Teste a API com o endpoint `/anonimizar` enviando um **POST** com um texto JSON contendo o campo `texto`.

   Exemplo de corpo de requisição:

   ```json
   {
     "texto": "João da Silva, brasileiro (...) com CPF 123.456.789-00 (...)"
   }
   ```

   Resposta esperada:

   ```json
   {
     "texto_anonimizado": "[ANONIMIZADO], brasileiro (...), com CPF [ANONIMIZADO] (...)",
     "entidades": [
       {
         "texto": "João da Silva",
         "label": "PESSOA",
         "posicao_inicio": 0,
         "posicao_fim": 14
       },
       {
         "texto": "123.456.789-00",
         "label": "CPF",
         "posicao_inicio": 45,
         "posicao_fim": 60
       }
     ]
   }
   ```

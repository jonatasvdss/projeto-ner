import pandas as pd
from services.comparar_metadados import peticao_contem_metadados
import sys

df = pd.read_csv("/app/metadado_peticoes_iniciais_13112025.csv")

df.drop(columns=["comarca", "serventia", "classe", "assunto"], inplace=True)

if __name__ == "__main__":
    try:
      linha = df.iloc[int(sys.argv[1]), :]

      peticao = linha["inteiro_teor"]

      meta_nome_autor = linha["polo_ativo"]
      meta_id_autor = linha["cpf_cnpj_polo_ativo"]
      meta_nome_reu = linha["polo_passivo"]
      meta_id_reu = linha["cpf_cnpj_polo_passivo"]

      peticao_contem_metadados(
        peticao,
        meta_nome_autor,
        meta_id_autor,
        meta_nome_reu,
        meta_id_reu
      )
    except IndexError:
       print("Índice deve ser no mínimo 0 e no máximo 999!")
    except Exception as e:
       print(e)
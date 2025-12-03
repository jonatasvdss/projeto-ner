import pandas as pd
from services.comparar_metadados import peticao_contem_metadados
import sys

df = pd.read_csv("/app/dados/metadado_peticoes_iniciais_13112025.csv")

df.drop(columns=["comarca", "serventia", "classe", "assunto"], inplace=True)

if __name__ == "__main__":
    try:
      linha = df.iloc[int(sys.argv[1]), :]

      peticao = linha["inteiro_teor"]

      meta_nome_autor = linha["polo_ativo"]
      meta_id_autor = linha["cpf_cnpj_polo_ativo"]
      meta_nome_reu = linha["polo_passivo"]
      meta_id_reu = linha["cpf_cnpj_polo_passivo"]

      resultado, _ = peticao_contem_metadados(
        peticao,
        meta_nome_autor,
        meta_id_autor,
        meta_nome_reu,
        meta_id_reu
      )

      print(f"Sucesso geral? {resultado['sucesso_geral']}")
      
      print("\n", "----------------------- IDs ----------------------", end="")
      print(" ------ Status ------")
      for id in resultado["comparacao_ids"]:
         print(f"{id['alvo']:<50} | {id['status']}")
      
      print("\n", "---------------------- Nomes ---------------------", end="")
      print(" ------ Status ------")
      for nome in resultado["comparacao_nomes"]:
         print(f"{nome['alvo']:<50} | {nome['status']}")

    except IndexError:
       print("Índice deve ser no mínimo 0 e no máximo 999!")
    except Exception as e:
       print(e)
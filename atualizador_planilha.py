import os
import openai
import requests
import schedule
import time

# Pegando variáveis de ambiente de forma segura
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")
CAMINHO_PLANILHA_LOCAL = "planilha.csv"  # Nome do arquivo que estará junto no Render

# Configurar a chave da API
openai.api_key = OPENAI_API_KEY

def upload_arquivo(filepath):
    """Faz upload do arquivo CSV para a OpenAI."""
    with open(filepath, "rb") as f:
        response = openai.files.create(file=f, purpose="assistants")
    return response.id

def atualizar_assistant(file_id):
    """Atualiza o Assistant com o novo arquivo enviado."""
    openai.beta.assistants.update(
        assistant_id=ASSISTANT_ID,
        file_ids=[file_id]
    )
    print(f"Assistant atualizado com o novo arquivo: {file_id}")

def tarefa_principal():
    """Função principal que atualiza o Assistant."""
    try:
        print("Iniciando atualização...")
        novo_file_id = upload_arquivo(CAMINHO_PLANILHA_LOCAL)
        atualizar_assistant(novo_file_id)
        print("Atualização concluída com sucesso!")
    except Exception as e:
        print(f"Erro: {str(e)}")

# Agendamento
schedule.every(1).hours.do(tarefa_principal)

if __name__ == "__main__":
    print("Bot iniciado!")
    tarefa_principal()  # Executa na inicialização também
    while True:
        schedule.run_pending()
        time.sleep(1)

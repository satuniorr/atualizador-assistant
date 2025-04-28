# ===============================================
# Atualizador de Planilha no Assistant (v2 Deluxe)
# ===============================================

import os
import openai
import requests
import schedule
import smtplib
import time
from email.mime.text import MIMEText
from datetime import datetime

# ===============================================
# CONFIGURAÇÕES
# ===============================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")
CAMINHO_PLANILHA_LOCAL = "planilha.csv"
URL_PLANILHA = os.getenv("PLANILHA_URL")  # opcional para download automático
EMAIL_SENDER = os.getenv("EMAIL_SENDER")  # opcional para alerta
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

openai.api_key = OPENAI_API_KEY

# ===============================================
# FUNÇÕES DE UTILIDADE
# ===============================================

def log(mensagem):
    agora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{agora}] {mensagem}")

def enviar_alerta(erro):
    if not EMAIL_SENDER or not EMAIL_PASSWORD or not EMAIL_RECEIVER:
        log("[ALERTA] Email de alerta não configurado. Ignorando envio.")
        return
    try:
        msg = MIMEText(f"Ocorreu um erro no bot: {erro}")
        msg["Subject"] = "⚠️ Bot Atualizador - Erro Detectado"
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())

        log("[ALERTA] Email de erro enviado!")
    except Exception as e:
        log(f"[ERRO-EMAIL] Falha ao enviar alerta: {str(e)}")

def baixar_planilha():
    if not URL_PLANILHA:
        log("[INFO] URL de download da planilha não configurada. Usando arquivo local.")
        return
    try:
        resposta = requests.get(URL_PLANILHA)
        if resposta.status_code == 200:
            with open(CAMINHO_PLANILHA_LOCAL, 'wb') as f:
                f.write(resposta.content)
            log("Planilha baixada com sucesso.")
        else:
            log(f"[ERRO] Falha ao baixar planilha: Status {resposta.status_code}")
    except Exception as e:
        log(f"[ERRO] Exceção ao baixar planilha: {str(e)}")

def upload_arquivo(filepath):
    with open(filepath, "rb") as f:
        response = openai.files.create(file=f, purpose="assistants")
    return response.id

def atualizar_assistant(file_id):
    openai.beta.assistants.update(
        assistant_id=ASSISTANT_ID,
        file_ids=[file_id]
    )
    log(f"Assistant atualizado com novo arquivo: {file_id}")

def tarefa_principal():
    try:
        log("Iniciando ciclo de atualização...")
        baixar_planilha()
        novo_file_id = upload_arquivo(CAMINHO_PLANILHA_LOCAL)
        atualizar_assistant(novo_file_id)
        tamanho_kb = os.path.getsize(CAMINHO_PLANILHA_LOCAL) / 1024
        log(f"Upload concluído. Arquivo enviado: {tamanho_kb:.2f} KB")
        log("Atualização finalizada.")
    except Exception as e:
        log(f"[ERRO-GERAL] {str(e)}")
        enviar_alerta(str(e))

# ===============================================
# INICIALIZAÇÃO
# ===============================================

if __name__ == "__main__":
    log("Bot iniciado!")
    tarefa_principal()  # Executa uma vez ao iniciar
    schedule.every(1).hours.do(tarefa_principal)  # Executa de hora em hora

    while True:
        schedule.run_pending()
        time.sleep(1)


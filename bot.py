from botcity.web import WebBot, Browser
from botcity.maestro import *
from webdriver_manager.chrome import ChromeDriverManager
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os
import shutil

BotMaestroSDK.RAISE_NOT_CONNECTED = False

pasta_origem = "C:/Users/noturno/Downloads/organizada"
pasta_imagens = os.path.join(pasta_origem, "imagens")
pasta_documentos = os.path.join(pasta_origem, "documentos")

# Criar as pastas 
os.makedirs(pasta_imagens, exist_ok=True)
os.makedirs(pasta_documentos, exist_ok=True)

def download_drive_folder(drive, folder_id, destino):
    # Lista os arquivos no Google Drive
    file_list = drive.ListFile({'q': f"'{folder_id}' in parents and trashed=false"}).GetList()

    for file in file_list:
        file_name = file['title']
        file_id = file['id']
        print(f"Baixando {file_name}...")

        # Verifica se é um arquivo para baixar
        if file['mimeType'] != 'application/vnd.google-apps.folder':
            file.GetContentFile(os.path.join(destino, file_name))
        else:
            novo_destino = os.path.join(destino, file_name)
            os.makedirs(novo_destino, exist_ok=True)
            download_drive_folder(drive, file_id, novo_destino)

def autenticar_google_drive():
    gauth = GoogleAuth()

    # Carrega as credenciais 
    gauth.LoadCredentialsFile("mycreds.txt")
    if gauth.credentials is None:
        # Salva as credenciais
        gauth.LocalWebserverAuth()
        gauth.SaveCredentialsFile("mycreds.txt")
    elif gauth.access_token_expired:
        # Atualiza o token 
        gauth.Refresh()
        gauth.SaveCredentialsFile("mycreds.txt")
    else:
        # Usa as credenciais salvas
        gauth.Authorize()

    return GoogleDrive(gauth)

def organizar_arquivos(destino):
    extensoes_imagens = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
    extensoes_documentos = ['.pdf', '.docx', '.doc', '.txt', '.zip']

    for root, _, files in os.walk(destino):
        for file in files:
            extensao = os.path.splitext(file)[1].lower()

            if extensao in extensoes_imagens:
                shutil.move(os.path.join(root, file), os.path.join(pasta_imagens, file))
            elif extensao in extensoes_documentos:
                shutil.move(os.path.join(root, file), os.path.join(pasta_documentos, file))

def main():
    maestro = BotMaestroSDK.from_sys_args()
    execution = maestro.get_execution()

    print(f"Task ID is: {execution.task_id}")
    print(f"Task Parameters are: {execution.parameters}")

    # bot = WebBot()
    # bot.headless = False
    # bot.browser = Browser.CHROME
    # bot.driver_path = ChromeDriverManager().install()

    # Autenticação no Google Drive
    drive = autenticar_google_drive()

    # ID da pasta do Google Drive e destino de download
    folder_id = "1KBTMZMt5oe_iwjfjddv_bXkINXKbfaAS"  # ID da pasta para baixar
    destino = pasta_origem

    # Baixa a pasta do Google Drive
    download_drive_folder(drive, folder_id, destino)

    # Organiza os arquivos baixados por extensão
    organizar_arquivos(destino)

    # bot.wait(30000)
    # bot.stop_browser()

    maestro.finish_task(
        task_id=execution.task_id,
        status=AutomationTaskFinishStatus.SUCCESS,
        message="Task Finished OK."
    )

def not_found(label):
    print(f"Element not found: {label}")

if __name__ == '__main__':
    main()

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os


# Configuração de autenticação sem acesso manual
gauth = GoogleAuth()

gauth.LoadCredentialsFile("credentials.json")

if gauth.credentials is None:
    # Se não houver credenciais, faça a autenticação usando o navegador
   gauth.LocalWebserverAuth()
#elif gauth.access_token_expired:
    # Se as credenciais expiraram, faça a atualização usando o método Refresh()
#    gauth.Refresh()
#else:
    # Se as credenciais ainda são válidas, a autenticação é bem-sucedida
#    gauth.Authorize()

drive = GoogleDrive(gauth)

# from pydrive.auth import GoogleAuth: Esta linha importa a classe GoogleAuth do módulo auth da biblioteca PyDrive. A classe GoogleAuth é responsável pela autenticação com o Google.
#from pydrive.drive import GoogleDrive: Esta linha importa a classe GoogleDrive do módulo drive da biblioteca PyDrive. A classe GoogleDrive é responsável por interagir com o Google Drive após a autenticação.
#gauth = GoogleAuth(): Esta linha cria uma instância da classe GoogleAuth, que é utilizada para autenticar o usuário.
#gauth.LocalWebserverAuth(): Este método LocalWebserverAuth() realiza a autenticação local do usuário, abrindo um navegador da web padrão onde o usuário pode fazer login na sua conta do Google e conceder permissões para acessar o Google Drive.
#drive = GoogleDrive(gauth): Esta linha cria uma instância da classe GoogleDrive, passando o objeto gauth como argumento. Essa instância é usada para interagir com o Google Drive após a autenticação.

# ID da pasta no Google Drive para onde os arquivos serão carregados
folder_id = '<ID>'

# Diretório local
local_directory = '<diretório com os dados>'

# Lista de arquivos no diretório local
files = os.listdir(local_directory)
print(files)

# Loop pelos arquivos no diretório local
for file_name in files:
    # Caminho completo do arquivo local
    local_file_path = os.path.join(local_directory, file_name)

    # Cria um objeto de arquivo no Google Drive
    file_drive = drive.CreateFile({'title': file_name, 'parents': [{'id': folder_id}]})

    # Define o conteúdo do arquivo como o arquivo local
    file_drive.SetContentFile(local_file_path)

    # Carrega o arquivo para o Google Drive
    file_drive.Upload()

    print(f"Arquivo '{file_name}' carregado com sucesso para o Google Drive.")

print("Todos os arquivos foram carregados para o Google Drive.")


# Download files
#file_list = drive.ListFile({'q' : f"'{folder}' in parents and trashed=false"}).GetList()
#for index, file in enumerate(file_list):
#    print(index+1, 'file downloaded : ', file['title'])
#    file.GetContentFile(file['title'])

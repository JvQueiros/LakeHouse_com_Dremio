# Data Lakehouse with Dremio

O presente projeto apresenta uma arquitetura que possibilita o armazenamento e análise de dados de forma simples e rápida. Não utiliza códigos, focando, principalmente, em ferramentas SaaS, o que pode ser uma boa escolha para empresas de pequeno e médio porte, pois é fácil ensina-las a colaboradores não tão técnicos. Ademais, dessa forma, podemos extrair valor das informações dos dados com baixo custo e no menor tempo possível, aumentando a eficiência do negócio.

Utilizando o Dremio como motor de execução de queries SQL, a ideia é analisar  dados armazenados no AWS S3. Conforme será detalhado adiante, os dados são gerados e armazenados em um diretório local, carregados em um serviço de armazenamento - que servirá como método de backup -  transformados e armazenados em um Data Lake e, por fim, consumidos no Data Lakehouse.

![Untitled](https://github.com/JvQueiros/LakeHouse-com-Dremio/assets/95942380/999d0e77-676b-44ad-bcd8-780809e93947)

**MONTANDO A INFRAESTRUTURA**

→ **Backup dos arquivos para o Google Drive**

Utilizando a biblioteca PyDrive, construi-se um script Python e agenda-se sua execução com o Cron; dessa forma, o que se tem é um backup diário de determinado diretório. Nesse diretório armazenamos os arquivos com os datasets.

```python
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
    gauth.Refresh()
#else:
    # Se as credenciais ainda são válidas, a autenticação é bem-sucedida
    gauth.Authorize()

drive = GoogleDrive(gauth)

# ID da pasta no Google Drive para onde os arquivos serão carregados
folder_id = 'id_pasta_do_google_drive'

# Diretório local
local_directory = '/home/user/seu/diretorio/data'

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
```

![Untitled 1](https://github.com/JvQueiros/LakeHouse-com-Dremio/assets/95942380/26608b7e-e2a8-4d47-847c-4b5498ac4de9)

Com a API do Google Drive, realiza-se o upload atráves de uma conexão com OAuth. Ao final do texto, encontram-se os arquivos utilizados, bem como o link de referência com o passo a passo detalhado da criação do script.

![Untitled 2](https://github.com/JvQueiros/LakeHouse-com-Dremio/assets/95942380/a10ad629-47f0-4abd-b8a3-767be819fffe)

→ **Conectando com o Airbyte**

Com os arquivos no drive, as etapas do ETL são realizadas pelo Airbyte, rodando localmente com alguns containers no Docker.

![Untitled 3](https://github.com/JvQueiros/LakeHouse-com-Dremio/assets/95942380/6f869976-d4ec-414b-92f0-1f1d753cb678)

No que tange a configuração dos conectores, utilizou-se como Source o conector do Google Drive e, como Destination, o conector do S3; configurados com autenticação “Service Account Key Authentication” e “S3 Access Key Authentication”, respectivamente.

![Untitled 4](https://github.com/JvQueiros/LakeHouse-com-Dremio/assets/95942380/8c5d8d40-d5be-4116-85fa-d24767ed2439)

![Untitled 5](https://github.com/JvQueiros/LakeHouse-com-Dremio/assets/95942380/acb18e04-3582-487f-b3ac-8ac03206114c)

Importante, ao definir a conexão do Google Drive, i.e. a Source, devemos configurar dois Streams sync, direcionando-os para cada um dos arquivos individualmente. Caso contrário, todos os arquivos que estão na pasta do Google Drive, serão carregados no S3 em um único arquivo .JSON. Seguindo a maneira descrita nesse projeto, ao final, o que teremos são dois arquivos separados em pastas distintas no S3, veja-se: 

![Untitled 6](https://github.com/JvQueiros/LakeHouse-com-Dremio/assets/95942380/da39f945-a568-46d1-92bf-744a895ef73f)

![Untitled 7](https://github.com/JvQueiros/LakeHouse-com-Dremio/assets/95942380/e2f297da-5ff1-4fa2-824a-2d69bccf6720)

Outro ponto a se dar atenção é a utilização de arquivos excel (.xlsx) no Drive. O conector do Google Drive tem um tipo de streams destinado para a leitura de arquivos nesse formato, entretanto ainda está em beta. Tipicamente, utiliza-se o conector do Google Sheet, o qual nos permite compartilhar o link da planilha diretamente.

![Untitled 8](https://github.com/JvQueiros/LakeHouse-com-Dremio/assets/95942380/62b9b273-be1e-4e3e-b438-ded7137710b2)

→ **Dremio**

Com o Dremio, cria-se um “Sonar Project”, o qual fornecerá um template do Cloudformation para o deploy do stack.

![Untitled 9](https://github.com/JvQueiros/LakeHouse-com-Dremio/assets/95942380/96104744-48a8-4029-9137-1a0b9a820dc3)

O Dremio não se conecta automaticamente ao Bucket S3 onde os dados estão armazenados, é necessário configurar manualmente clicando no ícone de adição (+) ; selecionando “S3” e preenchendo os campos necessários.

![Untitled 10](https://github.com/JvQueiros/LakeHouse-com-Dremio/assets/95942380/c3c95f55-50a1-4f0a-810b-6cb536902087)

![Untitled 11](https://github.com/JvQueiros/LakeHouse-com-Dremio/assets/95942380/65827772-9816-4b96-94eb-7af4545171df)

![Untitled 12](https://github.com/JvQueiros/LakeHouse-com-Dremio/assets/95942380/d656ef7e-77ca-4b9b-969c-a8a5581b79a0)

Após a configuração, temos acesso ao bucket e aos arquivos:

![Untitled 13](https://github.com/JvQueiros/LakeHouse-com-Dremio/assets/95942380/5ad4d935-43c0-4d27-9f9a-dd7e98b14aba)

É necessário configurar cada um dos arquivos para que sejam transformados em um formato tabular e assim analisados com SQL. Esse processo é simples, basta clicar no arquivo e indicar qual o formato atual:

![Untitled 14](https://github.com/JvQueiros/LakeHouse-com-Dremio/assets/95942380/ab1b0799-09cb-46e5-b56a-a9a1bc5e1201)

![Untitled 15](https://github.com/JvQueiros/LakeHouse-com-Dremio/assets/95942380/f96e4913-9944-4b43-8854-4f01dbfac031)

A partir daqui podemos realizar consultas SQL nesses arquivos:

![Untitled 16](https://github.com/JvQueiros/LakeHouse-com-Dremio/assets/95942380/88b39b35-3ad3-4b4f-93aa-1aa94f05290e)

![Untitled 17](https://github.com/JvQueiros/LakeHouse-com-Dremio/assets/95942380/e522b6d2-20a5-4b3b-87d9-a30310c7fcc5)

Finalmente, esse projeto demonstra que é possível realizar consultas SQL aos dados que estão salvos no S3 de forma rápida, muito interessante para analises pontuais que não demandam grandes transformações e tratamentos nos dados. Foi desenvolvido tendo como base o projeto demonstrado no Curso de Formação de Engenheiro de Dados da Data Science Academy (DSA).

> Erros e problemas ao longo do projeto
> 
1. Erro com a autenticação automática na API do Google Drive. 
    
    Levei um tempo para conseguir identificar as credenciais e tolkens que devem compor o arquivo “credentials.json”. Estava retornando o erro abaixo. Para superar esse pequeno problema, alterei o código para que, ao realizar a autenticação manual, as credenciais fossem  gravadas em um arquivo, depois modifiquei novamente o código direcionando para o arquivo criado.
    

[**`credentials.json`**. O erro específico **`KeyError: '_module'`**](https://www.notion.so/credentials-json-O-erro-espec-fico-KeyError-_module-b18269ab0e854e1cacc47aadeae942ca?pvs=21)

2. O Docker estava com problemas para realizar o bind de um diretório.
    
    Impossibilitando o deploy  dos container com Airbyte, não estava conseguindo mapear o diretório necessário para o bind. Pesquisei na documentação e explorei os erros até que aprendi que o mapeamento necessário poderia ser realizado pelo Docker Desktop. Após a definição em “Resources” > “File sharing”, o Docker funcionou perfeitamente.
    

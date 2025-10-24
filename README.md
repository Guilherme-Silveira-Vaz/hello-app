# Projeto DevOps CI/CD - GitHub Actions Workflow + ArgoCD

## Introdução

Este projeto tem como objetivo utilizar ferramentas muito populares de **DevOps** no momento atual para o desenvolvimento continuo e entrega de aplicações modernas. Dessa maneira iremos abordar a aplicação **fastAPI**, criando um Workflow com **GitHub Actions** para construir as imagens da aplicação, e integrando o **ArgoCD** para monitorar o repositório com os arquivos manifestos yaml, reponsáveis por realizar os **deployments de forma automatizada**, garantindo agilididade, segurança e consistência.

## Requisitos para realizar o projeto

- Git/GitHub
- Conta no Docker Hub
- Rancher Desktop (com **kubernetes** habilitado)
- ArgoCD instalado no cluster Kubernetes
- Python 3 e Docker instalados

## Sumário

- [1. Configurando o Ambiente](#1---configurando-o-ambiente)
  - [1.1 Repositório hello-app para workflow do build da aplicação](#11---repositório-hello-app-para-workflow-do-build-da-aplicação)
  - [1.2 Repositório com os manifestos yaml monitorados pelo ArgoCD](#12---repositório-com-os-manifestos-yaml-monitorados-pelo-argocd)
- [2. Montando a Pipeline](#2---montando-a-pipeline)
  - [2.1 Criando os Secrets no Repositório](#21---criando-os-secrets-no-repositório)
  - [2.2 Criando o Workflow do GitHub Actions para build da imagem no DockerHub](#22---criando-o-workflow-do-github-actions-para-build-da-imagem-no-dockerhub)
- [3. Criando os arquivos manifests](#3---criando-os-arquivos-manifests)
- [4. Buildando e verificando imagem no DockerHub](#4---buildando-e-verificando-imagem-no-dockerhub)
- [5. Montando a aplicação no ArgoCD](#5---montando-a-aplicação-no-argocd)
  - [5.1 Conectando o ArgoCD](#51---conectando-o-argocd)
  - [5.2 Criando a aplicação](#52---criando-a-aplicação)
- [6. Testando a aplicação](#6---testando-a-aplicação)
- [7. Conclusão](#7---conclusão)

## 1 - Configurando o Ambiente

O primeiro passo para a criação e execução do projeto é a criação de dois repositórios públicos no GitHub, sendo um (pode ser https)responsável pelo build da imagem docker que contém uma aplicação de fastAPI, e o outro (**SSH OBRIGATÓRIO**)responsável por armazenar os manifestos yaml que servirá como fonte de verdade para o ArgoCD implementar a aplicação no cluster Kubernetes.

### 1.1 - Repositório hello-app para workflow do build da aplicação

- Na sua conta do GitHub navegue até a aba de repositórios
- Crie um novo repositório com o nome **hello-app**
- Crie o **diretório hello-app** que utilizaremos com o VSCode
- No diretório hello-app crie o arquivo **Dockerfile**, **main.py**, **requirements.txt**
- No mesmo diretório hello-app crie mais 2 diretórios, o primeiro **.github** e dentro do .github crie o diretório **workflows**
- No diretório workflows crie o arquivo **ci.yaml**

Diagrama da estrutura:

```
hello-app/
├── .github/
│   └── workflows/
│       └── ci.yaml
├── Dockerfile
├── main.py
└── requirements.txt
```

No arquivo **main.py** utilize os comandos da aplicação fastAPI:

```
from fastapi import FastAPI
app = FastAPI()
@app.get("/")
async def root():
 return {"message": "Hello World"}
```

No arquivo **requirements.txt** escreva os comandos que serão utilizados pelo Dockerfile como dependência do fastAPI:

```
fastapi
uvicorn
```

No arquivo **Dockerfile** deixe assim:

```
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]
```

- RUN pip install -r requirements.txt : o container utilizará o pacote pip install do python para baixar as dependências que escrevemos dentro do arquivo requirements

- CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--reload"] : o terminal do container vai rodar o pacote uvicorn (fastAPI) no arquivo main:app, e vai disponibilizar o serviço na porta 80 para sincronizar futuramente com a máquina, e o reload garantirá que toda vez que o arquivo main.py do fastAPI for alterado, o pacote irá recarregar a aplicação.

![dockerFile](img/filedocker.png?raw=true)

Agora podemos **SUBIR OS ARQUIVOS PARA O REPOSITÓRIO hello-app** no GitHub, não se preocupe com o arquivo **ci.yaml** por enquanto, vamos popular ele mais tarde!

```
git init
git add .
git commit -m "first commit"
git branch -M main
git remote add origin [URL_DO_SEU_REPOSITORIO_DO_GITHUB]
git push -u origin main
```

### 1.2 - Repositório com os manifestos yaml monitorados pelo ArgoCD

- Na sua conta do GitHub navegue até a aba de repositórios
- Crie um novo repositório **conexão via SSH** com o nome **manifests-ci-cd**
- Crie o **diretório manifests-ci-cd** que utilizaremos com o VSCode
- No diretório manifests-ci-cd crie o arquivo **deployment.yaml**, **service.yaml** e um arquivo chamado **SERVICE** sem extensão

Diagrama da estrutura:

```
manifests-ci-cd/
|
├── deployment.yaml
├── service.yaml
└── SERVICE
```

Por enquanto vamos simplesmente digitar o número 0 no arquivo **SERVICE**, ele vai servir para incretarmos o valor da versão/tag do aplicativo a cada push e build de nova imagem no dockerhub realizado por Workflow do GitHub Actions.

Suba os arquivos para o repositório criado:

```
git init
git add .
git commit -m "first commit"
git branch -M main
git remote add origin [URL_DO_SEU_REPOSITORIO_DO_GITHUB]
git push -u origin main
```

## 2 - Montando a Pipeline

Agora com os dois repositórios criados, vamos adicionar os secrets e montar o workflow do GitHub actions no repositório hello-app para funcionar como pipeline, buildando a imagem e adicionando ao Docker Hub com a aplicação fastAPI.

### 2.1 - Criando os **Secrets** no Repositório

Primeiramente precisamos armazenar as credenciais de login do DockerHub onde subiremos a imagem automaticamente com o workflow.

Estando conectado no DockerHub, clique em **Perfil** -> **Account Settings** -> **Personal access tokens** -> **Generate new token** -> **Access permissions** -> **Read, Write, Delete** -> **Generate**

![dockerhubToken](img/tokenDockerHhub.png?raw=true)

Agora copie o Token e vamos utilizar como value em um Secrets de senha no repositório do Github.

De volta ao seu repositório **hello-app** do GitHub, clique na aba **Settings** (do próprio repositório) -> **Secrets and variables** -> **Actions** -> **Secrets** -> **New repository secret**

![secretsGithub](img/secretsGithub.png?raw=true)

Primeiro crie esses dois secrets com as credenciais de login do DockerHub:

- Name: **DOCKER_USERNAME** -> **Secret**: seu usuário de login do DockerHub -> **Add secret**
- Name: **DOCKER_PASSWORD** -> **Secret**: cole o token que acabou de copiar do DockerHub -> **Add secret**

Agora precisamos criar um secret que vai armazenar uma chave SSH para que o runner do Workflow consiga clonar o repositório manifests-ci-cd e commitar alterações nele de maneira automatizada.

Para **criar a chave SSH**, abra o terminal e navegue até a pasta onde deseja guardar as chaves SSH (não deixar em nenhum diretório utilizado pra subir arquivos nos repositórios para não acabar subindo o arquivo da chave junto por engano).

Utilize o comando:

```
ssh-keygen -t ed25519 -C "nome@identificacao"
```

Pressione Enter para aceitar o local padrão aonde você rodou o comando, ou altera para outro diretório da sua preferência, depois aperte Enter mais duas vezes pra não adicionar nenhuma senha na chave.

Agora vamos usar as chaves para conectar os dois repositórios, para acessar o valor das chaves navegue até o diretório onde gerou e rode os comandos:

```
cat id_ed25519_nomeChave.pub
cat id_ed25519_nomeChave
```

Copie o valor do output do comando cat chave.pub, vá no seu repositório do **manifests-ci-cd** -> **Settings** -> **Deploy keys** -> **Add deploy key** -> **Title**: nome descritivo -> **Key**: cole o valor do output da chave.pub -> **SELECIONE "Allow write access"** -> **Add key**

![deployKey](img/deployKey.png?raw=true)

Agora vamos armazenar o valor da outra chave sem extensão .pub nos **Secrets** do repositório **hello-app**.
De volta ao seu repositório hello-app do GitHub, clique na aba **Settings** (do próprio repositório) -> **Secrets and variables** -> **Actions** -> **Secrets** -> **New repository secret**:

![keySsh](img/keySSHCICD.png?raw=true)

- Name: **SSH_PRIVATE_KEY** -> **Secret**: valor do output do comando cat id_ed25519_nomeChave (copie até mesmo as linhas ---OPEN--- e ---END---) -> **Add secret**

### 2.2 - Criando o **Workflow** do **GitHub Actions** para build da imagem no DockerHub

Agora que estamos com os secrets configurados e a chave do SSH ligando os dois repositórios, podemos partir para a criação do Workflow que vai automatizar o build da aplicação.

Vamos popular o arquivo **ci.yaml** que está no diretório hello-app/.github/workflows responsável pelo repositório hello-app no GitHub.

```
name: CI/CD Hello-App

on:
  push:
    branches:
      - main

env:
  IMAGE_NAME: ${{ secrets.DOCKER_USERNAME }}/hello-app

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3

    - name: Log in to Docker Hub
      uses: docker/login-action@v3
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}

    - name: Setup SSH for manifests repo
      uses: webfactory/ssh-agent@v0.9.1
      with:
        ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}

    - name: Clone manifests repo
      run: git clone git@github.com:Guilherme-Silveira-Vaz/manifests-ci-cd.git

    - name: Increment image version
      run: |
        cd manifests-ci-cd
        LAST=$(cat VERSION)
        NEW=$((LAST + 1))
        echo "TAG=v$NEW" >> $GITHUB_ENV
        echo "$NEW" > VERSION

    - name: Build and push Docker image
      run: |
        docker build -t $IMAGE_NAME:$TAG .
        docker push $IMAGE_NAME:$TAG

    - name: Update deployment image
      run: |
        cd manifests-ci-cd
        sed -i "s|image: .*|image: $IMAGE_NAME:$TAG|" deployment.yaml
        git config user.name "github-actions"
        git config user.email "actions@github.com"
        git add deployment.yaml VERSION
        git commit -m "Update image to $TAG"
        git push origin main
```

- **Increment image version**: foi criado a lógica para alterar o arquivo VERSION que continha apenas o número 0, cada vez que realizarmos um push via workflow dispatch, significa que vamos criar um novo build da aplicação, o valor do VERSION será incrementado em 1, e vamos utilizar esse valor como tag de versão da imagem no DockerHub.

- **Update deployment image**: estamos navegando até o diretório do repositório que clonamos no runner do workflow, alterando qualquer conteúdo da linha "image" para o nome da nova imagem com a nova versão do dockerHub no arquivo deployment.yaml. Depois da alteração estamos commitando a alteração nesse arquivo por meio do SSH que permitimos a escrita no repositório.

- **Imagens do código no diretório 'img' deste repositório**

Agora com o último arquivo desse repositório pronto, podemos realizar o push novamente para utilizarmos o workflow_dispatch para disparar o fluxo de trabalho futuramente.

## 3 - Criando os arquivos manifests

De volta ao diretório dos arquivos responsáveis pelo repositório do manifests-ci-cd, vamos popular primeiramente o arquivo **deployment.yaml** que será utilizado no cluster kubernetes:

```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hello-app
  namespace: hello-app-ci
  labels:
    app: hello-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: hello-app
  template:
    metadata:
      labels:
        app: hello-app
    spec:
      containers:
      - name: hello-app
        image: guilhermesv3/hello-app:v0
        ports:
        - containerPort: 80
```

- **metadata: namespace: hello-app-ci** - esse trecho do código é para quando formos vincular o argoCD com o cluster kubernetes no namespace hello-app-ci que ainda vamos criar posteriormente

- **containers:image:** - nome do seu usário no docker, o /hello-app:v0 será substituido após o workflow rodar e criar a imagem docker com a primeira versão, pegando exatamente o mesmo nome da imagem que estará disponível no dockerHub, que no caso -> userDockerHub/hello-app:v1

- **- containerPort: 80** - a porta onde vamos vincular o service do cluster kubernetes para acessar o pod/container com a imagem do dockerHub.

- **Imagens do código no diretório 'img' deste repositório**

Agora vamos popular o arquivo **service.yaml**, responsável pela criação do service no cluster kubernetes:

```
apiVersion: v1
kind: Service
metadata:
  name: hello-app-service
spec:
  selector:
    app: hello-app
  ports:
    - protocol: TCP
      port: 8080
      targetPort: 80
  type: ClusterIP
```

- **ports: port: 8080 targetport: 80** - aqui estamos vinculando a porta do service da aplicação com o pod/container, pra posteriormente fazermos o port-forward da aplicação e acessar via localhost.

- **Imagens do código no diretório 'img' deste repositório**

Agora podemos realizar o push no diretório com os arquivos alterados e deixar os dois repositórios do github prontos.

## 4 - Buildando e verificando imagem no DockerHub

Depois de ter os dois repositórios prontos com o push, o workflow já irá disparar para construir a imagem, agora podemos verificar se subiu corretamente no dockerHub antes de integrarmos com o ArgoCD para a criação certa dos pods com a imagem do registry.

Espere o workflow realizar todas as etapas:

![workflowComplete](img/workflowGithub.png?raw=true)

Agora que o workflow foi executado, a imagem deve aparecer no seu repositório dockerHub:

![dockerRegistry](img/dockerHub.png?raw=true)

Adicione uma descrição da imagem -> **Add a description** no topo do repositório -> Abaixo do quadro da imagem do repositório edite o overwiew, que vai servir como descrição do que a imagem faz -> **Repository overview** -> **Edit**

Agora que a imagem está criada e armazenada no registry, podemos utilizar ela para os pods do cluster que o ArgoCD vai gerar!

## 5 - Montando a aplicação no ArgoCD

### 5.1 - Conectando o ArgoCD

Para montar a aplicação no ArgoCD, primeiro vamos criar um namespace no cluster Kubernetes onde ficará a aplicação, abra o Rancher Desktop com o cluster Kubernetes ativado e rode o comando no terminal:

```
kubectl create namespace hello-app-ci
```

Verifique se o namespace foi criado:

```
kubectl get namespace
```

Depois de termos criado o namespace, podemos partir para configurar o aplicativo no ArgoCD.
Primeiramente em um novo terminal em paralelo, realize o port-forward para habilitar a interface gráfica do ArgoCD no navegador:

```
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

![portForwardArgocd](img/portForwardArgoCD.png?raw=true)

Depois abra o navegador e digite na URL: http://localhost:8080

- **Login**: admin
- **Senha**: precisamos pegar o secret no rancher desktop, ou utilizar o comando no terminal:

```
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

Como pegar a senha no rancher:

![rancherSecret1](img/rancher.png?raw=true)

![rancherSecret2](img/rancher2o.png?raw=true)

Depois de conectar no ArgoCD, precisamos armazenar o repositório **manifests-ci-cd** com a chave SSH privada que geramos anteriormente para o ArgoCD conseguir monitorar o repositório. Clique em **Settings** -> **CONNECT REPO**:

![repoArgocd](img/connectRepoSsh.png?raw=true)

- **Choose your connection method**: **VIA SSH**
- **Project**: Selecione **default**
- **Repository URL**: link do seu repositório SSH **com final .git**
- **SSH private key data**: cole o mesmo valor do output da **chave privada** que geramos e copiamos anteriormente.

Clique em Connect após inserir os dados, e agora podemos criar a aplicação com o repositório salvo.

### 5.2 - Criando a aplicação

Agora clique em **Applications** -> **NEW APP**:

![createApp1](img/createAppArgoCD.png?raw=true)
![createApp2](img/createAppArgoCD2.png?raw=true)

- **Application Name**: hello-app
- **Project Name**: selecione o default
- **Sync Policy**: ative as 3 opções como na imagem
- **Source**: cole a URL do seu repositório manifests-ci-cd com .git no final
- **Revision**: branch que será monitorada, selecione a main
- **Path**: caminho onde se encontram os manifestos, se for no diretório raiz, escreva **'.' em vez de '/'**
- **Cluster URL**: https://kubernetes.default.svc
- **Namespace**: hello-app-ci que acabamos de criar

Depois clique em **CREATE** e a aplicação já deve estar disponível!

![appArgocd](img/appArgoCD.png?raw=true)

Espere alguns minutos e verifique se o pod e o service da aplicação foram criados no namespace hello-app-ci:

```
kubectl get pods -n hello-app-ci
kubectl get svc -n hello-app-ci
```

## 6 - Testando a aplicação

Agora para verificar se a aplicação com a imagem que buildamos com o fastAPI está funcionando, precisamos fazer novamente um port-forward em outro terminal em paralelo para disponibilizar a aplicação no navegador.

```
kubectl get svc -n hello-app-ci
kubectl port-forward svc/hello-app-service -n hello-app-ci 8081:8080
```

Agora podemos acessar a URL e verificar que a aplicação está funcionando: http://localhost:8081

![testingApp](img/portForwardFastApiService.png?raw=true)

Agora para verificar se a aplicação está com a automação CI/CD basta ir no repositório **hello-app** e alterar a mensagem do arquivo main.py por exemplo:

![changeMainpy](img/testandoAlteracaoMainpy.png?raw=true)

Depois de commitar a alteração, vá na aba **actions** e execute o **run workflow** novamente para o GitHub Actions buildar a nova imagem da aplicação alterada no dockerHub. Depois do Workflow ser executado o repositório do dockerHub deve ter a imagem da nova aplicação em uma nova versão:

![dockerRegistry2](img/dockerHub2.png?raw=true)

O ArgoCD vai ser encarregado de monitorar o repositório que está com a alteração da nova imagem e lançar os pods da aplicação nova automaticamente.

**Observação**: se o número de replicas do arquivo deployment.yaml for 1, o argocd vai destruir o pod que estava em execução da primeira imagem e criar um novo com a nova imagem, sendo necessário realizar um port-forward para o svc novamente.
**Resolva**: aumentando o número de replicas para a aplicação mudar em real time sem precisar fazer um novo port-forward, porque se o número de pods for maior que 1, o argocd pode derrubar e criar um pod por vez sem derrubar o pod da aplicação antes de criar o pod da nova imagem.

## 7 - Conclusão

Agora os pods/containers estão criados e sincronizados com a imagem que buildamos no dockerHub, se fizermos uma nova alteração na aplicação no repositório **hello-app** e acionarmos o workflow para buildar essa imagem nova, o repositório **manifests-ci-cd** automaticamente vai ser alterado buscando a imagem já atualizada que acabou de ser buildada, e como o ArgoCD está monitorando o repositório dos manifestos, ele vai automaticamente destruir e criar novos pods já com a nova imagem puxada do repositório com o arquivo deployment.

Podemos também verificar os logs do pod da aplicação, assim como realizar um curl para verificar se o conteúdo da aplicação mudou como desejado:

![logsPod](img/logsPod.png?raw=true)

Agora temos a aplicação completa com o build da imagem e a alteração no repositório dos manifestos e no cluster Kubernetes de forma automatizada utilizando de ferramentas em alta no mercado DevOps!

**Nota**: Para fins didáticos foi alterado o **on push** para **workflow_dispatch** como trigger na realização da documentação para ter mais controle das versões da aplicação, já que as alterações foram mínimas, e colocar o trigger como **push** iria dificultar a lógica, já que a documentação também acionaria o trigger. Em cenário de produção poderiamos deixar automatizado sem utilizar o workflow_dispatch!

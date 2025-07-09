✅ 1. Instalar o Azure CLI
🖥️ Windows
Baixe e instale via o instalador oficial:

👉 https://aka.ms/installazurecliwindows

💻 macOS (via Homebrew)
bash
Copiar
Editar
brew update && brew install azure-cli
🐧 Linux (Debian/Ubuntu)
bash
Copiar
Editar
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
✅ 2. Verificar se foi instalado corretamente
Após a instalação, rode:

bash
Copiar
Editar
az --version
Você deve ver algo como:

bash
Copiar
Editar
azure-cli                         2.61.0
✅ 3. Fazer login no Azure
No terminal, digite:

bash
Copiar
Editar
az login
O que acontece:
Ele abrirá uma aba no navegador.

Você vai entrar com seu e-mail e senha da conta Azure.

✅ Depois do login, você verá um JSON com informações da sua conta/subscrição:

json
Copiar
Editar
[
  {
    "cloudName": "AzureCloud",
    "id": "SEU_SUBSCRIPTION_ID",
    "isDefault": true,
    "name": "Nome da Subscrição",
    "tenantId": "SEU_TENANT_ID",
    ...
  }
]
✅ 4. Verificar sua assinatura ativa
bash
Copiar
Editar
az account show
Retorna algo como:

json
Copiar
Editar
{
  "id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "tenantId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  ...
}
Se tudo isso estiver funcionando, o próximo passo é:
bash
Copiar
Editar
az ad sp create-for-rbac --name "my-github-sp" --role contributor \
  --scopes /subscriptions/<SEU_SUBSCRIPTION_ID> \
  --sdk-auth


# ####################################################################################################

✅ 1. Criar um Service Principal no Azure
Esse Service Principal será usado para autenticar no Azure com permissões específicas.

🔧 Comando Azure CLI
Execute isso no terminal (com az CLI instalado e logado):

bash
Copiar
Editar
az ad sp create-for-rbac --name "my-github-sp" --role contributor \
  --scopes /subscriptions/<SEU_SUBSCRIPTION_ID> \
  --sdk-auth
🔁 Substitua <SEU_SUBSCRIPTION_ID> pelo ID da sua assinatura Azure.

Esse comando retorna um JSON assim:

json
Copiar
Editar
{
  "clientId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "clientSecret": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "subscriptionId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "tenantId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  ...
}
✅ 2. Adicionar os valores no GitHub Secrets
🔐 Vá em:
Settings > Secrets and variables > Actions > New repository secret

Adicione cada um desses valores individualmente:

Nome do Secret	Valor (do JSON gerado acima)
ARM_CLIENT_ID	"clientId"
ARM_CLIENT_SECRET	"clientSecret"
ARM_SUBSCRIPTION_ID	"subscriptionId"
ARM_TENANT_ID	"tenantId"

💡 Dica: Exemplo visual no GitHub
Acesse seu repositório no GitHub.

Vá em Settings (⚙️ no topo).

Clique em Secrets and variables > Actions.

Clique em "New repository secret".

No campo Name, coloque ARM_CLIENT_ID.

No campo Secret, cole o valor de clientId do JSON.

Clique em Add secret.

Repita para os outros 3.


# ####################################################################################################


(.github/workflows/deploy.yml) que utiliza os secrets do Azure (ARM_CLIENT_ID, ARM_CLIENT_SECRET, ARM_SUBSCRIPTION_ID, ARM_TENANT_ID) para autenticar e fazer deploy de infraestrutura usando Terraform, o caso mais comum com esses secrets.

✅ Exemplo: deploy.yml usando Terraform no Azure
yaml
Copiar
Editar
name: Deploy Infra to Azure

on:
  push:
    branches:
      - main

permissions:
  id-token: write
  contents: read

jobs:
  terraform:
    name: Terraform Plan & Apply
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: 1.7.5

      - name: Terraform Init
        run: terraform init
        env:
          ARM_CLIENT_ID: ${{ secrets.ARM_CLIENT_ID }}
          ARM_CLIENT_SECRET: ${{ secrets.ARM_CLIENT_SECRET }}
          ARM_SUBSCRIPTION_ID: ${{ secrets.ARM_SUBSCRIPTION_ID }}
          ARM_TENANT_ID: ${{ secrets.ARM_TENANT_ID }}

      - name: Terraform Plan
        run: terraform plan
        env:
          ARM_CLIENT_ID: ${{ secrets.ARM_CLIENT_ID }}
          ARM_CLIENT_SECRET: ${{ secrets.ARM_CLIENT_SECRET }}
          ARM_SUBSCRIPTION_ID: ${{ secrets.ARM_SUBSCRIPTION_ID }}
          ARM_TENANT_ID: ${{ secrets.ARM_TENANT_ID }}

      - name: Terraform Apply
        if: github.ref == 'refs/heads/main'
        run: terraform apply -auto-approve
        env:
          ARM_CLIENT_ID: ${{ secrets.ARM_CLIENT_ID }}
          ARM_CLIENT_SECRET: ${{ secrets.ARM_CLIENT_SECRET }}
          ARM_SUBSCRIPTION_ID: ${{ secrets.ARM_SUBSCRIPTION_ID }}
          ARM_TENANT_ID: ${{ secrets.ARM_TENANT_ID }}
🧠 Explicação rápida
Esse workflow roda no push para a branch main.

Usa os secrets para autenticar no Azure.

Executa terraform init, plan e apply automaticamente.

Garante que as credenciais Azure estejam disponíveis nas variáveis de ambiente.

✅ Pré-requisitos
Antes de isso funcionar, você precisa garantir que:

Os secrets estejam corretamente configurados no repositório.

Haja um projeto Terraform válido no repositório com:

main.tf

variables.tf

terraform.tfvars (opcional)

O terraform init consiga encontrar seu provider Azure, algo como:

hcl
Copiar
Editar
provider "azurerm" {
  features {}
}

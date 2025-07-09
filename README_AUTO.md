# Airflow Azure Deploy

# Airflow na Azure com Docker, Terraform e GitHub Actions

Este guia profissional configura um ambiente completo com Apache Airflow usando:

* Azure Virtual Machine (Ubuntu)
* Docker + Docker Compose
* Terraform (IaC)
* GitHub Actions (CI/CD)
* VS Code (ambiente de desenvolvimento)

---

## 1. Estrutura de Pastas

```bash
mkdir airflow-azure-deploy && cd airflow-azure-deploy

mkdir dags data terraform .github .github/workflows

touch docker-compose.yml .env

# Terraform
cd terraform && touch main.tf variables.tf outputs.tf init.sh && cd ..

# GitHub Actions
cd .github/workflows && touch deploy.yml && cd ../../
```

---

## 2. docker-compose.yml

```yaml
data:
version: '3.8'

services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow
    volumes:
      - postgres_db:/var/lib/postgresql/data

  redis:
    image: redis:latest

  airflow-webserver:
    image: apache/airflow:2.7.2
    environment:
      AIRFLOW__CORE__EXECUTOR: CeleryExecutor
      AIRFLOW__CORE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
      AIRFLOW__CELERY__BROKER_URL: redis://redis:6379/0
      AIRFLOW__CELERY__RESULT_BACKEND: db+postgresql://airflow:airflow@postgres/airflow
      AIRFLOW__CORE__FERNET_KEY: 'YOUR_FERNET_KEY'
      AIRFLOW__CORE__LOAD_EXAMPLES: 'False'
    depends_on:
      - postgres
      - redis
    ports:
      - "8080:8080"
    volumes:
      - ./dags:/opt/airflow/dags
      - ./data:/opt/airflow/data
    command: webserver

  airflow-scheduler:
    image: apache/airflow:2.7.2
    depends_on:
      - airflow-webserver
    command: scheduler
    environment:
      AIRFLOW__CORE__EXECUTOR: CeleryExecutor
      AIRFLOW__CORE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
      AIRFLOW__CELERY__BROKER_URL: redis://redis:6379/0
      AIRFLOW__CELERY__RESULT_BACKEND: db+postgresql://airflow:airflow@postgres/airflow
    volumes:
      - ./dags:/opt/airflow/dags
      - ./data:/opt/airflow/data

volumes:
  postgres_db:
```

---

## 3. DAG de Exemplo: `dags/merge_csv_txt_to_parquet.py`

```python
import pandas as pd
import os

def merge_and_convert():
    csv_path = '/opt/airflow/data/input.csv'
    txt_path = '/opt/airflow/data/input.txt'
    df_csv = pd.read_csv(csv_path)
    df_txt = pd.read_csv(txt_path)
    df = pd.concat([df_csv, df_txt], ignore_index=True)
    df.to_parquet('/opt/airflow/data/output.snappy.parquet', compression='snappy')

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

default_args = {
    'start_date': datetime(2023, 1, 1),
}

dag = DAG('merge_csv_txt_to_parquet', default_args=default_args, schedule_interval=None, catchup=False)

merge_task = PythonOperator(
    task_id='merge_and_save',
    python_callable=merge_and_convert,
    dag=dag,
)
```

---

## 4. Terraform: `terraform/variables.tf`

```hcl
variable "resource_group" { default = "airflow-rg" }
variable "location"       { default = "eastus" }
variable "vm_name"        { default = "airflow-vm" }
variable "admin_username" { default = "azureuser" }
variable "admin_password" {}
```

### `terraform/main.tf`

```hcl
provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "main" {
  name     = var.resource_group
  location = var.location
}

resource "azurerm_virtual_network" "vnet" {
  name                = "airflow-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name
}

resource "azurerm_subnet" "subnet" {
  name                 = "airflow-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.0.1.0/24"]
}

resource "azurerm_public_ip" "pip" {
  name                = "airflow-ip"
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name
  allocation_method   = "Dynamic"
}

resource "azurerm_network_interface" "nic" {
  name                = "airflow-nic"
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.subnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.pip.id
  }
}

resource "azurerm_linux_virtual_machine" "vm" {
  name                = var.vm_name
  resource_group_name = var.resource_group
  location            = var.location
  size                = "Standard_B2s"
  admin_username      = var.admin_username
  admin_password      = var.admin_password
  disable_password_authentication = false
  network_interface_ids = [azurerm_network_interface.nic.id]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts"
    version   = "latest"
  }

  custom_data = base64encode(file("${path.module}/init.sh"))
}
```

### `terraform/outputs.tf`

```hcl
output "public_ip" {
  value = azurerm_public_ip.pip.ip_address
}
```

### `terraform/init.sh`

```bash
#!/bin/bash
apt update && apt install -y docker.io docker-compose git
usermod -aG docker azureuser
cd /home/azureuser
rm -rf airflow-deploy

git clone https://github.com/SEU_USUARIO/airflow-azure-deploy.git airflow-deploy
cd airflow-deploy

docker-compose up -d
```

---

## 5. GitHub Actions `.github/workflows/deploy.yml`

```yaml
name: Terraform Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    env:
      ARM_CLIENT_ID: ${{ secrets.ARM_CLIENT_ID }}
      ARM_CLIENT_SECRET: ${{ secrets.ARM_CLIENT_SECRET }}
      ARM_SUBSCRIPTION_ID: ${{ secrets.ARM_SUBSCRIPTION_ID }}
      ARM_TENANT_ID: ${{ secrets.ARM_TENANT_ID }}
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3

      - name: Terraform Init
        run: terraform init
        working-directory: terraform

      - name: Terraform Apply
        run: terraform apply -auto-approve
        working-directory: terraform
```

---

## 6. Configurar Secrets no GitHub

Adicione em **Settings > Secrets and variables > Actions > New repository secret**:

* `ARM_CLIENT_ID`
* `ARM_CLIENT_SECRET`
* `ARM_SUBSCRIPTION_ID`
* `ARM_TENANT_ID`

Esses valores vêm da criação de um **Service Principal** no Azure.

---

## 7. Executar local ou via CI

```bash
cd terraform
terraform init
terraform apply
```

Ou apenas **faça push no GitHub** para `main` e o CI/CD executará.

---

## 8. Acessar o Airflow

```txt
http://<IP_PUBLICO>:8080
```

Use `admin` / `admin` se configurado no Dockerfile (ou adicione via CLI Airflow).

---

Sistema completo, modular e pronto para escalar em produção.

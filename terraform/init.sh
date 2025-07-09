#!/bin/bash
apt update && apt install -y docker.io docker-compose git
usermod -aG docker azureuser
cd /home/azureuser
rm -rf airflow-deploy

git clone https://github.com/rbezerrabjj/airflow-azure-deploy.git airflow-deploy
cd airflow-deploy

docker-compose up -d

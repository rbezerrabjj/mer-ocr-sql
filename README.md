# Projeto (Mock) em construção (pipeline)

Informações LBC

1. Pedro Lima (Partner LBC / Gestor de Projetos AMA - https://www.ama.gov.pt/ - Agencia para Modernização Administrativa - Portal de entidade pública) 
    - Necessário login com e-mail e senha
    - Livro Amarelo: Zona de reclamações, elogios, sugestões, etc (Livro Amarelo para Governo/exclusivo da AMA) 
    # O Livro Vermelho (não usamos)

2. Pedro Martins (Data Analyst - Projeto: GIAP - Líder)
    - Time:
        - Rodrigo -> Data Analyst (Python + SQL)
        - Francisco -> Data Analyst (Power BI)
        - Raquel -> BA (Business Analyst)
        - Kimberlin -> UX/UI
        - Davi -> BA (Está de saída - meio para final do mês de Julho)
        - Isabel -> Data Analyst

3. João Mateus (Manager do Projeto GIAP - Gestão Inteligente do Atendimento Publico)

4. Duvidas de pessoal e entendimento - Carlos Lopes (Product Manager) ou Yasmin (Desbloqueio/Product Manager)

5. Jorge Serro (AMA - Ponto Focal - Também desenvolve dahs, etc - mais técnico/sênior)

6. Serviços PRR (nutricionistas, saude, solicitar alteração de morada a nível multicanais [portal, app, presencialmente, etc]) - PRR -> Plano de Reestruturação e Resiliência (financiamentos tecnológico, climático, etc)

7. Outras tecnologias utilizadas no dia a dia:
    - Airflow
    - TicAPP (Sharepoint da AMA)
    - Confluence

# ########################################################################################

# MER OCR to SQL Script

Este projeto converte imagens contendo **modelos de dados relacionais (MER)** em comandos SQL compatíveis com o **MySQL Workbench**, utilizando **OCR com Tesseract**.

## 📷 Exemplo de entrada

Uma imagem contendo o modelo de dados com tabelas, campos e tipos (como JPEG, PNG etc).

## ⚙️ Tecnologias utilizadas

- Python 3
- OpenCV
- Pytesseract
- Tesseract OCR Engine

## 🚀 Como usar

### 1. Instale o Tesseract OCR

Baixe e instale o [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) e adicione ao PATH.  
Exemplo de caminho no Windows:

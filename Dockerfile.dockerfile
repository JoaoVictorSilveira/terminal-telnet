# Usar imagem base do Python
FROM python:3.10-slim

# Configurar diretório de trabalho no container
WORKDIR /app

# Copiar os arquivos necessários para o container
COPY requirements.txt .
COPY app.py .
COPY templates ./templates

# Instalar as dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt

# Expor a porta 5000 para acesso externo
EXPOSE 5000

# Comando para iniciar a aplicação
CMD ["python", "app.py"]

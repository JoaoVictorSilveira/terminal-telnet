# Usar a imagem oficial do Python
FROM python:3.12-slim

# Definir diretório de trabalho
WORKDIR /app

# Copiar requirements (se tiver) e app.py
COPY app.py /app/

# Instalar dependências
RUN pip install --no-cache-dir flask

# Expõe a porta que o Flask usará
EXPOSE 5000

# Comando para rodar o Flask
CMD ["python", "app.py"]

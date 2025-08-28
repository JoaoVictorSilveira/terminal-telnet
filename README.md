## Estrutura do Projeto

```
/app
├─ app.py
├─ templates/
│ └─ index.html
└─ Dockerfile
```
## Buildar imagem

docker build -t telnet-console .

## Rodar Container
docker run -d -p 5000:5000 --name console-telnet console-telnet

##Acesse via navegador na porta 5000

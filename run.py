from app import create_app

# O que faz: 
#   É o ponto de partida (entry point) do nosso backend. É este ficheiro que o terminal ou o VS Code executa para "ligar" o servidor.
# Como faz: 
#   Importa a função "create_app" da nossa pasta "app", cria a instância da aplicação e executa o servidor na porta 5000 com o modo de depuração (debug) ativo (o que faz o servidor reiniciar sozinho sempre que guardamos uma alteração no código).

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
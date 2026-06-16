from flask import Flask

app = Flask(__name__, static_folder='client', static_url_path='')


@app.route('/')
def index():
    return app.send_static_file('index.html')


if __name__ == '__main__':
    # debug=True habilita el recargador automático para ver cambios sin reiniciar manualmente
    app.run(debug=True, host='0.0.0.0', port=5000)

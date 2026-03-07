from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    # Tryb debug = True jest idealny na hackathonie, bo odświeża apkę po zapisaniu pliku
    app.run(debug=True)

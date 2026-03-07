from flask import Flask, render_template

# Wskazujemy Flaskowi poprawny folder z szablonami
app = Flask(__name__, template_folder='website/templates')

@app.route('/')
def home():
    return render_template('index.html')

# Kiedy JS robi fetch('QA.html'), Flask przechwytuje to tutaj
@app.route('/<module_name>')
def serve_module(module_name):
    # Sprawdzamy, czy plik kończy się na .html, żeby było bezpieczniej
    if module_name.endswith('.html'):
        return render_template(module_name)
    return "Nie znaleziono", 404

if __name__ == '__main__':
    app.run(debug=True)

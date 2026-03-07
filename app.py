from flask import Flask, render_template, request, jsonify
from models import db, School, Olimpiada, Wydarzenie, OpenDay
from datetime import datetime
import os

# Wskazujemy Flaskowi poprawny folder z szablonami
app = Flask(__name__, template_folder='website/templates')

# Konfiguracja bazy danych SQLite - w głównym katalogu projektu
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./scoolmatch.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicjalizacja bazy danych
db.init_app(app)

@app.route('/')
def home():
    # Tworzymy tabele przy pierwszym załadowaniu
    db.create_all()

    # Dodajemy przykładowe dane, jeśli baza jest pusta
    if School.query.count() == 0:
        example_schools = [
            School(nazwa='I Liceum Ogólnokształcące im. Adama Mickiewicza', lokalizacja='Śródmieście', specjalnosci='Matematyka, Fizyka, Historia', typ='Liceum', internat=True, odleglosc=2.5),
            School(nazwa='II Liceum Ogólnokształcące im. Króla Stanisława Leszczyńskiego', lokalizacja='Wrzeszcz', specjalnosci='Języki obce, Literatura', typ='Liceum', internat=False, odleglosc=4.2),
            School(nazwa='III Liceum Ogólnokształcące', lokalizacja='Oliwa', specjalnosci='Biologia, Chemia', typ='Liceum', internat=False, odleglosc=8.5),
            School(nazwa='Technikum Elektroniczne im. Józefa Marii Fitelberga', lokalizacja='Śródmieście', specjalnosci='Elektronika, Robotyka', typ='Technikum', internat=True, odleglosc=2.8),
            School(nazwa='Technikum Informacyjne', lokalizacja='Wrzeszcz', specjalnosci='Programowanie, Sieci komputerowe', typ='Technikum', internat=False, odleglosc=4.5),
            School(nazwa='Szkoła Zawodowa nr 1', lokalizacja='Oliwa', specjalnosci='Automechanika, Elektyka', typ='Szkoła zawodowa', internat=False, odleglosc=8.0),
            School(nazwa='IV Liceum Ogólnokształcące', lokalizacja='Kokoszki', specjalnosci='Ekonomia, Zarządzanie', typ='Liceum', internat=False, odleglosc=6.3),
            School(nazwa='Technikum Mechaniczne', lokalizacja='Śródmieście', specjalnosci='Budowa maszyn, CNC', typ='Technikum', internat=True, odleglosc=3.1),
            School(nazwa='Szkoła Zawodowa nr 2', lokalizacja='Wrzeszcz', specjalnosci='Kosmetyka, Fryzjerstwo', typ='Szkoła zawodowa', internat=False, odleglosc=4.0),
            School(nazwa='V Liceum Ogólnokształcące', lokalizacja='Przymorze', specjalnosci='Sztuka, Muzyka, Historia', typ='Liceum', internat=True, odleglosc=7.2),
        ]
        db.session.add_all(example_schools)
        db.session.commit()

    return render_template('index.html')

# Kiedy JS robi fetch('QA.html'), Flask przechwytuje to tutaj
@app.route('/<module_name>')
def serve_module(module_name):
    # Sprawdzamy, czy plik kończy się na .html, żeby było bezpieczniej
    if module_name.endswith('.html'):
        return render_template(module_name)
    return "Nie znaleziono", 404


@app.route('/schools')
def schools_view():
   schools = School.query.all()
   return render_template('school_view.html', schools=schools)

@app.route('/get-specialties')
def get_specialties():
    """Endpoint zwracający wszystkie unikalne specjalności z bazy danych"""
    schools = School.query.all()
    specialties = set()

    # Zbieramy wszystkie specjalności z każdej szkoły (oddzielone przecinkami)
    for school in schools:
        if school.specjalnosci:
            # Dzielimy po przecinku i usuwamy whitespace
            specs = [spec.strip() for spec in school.specjalnosci.split(',')]
            specialties.update(specs)

    # Sortujemy alfabetycznie
    specialties_list = sorted(list(specialties))

    return jsonify({'specialties': specialties_list})

@app.route('/filter-schools', methods=['POST'])
def filter_schools():
    """Endpoint do filtrowania szkół na podstawie kryteriów"""
    data = request.get_json()

    # Pobieramy parametry filtrowania
    school_type = data.get('type', '')
    specialties = data.get('specialties', [])
    has_dorm = data.get('dormitory', '')
    max_distance = data.get('distance', 50)

    # Budujemy zapytanie
    query = School.query

    # Filtrowanie po typie szkoły
    if school_type:
        query = query.filter_by(typ=school_type)

    # Filtrowanie po specjalnościach (szkoła musi mieć przynajmniej jedną z wybranych specjalności)
    if specialties:
        # Tworzymy warunki OR dla każdej specjalności
        specialty_conditions = []
        for specialty in specialties:
            specialty_conditions.append(School.specjalnosci.contains(specialty))
        # Łączymy warunki OR
        from sqlalchemy import or_
        query = query.filter(or_(*specialty_conditions))

    # Filtrowanie po internecie/bursie
    if has_dorm == 'Tak':
        query = query.filter_by(internat=True)
    elif has_dorm == 'Nie':
        query = query.filter_by(internat=False)

    # Filtrowanie po odległości
    try:
        max_distance = float(max_distance)
        query = query.filter(School.odleglosc <= max_distance)
    except (ValueError, TypeError):
        pass

    schools = query.all()

    # Zwracamy wyniki jako HTML
    result_html = ''
    if schools:
        for school in schools:
            internat_badge = '<span class="badge bg-success">Internat</span>' if school.internat else '<span class="badge bg-danger">Bez internatu</span>'
            specjalnosci_html = f'<div class="small text-muted mt-2"><strong>Specjalności:</strong> {school.specjalnosci}</div>'
            result_html += f'''<li class="list-group-item">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <strong>{school.nazwa}</strong>
                        <div class="small text-muted mt-1">
                            <span class="badge bg-secondary">{school.typ}</span>
                            {internat_badge}
                        </div>
                        {specjalnosci_html}
                    </div>
                    <div class="text-end">
                        <small class="text-muted">{school.odleglosc} km</small>
                    </div>
                </div>
            </li>'''
    else:
        result_html = '<li class="list-group-item text-muted">Brak szkół spełniających kryteria.</li>'

    return jsonify({'html': result_html})

if __name__ == '__main__':
    app.run(debug=True)

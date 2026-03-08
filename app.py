from flask import Flask, render_template, request, jsonify
from models import db, School, Olimpiada, Wydarzenie, OpenDay
from datetime import datetime, timedelta
import json
import os

# Wskazujemy Flaskowi poprawny folder z szablonami
app = Flask(__name__, template_folder='website/templates', static_folder='website/static')

# Konfiguracja bazy danych SQLite - w głównym katalogu projektu
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./scoolmatch.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicjalizacja bazy danych
db.init_app(app)
holland_descriptions = {
    "R": {
        "nazwa": "Typ realistyczny/praktyczny",
        "opis": "Osoby o takim typie osobowości zawodowej są przedstawiane jako konkretne, praktyczne, prostolinijne, systematyczne. W pracy wykorzystują uzdolnienia manualne, lubią konstruować, budować, mieć do czynienia z maszynami. Dążą do skonkretyzowania, czego się od nich oczekuje, co ma być wykonane.",
        "praca": "Rekomendowane rodzaje prac - produkcyjna, usługowa, sportowa.",
        "zawody": "Przykładowe zawody - murarz, elektryk, kierowca, stolarz, technik laboratorium, mechanik, jubiler, hydraulik."
    },
    "B": {
        "nazwa": "Typ badawczy",
        "opis": "Osoby o takim typie osobowości zawodowej są określane jako analityczne, dociekliwe, precyzyjne, konkretne, o szerokim umyśle, ciekawe zjawisk, racjonalne, niezależne, mające zmysł obserwacji. Lubią diagnozować, badać, obserwować, poznawać, rozumieć sedno problemu. Dobrze odnajdują się w pracy koncepcyjnej, samodzielnej, wymagającej logiki myślenia.",
        "praca": "Rekomendowane rodzaje prac - poznawcza, informacyjna.",
        "zawody": "Przykładowe zawody - analityk rynku, matematyk, programista, biolog, anestezjolog, konsultant, ekonomista."
    },
    "A": {
        "nazwa": "Typ artystyczny",
        "opis": "Osoby o takim typie osobowości zawodowej mają zdolności i preferencje artystyczne, są innowacyjne, niekonformistyczne, impulsywne, niestandardowe, opierające się na intuicji, wrażliwe. Decyzje podejmują „na wyczucie”, preferują zadania kreatywne, wolą pracować nad ideami, koncepcjami niż nad konkretnymi produktami.",
        "praca": "Rekomendowane rodzaje prac - artystyczna, twórcza.",
        "zawody": "Przykładowe zawody - szef reklamy, projektant mebli: mebli, mody, wnętrz, terenów zielonych, tancerz, grafik, pisarz, malarz, fotograf."
    },
    "S": {
        "nazwa": "Typ społeczny - socjalny",
        "opis": "Osoby o takim typie osobowości zawodowej są określane jako taktowne, hojne, pomocne, uprzejme, współpracujące, rozumiejące. Preferują pracę bezpośrednio związane z ludźmi. Lubią wyjaśniać, informować, szkolić, pomagać, doradzać.",
        "praca": "Rekomendowane rodzaje prac - organizacyjna, wychowawcza, opiekuńcza, usługowa, sportowa.",
        "zawody": "Przykładowe zawody - terapeuta, kosmetyczka, nauczyciel, szkoleniowiec, szef personalny, lekarz, pielęgniarka, pracownik socjalny."
    },
    "P": {
        "nazwa": "Typ przedsiębiorczy",
        "opis": "Osoby o takim typie osobowości zawodowej są energiczne, optymistyczne, entuzjastyczne, ekstrawertyczne, patrzące perspektywicznie, łatwo wyznaczające zadania, pociągające ludzi do osiągnięcia wyznaczonego celu, wywierające wpływ, mające wymierne osiągnięcia. Osoby takie lubią mówić, promować, sprzedawać, przewodzić, przekonywać.",
        "praca": "Rekomendowane rodzaje prac - organizacyjna, usługowa.",
        "zawody": "Przykładowe zawody - menedżer ds. kluczowych klientów, przedstawiciel handlowy, dziennikarz, agent ubezpieczeniowy, szef marketingu, szef sprzedaży."
    },
    "K": {
        "nazwa": "Typ konwencjonalny",
        "opis": "Osoby o takim typie osobowości zawodowej są określane jako metodyczne, precyzyjne, praktyczne, systematyczne. Preferują pracę z danymi liczbowymi, przestrzeganie procedur, organizowanie i porządkowanie danych, korzystanie z programów obliczeniowych.",
        "praca": "Rekomendowane rodzaje prac - organizacyjna, porządkowa, informacyjna.",
        "zawody": "Przykładowe zawody - urzędnik, sekretarka, pracownik biurowy, doradca podatkowy, kasjer, księgowy."
    }
}

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

    if Olimpiada.query.count() == 0:
        biologia_arkusze = [
            {"nazwa": "Arkusz - Etap I (Szkolny)",
             "url": "/static/arkusz-zadan-z-biologii-stopien-i-szkolny-–-2024-2025.pdf"},
            {"nazwa": "Model - Etap I",
             "url": "/static/model-odpowiedzi-do-zadan-z-biologii-stopien-i-szkolny-2024-2025.pdf"},
            {"nazwa": "Arkusz - Etap II (Rejonowy)",
             "url": "/static/arkusz-zadan-z-biologii-stopien-ii-rejonowy-2024-2025.pdf"},
            {"nazwa": "Model - Etap II",
             "url": "/static/model-odpowiedzi-do-zadan-z-biologii-stopien-ii-rejonowy-2024-2025.pdf"},
            {"nazwa": "Arkusz - Etap III (Wojewódzki)",
             "url": "/static/arkusz-zadan-z-biologii-stopien-iiii-wojewodzki-–-2024-2025.pdf"},
            {"nazwa": "Model - Etap III",
             "url": "/static/model-odpowiedzi-do-zadan-z-biologii-stopien-iii-wojewodzki-2024-2025.pdf"}
        ]

        example_olimpiady = [
            Olimpiada(nazwa='Olimpiada Matematyczna Juniorów', data=datetime.now() + timedelta(days=30),
                      pdf='/arkusze/omj_2024.pdf'),
            Olimpiada(nazwa='Olimpiada Literatury i Języka Polskiego', data=datetime.now() + timedelta(days=45),
                      pdf='/arkusze/olijp_2024.pdf'),
            Olimpiada(nazwa='Wojewódzki Konkurs Kuratoryjny z Biologii', data=datetime.now() + timedelta(days=15),
                      pdf=json.dumps(biologia_arkusze)),
            Olimpiada(nazwa='Olimpiada Informatyczna Juniorów', data=datetime.now() + timedelta(days=60),
                      pdf='/arkusze/oij_2024.pdf')
        ]
        db.session.add_all(example_olimpiady)
        db.session.commit()
        
    if Wydarzenie.query.count() == 0:
        example_events = [
            Wydarzenie(typ="Dni Otwarte", nazwa_wydarzenia="Dni Otwarte - Profil Informatyczny", data=datetime(2026, 3, 14, 10, 0), szkola="Technikum Łączności nr 4 w Gdańsku", odleglosc=4.5),
            Wydarzenie(typ="Warsztaty", nazwa_wydarzenia="Warsztaty: Zbuduj swojego robota", data=datetime(2026, 3, 21, 12, 0), szkola="Zespół Szkół Chłodniczych i Elektronicznych", odleglosc=8.2),
            Wydarzenie(typ="Doradztwo", nazwa_wydarzenia="Spotkanie z doradcą zawodowym", data=datetime(2026, 3, 25, 15, 0), szkola="Centrum Kształcenia Zawodowego", odleglosc=2.1),
            Wydarzenie(typ="Dni Otwarte", nazwa_wydarzenia="Dzień Otwarty - Klasy mundurowe", data=datetime(2026, 4, 5, 9, 0), szkola="Liceum Ogólnokształcące nr VII", odleglosc=12.0),
            Wydarzenie(typ="Targi", nazwa_wydarzenia="Targi Edukacyjne Trójmiasta", data=datetime(2026, 4, 10, 10, 0), szkola="AmberExpo Gdańsk", odleglosc=6.5),
            Wydarzenie(typ="Dni Otwarte", nazwa_wydarzenia="Poznaj szkołę morską", data=datetime(2026, 4, 18, 11, 0), szkola="Zespół Szkół Morskich", odleglosc=3.0),
            Wydarzenie(typ="Dni Otwarte", nazwa_wydarzenia="Dni Otwarte Technikum Leśnego", data=datetime(2026, 4, 22, 9, 0), szkola="Technikum Leśne (Sopot)", odleglosc=18.5),
            Wydarzenie(typ="Warsztaty", nazwa_wydarzenia="Warsztaty gastronomiczne", data=datetime(2026, 5, 10, 10, 0), szkola="Zespół Szkół Gastronomicznych (Gdynia)", odleglosc=25.0)
        ]
        db.session.add_all(example_events)
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


@app.route('/olimpiady')
def olimpiady_view():
    olimpiady = Olimpiada.query.order_by(Olimpiada.data.asc()).all()

    # Przetwarzamy pole pdf na łatwą w obsłudze listę
    for olimpiada in olimpiady:
        if olimpiada.pdf and olimpiada.pdf.startswith('['):
            try:
                olimpiada.arkusze_list = json.loads(olimpiada.pdf)
            except json.JSONDecodeError:
                olimpiada.arkusze_list = [{"nazwa": "Zobacz arkusze z poprzednich lat", "url": olimpiada.pdf}]
        elif olimpiada.pdf:
            olimpiada.arkusze_list = [{"nazwa": "Zobacz arkusze z poprzednich lat", "url": olimpiada.pdf}]
        else:
            olimpiada.arkusze_list = []

    return render_template('olimpiady.html', olimpiady=olimpiady)
@app.route('/api/events')
def api_events():
    events = Wydarzenie.query.all()
    result = []
    
    for ev in events:
        # Dobieramy ikonę Bootstrapa na podstawie typu wydarzenia
        icon = "bi-calendar-event"
        if ev.typ == "Dni Otwarte": icon = "bi-door-open"
        elif ev.typ == "Warsztaty": icon = "bi-tools"
        elif ev.typ == "Doradztwo": icon = "bi-person-badge"
        elif ev.typ == "Targi": icon = "bi-mega-phone"

        result.append({
            "id": ev.id,
            "title": ev.nazwa_wydarzenia,
            "school": ev.szkola or "Brak lokalizacji",
            "date": ev.data.strftime('%Y-%m-%d'),
            "distance": ev.odleglosc or 0.0,
            "type": ev.typ,
            "icon": icon
        })
        
    return jsonify(result)

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
@app.route('/api/oblicz-wynik', methods=['POST'])
def oblicz_wynik():
    # Pobranie danych JSON wysłanych z frontendu
    answers = request.get_json()

    if not answers:
        return jsonify({"error": "Brak danych"}), 400

    # Inicjacja liczników
    scores = {'R': 0, 'B': 0, 'A': 0, 'S': 0, 'P': 0, 'K': 0}

    # Przeliczanie odpowiedzi
    for question_id, answer in answers.items():
        if answer == "tak":
            # question_id ma format "R_q1", więc pierwsza litera to typ
            category = question_id[0]
            if category in scores:
                scores[category] += 1

    # Sortowanie wyników malejąco i wybór najwyższego
    # scores.items() zwraca krotki (typ, punkty), sortujemy po punktach
    sorted_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)

    top_type_key = sorted_scores[0][0]
    top_score = sorted_scores[0][1]
    result_data = holland_descriptions.get(top_type_key)

    # Zwrócenie wyniku jako JSON
    return jsonify({
        "topType": top_type_key,
        "score": top_score,
        "details": result_data,
        "allScores": scores
    })

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, jsonify, request


# Wskazujemy Flaskowi poprawny folder z szablonami
app = Flask(__name__, template_folder='website/templates')

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
    return render_template('index.html')

# Kiedy JS robi fetch('QA.html'), Flask przechwytuje to tutaj
@app.route('/<module_name>')
def serve_module(module_name):
    # Sprawdzamy, czy plik kończy się na .html, żeby było bezpieczniej
    if module_name.endswith('.html'):
        return render_template(module_name)
    return "Nie znaleziono", 404


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

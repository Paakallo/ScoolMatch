from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class School(db.Model):
    """Tabela szkół"""
    __tablename__ = 'school'

    id = db.Column(db.Integer, primary_key=True)
    nazwa = db.Column(db.String(255), nullable=False)
    lokalizacja = db.Column(db.String(255), nullable=False)
    specjalnosci = db.Column(db.String(500), nullable=True)  # np. "Informatyka, Elektronika"
    typ = db.Column(db.String(100), nullable=True)  # Liceum, Technikum, Szkoła zawodowa
    internat = db.Column(db.Boolean, default=False)  # Czy szkoła ma internat
    odleglosc = db.Column(db.Float, nullable=True)  # Odległość od centrum Gdańska (km)

    # Relacje
    open_days = db.relationship('OpenDay', backref='school', lazy=True)

    def __repr__(self):
        return f'<School {self.nazwa}>'


class Olimpiada(db.Model):
    """Tabela olimpiad"""
    __tablename__ = 'olimpiada'

    id = db.Column(db.Integer, primary_key=True)
    nazwa = db.Column(db.String(255), nullable=False)
    data = db.Column(db.DateTime, nullable=False)
    pdf = db.Column(db.String(255), nullable=True)  # Ścieżka do pliku PDF

    def __repr__(self):
        return f'<Olimpiada {self.nazwa}>'


class Wydarzenie(db.Model):
    """Tabela wydarzeń"""
    __tablename__ = 'wydarzenie'

    id = db.Column(db.Integer, primary_key=True)
    typ = db.Column(db.String(100), nullable=False)  # np. "Konferencja", "Warsztaty"
    nazwa_wydarzenia = db.Column(db.String(255), nullable=False)
    data = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<Wydarzenie {self.nazwa_wydarzenia}>'


class OpenDay(db.Model):
    """Tabela dni otwartych"""
    __tablename__ = 'open_day'

    id = db.Column(db.Integer, primary_key=True)
    id_szkoly = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)
    data = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<OpenDay School={self.id_szkoly} Data={self.data}>'


from datetime import datetime

from app.extensions import db


class Pesquisa(db.Model):
    __tablename__ = "pesquisa"

    id = db.Column(db.Integer, primary_key=True)
    morada = db.Column(db.String(255), nullable=False)
    categoria = db.Column(db.String(80), nullable=False)
    modo_deslocacao = db.Column(db.String(40), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    data_pesquisa = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Pesquisa {self.id} - {self.categoria}>"

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from app.extensions import db


class Pesquisa(db.Model):
    __tablename__ = "pesquisa"

    FUSO_HORARIO_LOCAL = ZoneInfo("Europe/Lisbon")

    id = db.Column(db.Integer, primary_key=True)
    morada = db.Column(db.String(255), nullable=False)
    categoria = db.Column(db.String(80), nullable=False)
    modo_deslocacao = db.Column(db.String(40), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    data_pesquisa = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    @property
    def data_pesquisa_local(self) -> datetime:
        
        return self.data_pesquisa.replace(tzinfo=timezone.utc).astimezone(self.FUSO_HORARIO_LOCAL)

from src.models.user import db
from datetime import datetime

class LinkUtil(db.Model):
    __tablename__ = "links_uteis"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    titulo = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(2000), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    categoria = db.Column(db.String(100), nullable=True)
    data_criacao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<LinkUtil {self.id} - {self.titulo}>"

    def to_dict(self):
        return {
            "id": self.id,
            "titulo": self.titulo,
            "url": self.url,
            "descricao": self.descricao,
            "categoria": self.categoria,
            "data_criacao": self.data_criacao.isoformat()
        }

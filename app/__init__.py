import os

from flask import Flask, render_template

from .extensions import db


def create_app():
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
        instance_relative_config=True,
    )

    os.makedirs(app.instance_path, exist_ok=True)

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(app.instance_path,"aroundme.db",)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    from . import models
    from .routes import main_bp

    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()

    @app.errorhandler(404)
    def pagina_nao_encontrada(erro):
        return render_template("erro.html", mensagem = "A pagina que procuras nao existe.",), 404

    @app.errorhandler(500)
    def erro_interno(erro):
        db.session.rollback()
        return render_template("erro.html", mensagem= "Ocorreu um erro inesperado. Tenta novamente mais tarde.",), 500

    return app

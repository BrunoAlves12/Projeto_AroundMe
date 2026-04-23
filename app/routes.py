import folium

from flask import Blueprint, render_template, request
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.geoapify import AroundMeErro, pesquisar_servicos
from app.models import Pesquisa


main_bp = Blueprint("main", __name__)


def criar_mapa_resultados(referencia: str, latitude: float, longitude: float, locais: list[dict]) -> str:
    mapa = folium.Map(location=[latitude, longitude], zoom_start=14, control_scale=True)

    folium.Marker(
        [latitude, longitude],
        popup=f"<strong>Morada pesquisada</strong><br>{referencia}",
        tooltip="Morada pesquisada",
        icon=folium.Icon(color="blue", icon="home"),).add_to(mapa)

    pontos = [[latitude, longitude]]

    for local in locais:
        local_lat = local.get("lat")
        local_lon = local.get("lon")
        if local_lat is None or local_lon is None:
            continue

        pontos.append([local_lat, local_lon])
        folium.Marker(
            [local_lat, local_lon],
            popup=f"<strong>{local['nome']}</strong><br>{local['morada']}",
            tooltip=local["nome"],
            icon=folium.Icon(color="green", icon="info-sign"),).add_to(mapa)

    if len(pontos) > 1:
        mapa.fit_bounds(pontos, padding=(35, 35))

    return mapa._repr_html_()


def renderizar_pagina_resultados(pesquisa: Pesquisa, dados: dict):
    return render_template(
        "resultados.html",
        pesquisa=pesquisa,
        referencia=dados["referencia"],
        locais=dados["locais"],
        map_html=criar_mapa_resultados(
            referencia=dados["referencia"],
            latitude=dados["latitude"],
            longitude=dados["longitude"],
            locais=dados["locais"],
        ),
    )


def renderizar_historico(mensagem: str | None = None, tipo_mensagem: str = "info", status_code: int = 200):
    pesquisas = Pesquisa.query.order_by(Pesquisa.data_pesquisa.desc()).all()
    return (
        render_template("historico.html", pesquisas=pesquisas, mensagem_historico=mensagem, tipo_mensagem=tipo_mensagem,),status_code,
    )


@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/historico")
def historico():
    try:
        return renderizar_historico()
    except SQLAlchemyError:
        db.session.rollback()
        return render_template("erro.html",mensagem="Nao foi possivel carregar o historico de pesquisas.",), 500


@main_bp.route("/historico/<int:pesquisa_id>/resultados")
def ver_resultados_historico(pesquisa_id: int):
    try:
        pesquisa = db.session.get(Pesquisa, pesquisa_id)
        if pesquisa is None:
            return renderizar_historico(mensagem="A pesquisa selecionada ja nao existe no historico.", tipo_mensagem="erro",status_code=404,)

        dados = pesquisar_servicos(
            pesquisa.morada,
            pesquisa.categoria,
            pesquisa.modo_deslocacao,
        )
        return renderizar_pagina_resultados(pesquisa, dados)
    
    except AroundMeErro as erro:
        db.session.rollback()
        return renderizar_historico(mensagem=f"Nao foi possivel repetir a pesquisa: {erro}", tipo_mensagem="erro", status_code=400,
                                    )
    except SQLAlchemyError:
        db.session.rollback()
        return render_template("erro.html", mensagem="Nao foi possivel aceder ao historico de pesquisas.",), 500
    
    except Exception:
        db.session.rollback()
        return renderizar_historico(mensagem="Ocorreu um erro inesperado ao repetir a pesquisa.", tipo_mensagem="erro", status_code=500,
        )


@main_bp.route("/resultados", methods=["POST"])
def resultados():
    morada = request.form.get("morada", "").strip()
    categoria = request.form.get("categoria", "").strip().lower()
    modo = request.form.get("modo_deslocacao", "").strip().lower()
    valores = {
        "morada": morada,
        "categoria": categoria,
        "modo_deslocacao": modo,
    }

    try:
        dados = pesquisar_servicos(morada, categoria, modo)

        pesquisa = Pesquisa(
            morada=morada,
            categoria=categoria,
            modo_deslocacao=modo,
            latitude=dados["latitude"],
            longitude=dados["longitude"],
        )
        db.session.add(pesquisa)
        db.session.commit()
        return renderizar_pagina_resultados(pesquisa, dados)
    
    except AroundMeErro as erro:
        db.session.rollback()
        return render_template("index.html", erro=str(erro), valores=valores), 400
    
    except SQLAlchemyError:
        db.session.rollback()
        return render_template("erro.html", mensagem="Nao foi possivel guardar a pesquisa no historico.",), 500
    
    except Exception:
        db.session.rollback()
        return render_template("erro.html", mensagem="Ocorreu um erro inesperado ao processar a pesquisa.",), 500

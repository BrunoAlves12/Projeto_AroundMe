import os
import time
from typing import Dict, List, Tuple

import requests


GEOCODE_URL = "https://api.geoapify.com/v1/geocode/search"
PLACES_URL = "https://api.geoapify.com/v2/places"
ROUTING_URL = "https://api.geoapify.com/v1/routing"

REQUEST_TIMEOUT = 20
MIN_INTERVAL_SECONDS = 0.35

CATEGORY_MAP = {
    "farmacia": "healthcare.pharmacy",
    "hospital": "healthcare.hospital",
    "escola": "education.school",
    "supermercado": "commercial.supermarket",
    
}

MODE_MAP = {
    "carro": "drive",
    "a pe": "walk",
    "a_pe": "walk",
    "pe": "walk",
}


class AroundMeErro(Exception):
    pass


SESSION = requests.Session()

LAST_REQUEST_AT: Dict[str, float] = {}
CACHE_GEOCODING: Dict[str, Dict] = {}
CACHE_PLACES: Dict[Tuple[float, float, str, int], List[Dict]] = {}
CACHE_ROUTES: Dict[Tuple[float, float, float, float, str], Dict] = {}


def esperar_intervalo(servico: str) -> None:
    ultimo = LAST_REQUEST_AT.get(servico)
    if ultimo is None:
        return

    decorrido = time.monotonic() - ultimo
    falta = MIN_INTERVAL_SECONDS - decorrido
    if falta > 0:
        time.sleep(falta)


def registar_pedido(servico: str) -> None:
    LAST_REQUEST_AT[servico] = time.monotonic()


def obter_api_key() -> str:
    api_key = os.getenv("GEOAPIFY_API_KEY")
    if not api_key:
        raise AroundMeErro(
            "Nao encontrei a variavel de ambiente GEOAPIFY_API_KEY. "
            "Define a chave antes de usar a pesquisa."
        )
    return api_key.strip()


def validar_categoria(categoria: str) -> str:
    categoria = categoria.strip().lower()
    if not categoria:
        raise AroundMeErro("Tens de escolher uma categoria.")
    if categoria not in CATEGORY_MAP:
        opcoes = ", ".join(sorted({"farmacia", "hospital", "escola", "supermercado"}))
        raise AroundMeErro(f"Categoria invalida. Escolhe uma destas: {opcoes}.")
    return categoria


def validar_modo(modo: str) -> str:
    modo = modo.strip().lower()
    if not modo:
        raise AroundMeErro("Tens de escolher um modo de deslocacao.")
    if modo not in MODE_MAP:
        raise AroundMeErro("Modo invalido. Usa 'a pe' ou 'carro'.")
    return modo


def tratar_resposta(resposta: requests.Response, servico: str) -> None:
    if resposta.status_code == 401:
        raise AroundMeErro(f"Chave invalida ou em falta no servico {servico}.")
    if resposta.status_code == 403:
        raise AroundMeErro(f"Acesso recusado pelo servico {servico}.")
    if resposta.status_code == 429:
        raise AroundMeErro(
            f"O servico {servico} limitou temporariamente os pedidos. "
            "Espera um pouco antes de testar novamente."
        )
    resposta.raise_for_status()


def geoapify_get(servico: str, url: str, params: Dict) -> Dict:
    esperar_intervalo(servico)
    try:
        resposta = SESSION.get(url, params=params, timeout=REQUEST_TIMEOUT)
        registar_pedido(servico)
        tratar_resposta(resposta, servico)
        try:
            return resposta.json()
        except ValueError as erro:
            raise AroundMeErro(f"O servico {servico} devolveu uma resposta invalida.") from erro
    except requests.Timeout as erro:
        raise AroundMeErro(f"O pedido ao servico {servico} demorou demasiado.") from erro
    except requests.RequestException as erro:
        raise AroundMeErro(f"Erro de rede ao contactar o servico {servico}.") from erro


def geocodificar_morada(morada: str, api_key: str) -> Dict:
    morada = morada.strip()
    if not morada:
        raise AroundMeErro("A morada nao pode ficar vazia.")

    if morada in CACHE_GEOCODING:
        return CACHE_GEOCODING[morada]

    params = {
        "text": morada,
        "format": "json",
        "limit": 1,
        "lang": "pt",
        "filter": "countrycode:pt",
        "apiKey": api_key,
    }

    dados = geoapify_get("geocoding", GEOCODE_URL, params)
    resultados = dados.get("results", [])
    if not resultados:
        raise AroundMeErro("Nao foi possivel encontrar essa morada.")

    resultado = resultados[0]
    if resultado.get("lat") is None or resultado.get("lon") is None:
        raise AroundMeErro("A API devolveu uma morada sem coordenadas validas.")

    CACHE_GEOCODING[morada] = resultado
    return resultado


def procurar_locais(lat: float, lon: float, categoria: str, api_key: str) -> List[Dict]:
    categoria = validar_categoria(categoria)
    categoria_api = CATEGORY_MAP[categoria]

    for raio in (1000, 3000):
        cache_key = (round(lat, 5), round(lon, 5), categoria_api, raio)
        if cache_key in CACHE_PLACES:
            locais = CACHE_PLACES[cache_key]
        else:
            params = {
                "categories": categoria_api,
                "filter": f"circle:{lon},{lat},{raio}",
                "bias": f"proximity:{lon},{lat}",
                "limit": 5,
                "lang": "pt",
                "apiKey": api_key,
            }

            dados = geoapify_get("places", PLACES_URL, params)
            locais = formatar_locais(dados.get("features", []))
            CACHE_PLACES[cache_key] = locais

        if locais:
            return locais

    return []


def formatar_locais(features: List[Dict]) -> List[Dict]:
    locais = []
    for feature in features:
        props = feature.get("properties", {})
        if props.get("lat") is None or props.get("lon") is None:
            continue

        locais.append(
            {
                "nome": props.get("name") or props.get("address_line1") or "Local sem nome",
                "morada": props.get("formatted") or props.get("address_line2") or "Morada indisponivel",
                "lat": props.get("lat"),
                "lon": props.get("lon"),
                "distancia_m": props.get("distance"),
                "categorias": props.get("categories", []),
            }
        )

    locais.sort(key=lambda local: local.get("distancia_m") or float("inf"))
    return locais


def obter_rota(origem_lat: float, origem_lon: float, destino_lat: float, destino_lon: float, modo: str, api_key: str,) -> Dict:
    modo = validar_modo(modo)
    modo_api = MODE_MAP[modo]
    cache_key = (
        round(origem_lat, 5),
        round(origem_lon, 5),
        round(destino_lat, 5),
        round(destino_lon, 5),
        modo_api,
    )
    if cache_key in CACHE_ROUTES:
        return CACHE_ROUTES[cache_key]

    params = {
        "waypoints": f"{origem_lat},{origem_lon}|{destino_lat},{destino_lon}",
        "mode": modo_api,
        "format": "json",
        "apiKey": api_key,
    }

    dados = geoapify_get("routing", ROUTING_URL, params)
    resultados = dados.get("results", [])
    if not resultados:
        raise AroundMeErro("Nao foi possivel calcular a rota.")

    rota = resultados[0]
    resposta = {
        "distancia_m": rota.get("distance", 0),
        "tempo_s": rota.get("time", 0),
    }
    CACHE_ROUTES[cache_key] = resposta
    return resposta


def enriquecer_com_rotas(locais: List[Dict], origem_lat: float, origem_lon: float, modo: str, api_key: str,) -> List[Dict]:
    resultados = []
    for local in locais[:3]:
        local = local.copy()
        if local.get("lat") is None or local.get("lon") is None:
            local["distancia_rota_km"] = None
            local["tempo_min"] = None
            resultados.append(local)
            continue

        try:
            rota = obter_rota(
                origem_lat=origem_lat,
                origem_lon=origem_lon,
                destino_lat=local["lat"],
                destino_lon=local["lon"],
                modo=modo,
                api_key=api_key,
            )
            local["distancia_rota_km"] = rota["distancia_m"] / 1000
            local["tempo_min"] = rota["tempo_s"] / 60
        except AroundMeErro:
            local["distancia_rota_km"] = None
            local["tempo_min"] = None

        resultados.append(local)

    return resultados


def pesquisar_servicos(morada: str, categoria: str, modo: str) -> Dict:
    morada = morada.strip()
    if not morada:
        raise AroundMeErro("A morada nao pode ficar vazia.")

    api_key = obter_api_key()
    categoria = validar_categoria(categoria)
    modo = validar_modo(modo)

    resultado_morada = geocodificar_morada(morada, api_key)
    lat = resultado_morada["lat"]
    lon = resultado_morada["lon"]
    referencia = resultado_morada.get("formatted", morada)

    locais = procurar_locais(lat, lon, categoria, api_key)
    if not locais:
        raise AroundMeErro("Nao encontrei locais dessa categoria perto da morada indicada.")

    locais = enriquecer_com_rotas(locais, lat, lon, modo, api_key)

    return {
        "referencia": referencia,
        "latitude": lat,
        "longitude": lon,
        "categoria": categoria,
        "modo": modo,
        "locais": locais,
    }

import math
import os
import time
from typing import Dict, List, Tuple

import requests

# AroundMe - primeiro teste técnico
# Objetivo: receber uma morada, procurar locais próximos por categoria
# e calcular distância/tempo estimado a pé ou de carro.
#
# Este ficheiro já inclui alguns cuidados para não abusar das APIs:
# - intervalo mínimo entre pedidos
# - cache em memória durante a execução
# - poucos resultados por pedido
# - sem loops agressivos nem retries infinitos

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
ORS_BASE_URL = "https://api.openrouteservice.org/v2/directions"

USER_AGENT = os.getenv(
    "AROUNDME_USER_AGENT",
    "AroundMe/0.1 (Bruno Alves; contacto: hulk8b@gmail.com)",
)
NOMINATIM_EMAIL = os.getenv("NOMINATIM_EMAIL", "hulk8b@gmail.com")
REQUEST_TIMEOUT = 30

# Intervalos mínimos entre pedidos por serviço
MIN_INTERVALS = {
    "nominatim": 1.2,
    "overpass": 2.0,
    "ors": 0.8,
}

# Cache simples em memória para evitar repetir pedidos iguais na mesma execução
CACHE_GEOCODING: Dict[str, Tuple[float, float, str]] = {}
CACHE_SEARCH: Dict[Tuple[float, float, str, int], List[Dict]] = {}
CACHE_ROUTE: Dict[Tuple[float, float, float, float, str], Dict[str, float]] = {}
LAST_REQUEST_AT: Dict[str, float] = {}

CATEGORY_MAP = {
    "farmacia": ("amenity", "pharmacy"),
    "hospital": ("amenity", "hospital"),
    "escola": ("amenity", "school"),
    "supermercado": ("shop", "supermarket"),
    "supermecado": ("shop", "supermarket"),  # tolerância a typo comum
}

MODE_MAP = {
    "a pe": "foot-walking",
    "a_pe": "foot-walking",
    "pe": "foot-walking",
    "carro": "driving-car",
}


class AroundMeErro(Exception):
    pass


SESSION = requests.Session()


def headers() -> Dict[str, str]:
    return {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
        "Accept-Language": "pt-PT,pt;q=0.9,en;q=0.8",
    }


SESSION.headers.update(headers())



def validar_identificacao() -> None:
    placeholders = {"hulk8b@gmail.com", "brunoalves2001@gmail.com"}
    if NOMINATIM_EMAIL in placeholders or USER_AGENT.endswith("gmail.com)"):
        print(
            "[aviso] Ainda tens um email placeholder no User-Agent ou em NOMINATIM_EMAIL. "
            "Troca por um contacto teu real antes de usar muitas vezes."
        )



def esperar_entre_pedidos(servico: str) -> None:
    intervalo = MIN_INTERVALS.get(servico, 1.0)
    ultimo = LAST_REQUEST_AT.get(servico)
    if ultimo is None:
        return

    decorrido = time.monotonic() - ultimo
    falta = intervalo - decorrido
    if falta > 0:
        time.sleep(falta)



def registar_pedido(servico: str) -> None:
    LAST_REQUEST_AT[servico] = time.monotonic()



def verificar_resposta_limites(resposta: requests.Response, servico: str) -> None:
    if resposta.status_code in (403, 429):
        raise AroundMeErro(
            f"O serviço '{servico}' recusou ou limitou o pedido (HTTP {resposta.status_code}). "
            "Para evitar bloqueios, reduz a frequência dos testes e confirma o User-Agent/email."
        )
    resposta.raise_for_status()



def obter_chave_ors() -> str:
    chave = os.getenv("ORS_API_KEY")
    if not chave:
        raise AroundMeErro(
            "Não foi encontrada a variável de ambiente ORS_API_KEY. "
            "Cria uma chave gratuita no openrouteservice e define-a antes de correr o script."
        )
    return chave



def geocodificar_morada(morada: str) -> Tuple[float, float, str]:
    morada_limpa = morada.strip()
    if morada_limpa in CACHE_GEOCODING:
        return CACHE_GEOCODING[morada_limpa]

    params = {
        "q": morada_limpa,
        "format": "jsonv2",
        "limit": 1,
        "addressdetails": 1,
        "countrycodes": "pt",
        "email": NOMINATIM_EMAIL,
    }

    esperar_entre_pedidos("nominatim")
    resposta = SESSION.get(
        NOMINATIM_URL,
        params=params,
        timeout=REQUEST_TIMEOUT,
    )
    registar_pedido("nominatim")
    verificar_resposta_limites(resposta, "nominatim")

    dados = resposta.json()
    if not dados:
        raise AroundMeErro("Não foi possível encontrar essa morada.")

    resultado = dados[0]
    lat = float(resultado["lat"])
    lon = float(resultado["lon"])
    nome = resultado.get("display_name", morada_limpa)

    tuplo = (lat, lon, nome)
    CACHE_GEOCODING[morada_limpa] = tuplo
    return tuplo



def construir_query_overpass(lat: float, lon: float, chave: str, valor: str, raio: int = 3000) -> str:
    return f"""
    [out:json][timeout:25];
    (
      node[\"{chave}\"=\"{valor}\"](around:{raio},{lat},{lon});
      way[\"{chave}\"=\"{valor}\"](around:{raio},{lat},{lon});
      relation[\"{chave}\"=\"{valor}\"](around:{raio},{lat},{lon});
    );
    out center tags;
    """.strip()



def obter_nome_local(tags: Dict[str, str], fallback: str) -> str:
    return tags.get("name") or tags.get("brand") or tags.get("operator") or fallback



def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    raio_terra = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return raio_terra * c



def procurar_locais(lat: float, lon: float, categoria: str, raio: int = 3000) -> List[Dict]:
    categoria = categoria.strip().lower()
    if categoria not in CATEGORY_MAP:
        raise AroundMeErro(
            f"Categoria inválida: {categoria}. "
            f"Escolhe uma destas: {', '.join(sorted(set(CATEGORY_MAP.keys())))}."
        )

    cache_key = (round(lat, 5), round(lon, 5), categoria, raio)
    if cache_key in CACHE_SEARCH:
        return CACHE_SEARCH[cache_key]

    chave, valor = CATEGORY_MAP[categoria]
    query = construir_query_overpass(lat, lon, chave, valor, raio=raio)

    esperar_entre_pedidos("overpass")
    resposta = SESSION.post(
        OVERPASS_URL,
        data=query.encode("utf-8"),
        timeout=REQUEST_TIMEOUT,
    )
    registar_pedido("overpass")
    verificar_resposta_limites(resposta, "overpass")

    dados = resposta.json()
    elementos = dados.get("elements", [])
    resultados = []
    vistos = set()

    for elemento in elementos:
        tags = elemento.get("tags", {})

        if "lat" in elemento and "lon" in elemento:
            local_lat = elemento["lat"]
            local_lon = elemento["lon"]
        elif "center" in elemento:
            local_lat = elemento["center"]["lat"]
            local_lon = elemento["center"]["lon"]
        else:
            continue

        nome = obter_nome_local(tags, f"Local sem nome ({elemento.get('type', 'desconhecido')})")
        identificador = (nome.lower(), round(local_lat, 5), round(local_lon, 5))
        if identificador in vistos:
            continue
        vistos.add(identificador)

        resultados.append(
            {
                "nome": nome,
                "lat": local_lat,
                "lon": local_lon,
                "categoria": categoria,
                "morada": tags.get("addr:street"),
                "distancia_linha_reta_km": haversine_km(lat, lon, local_lat, local_lon),
            }
        )

    resultados.sort(key=lambda item: item["distancia_linha_reta_km"])

    # Guardamos poucos resultados para não disparar demasiadas rotas depois
    resultados = resultados[:8]
    CACHE_SEARCH[cache_key] = resultados
    return resultados



def obter_rota(
    origem_lat: float,
    origem_lon: float,
    destino_lat: float,
    destino_lon: float,
    modo: str,
    api_key: str,
) -> Dict[str, float]:
    modo = modo.strip().lower()
    if modo not in MODE_MAP:
        raise AroundMeErro("Modo inválido. Usa 'a pe' ou 'carro'.")

    cache_key = (
        round(origem_lat, 5),
        round(origem_lon, 5),
        round(destino_lat, 5),
        round(destino_lon, 5),
        modo,
    )
    if cache_key in CACHE_ROUTE:
        return CACHE_ROUTE[cache_key]

    perfil = MODE_MAP[modo]
    url = f"{ORS_BASE_URL}/{perfil}"

    payload = {
        "coordinates": [
            [origem_lon, origem_lat],
            [destino_lon, destino_lat],
        ]
    }

    esperar_entre_pedidos("ors")
    resposta = SESSION.post(
        url,
        json=payload,
        headers={
            **headers(),
            "Authorization": api_key,
            "Content-Type": "application/json",
        },
        timeout=REQUEST_TIMEOUT,
    )
    registar_pedido("ors")
    verificar_resposta_limites(resposta, "openrouteservice")

    dados = resposta.json()
    rotas = dados.get("routes", [])
    if not rotas:
        raise AroundMeErro("Não foi possível calcular uma rota para este local.")

    resumo = rotas[0].get("summary", {})
    resultado = {
        "distancia_m": float(resumo.get("distance", 0)),
        "duracao_s": float(resumo.get("duration", 0)),
    }
    CACHE_ROUTE[cache_key] = resultado
    return resultado



def enriquecer_com_rotas(
    origem_lat: float,
    origem_lon: float,
    locais: List[Dict],
    modo: str,
    limite: int = 3,
) -> List[Dict]:
    api_key = obter_chave_ors()
    escolhidos = locais[:limite]
    resultados = []

    for local in escolhidos:
        try:
            rota = obter_rota(
                origem_lat,
                origem_lon,
                local["lat"],
                local["lon"],
                modo,
                api_key,
            )
            local["distancia_rota_km"] = rota["distancia_m"] / 1000
            local["duracao_min"] = rota["duracao_s"] / 60
            resultados.append(local)
        except AroundMeErro as erro:
            print(f"[aviso] Não consegui calcular rota para '{local['nome']}': {erro}")
        except requests.RequestException as erro:
            print(f"[aviso] Erro de rede na rota para '{local['nome']}': {erro}")

    resultados.sort(key=lambda item: item.get("duracao_min", float("inf")))
    return resultados



def mostrar_resultados(resultados: List[Dict], referencia: str, modo: str) -> None:
    print("" + "=" * 70)
    print("RESULTADOS AROUNDME")
    print("=" * 70)
    print(f"Origem: {referencia}")
    print(f"Modo: {modo}")

    if not resultados:
        print("Sem resultados para mostrar.")
        return

    for indice, local in enumerate(resultados, start=1):
        print(f"{indice}. {local['nome']}")
        print(f"   Categoria: {local['categoria']}")
        print(f"   Distância em linha reta: {local['distancia_linha_reta_km']:.2f} km")
        print(f"   Distância estimada pela rota: {local.get('distancia_rota_km', 0):.2f} km")
        print(f"   Tempo estimado: {local.get('duracao_min', 0):.0f} min")



def main() -> None:
    validar_identificacao()

    print("AroundMe - teste inicial das APIs")
    print("Categorias disponíveis: farmacia, hospital, escola, supermercado")
    print("Modos disponíveis: a pe, carro")

    morada = input("Introduz a morada ou localidade: ").strip()
    categoria = input("Introduz a categoria: ").strip().lower()
    modo = input("Introduz o modo de deslocação: ").strip().lower()

    if not morada:
        raise AroundMeErro("A morada não pode ficar vazia.")

    lat, lon, referencia = geocodificar_morada(morada)
    print(f"[ok] Morada encontrada: {referencia}")
    print(f"[ok] Coordenadas: {lat:.6f}, {lon:.6f}")

    locais = procurar_locais(lat, lon, categoria, raio=3000)
    if not locais:
        raise AroundMeErro("Não encontrei locais dessa categoria perto da morada indicada.")

    print(f"[ok] Locais encontrados nesta amostra: {len(locais)}")

    resultados = enriquecer_com_rotas(lat, lon, locais, modo, limite=3)
    mostrar_resultados(resultados, referencia, modo)


if __name__ == "__main__":
    try:
        main()
    except AroundMeErro as erro:
        print(f"[erro] {erro}")
    except requests.HTTPError as erro:
        print(f"[erro HTTP] {erro}")
    except requests.RequestException as erro:
        print(f"[erro de rede] {erro}")
    except KeyboardInterrupt:
        print("Execução interrompida pelo utilizador.")

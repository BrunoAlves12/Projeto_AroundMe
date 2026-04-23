# AroundMe

## Descricao

O **AroundMe** e uma aplicacao web em **Python + Flask** que permite pesquisar servicos uteis perto de uma morada ou localidade em Portugal.

O utilizador pode escolher uma categoria, selecionar o modo de deslocacao e consultar os resultados obtidos a partir da API da **Geoapify**. A aplicacao guarda tambem o historico das pesquisas em **SQLite**.

## Funcionalidades

- pesquisa por morada ou localidade
- categorias disponiveis: farmacia, hospital, escola e supermercado
- modos de deslocacao: a pe e carro
- apresentacao de locais proximos com distancia e tempo estimado
- historico de pesquisas guardado em base de dados SQLite

## Instalacao

### 1. Download do projeto


### 2. Criar e ativar ambiente virtual

No Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Se estiveres a usar outro terminal:

- PowerShell: `.\.venv\Scripts\Activate.ps1`
- CMD: `.\.venv\Scripts\activate.bat`
- Git Bash: `source .venv/Scripts/activate`

### 3. Instalar dependencias

```powershell
pip install -r requirements.txt
```

### 4. Criar conta na Geoapify

1. Aceder a [Geoapify](https://www.geoapify.com/)
2. Criar conta
3. Entrar no dashboard
4. Abrir a aba **API Keys**
5. Criar ou copiar uma chave de API

### 5. Definir a variavel de ambiente `GEOAPIFY_API_KEY`

No PowerShell:

```powershell
$env:GEOAPIFY_API_KEY="a_tua_chave"
```

Se quiseres confirmar:

```powershell
echo $env:GEOAPIFY_API_KEY
```

### 6. Executar a aplicacao

```powershell
python run.py
```

Depois abre no navegador o endereco apresentado no terminal, normalmente:

```text
http://127.0.0.1:5000
```

# AroundMe

## Visão geral

**AroundMe** é uma aplicação web desenvolvida em Python com Flask que permite ao utilizador encontrar serviços úteis perto de uma determinada morada ou localidade.

O objetivo principal é ajudar uma pessoa a identificar rapidamente locais importantes numa zona específica, sobretudo quando não conhece bem a área.

Exemplos de serviços que a aplicação pode procurar:

* farmácias
* hospitais
* escolas
* supermercados

Além disso, o utilizador pode escolher o modo de deslocação, como **a pé** ou **de carro**, para obter uma noção mais realista da distância e do tempo estimado.

---

## Problema que a aplicação resolve

Quando alguém está numa zona nova, nem sempre é fácil perceber rapidamente que serviços existem por perto e qual deles é mais conveniente.

A aplicação AroundMe pretende simplificar esse processo, permitindo:

* introduzir uma morada
* escolher uma categoria de serviço
* escolher o modo de deslocação
* ver resultados próximos com informação útil

A aplicação tem um contexto prático e realista, útil no dia a dia.

---

## Objetivo do MVP

Nesta fase, o foco é criar um **MVP funcional**, simples e fácil de explicar.

O MVP deve ser capaz de:

1. receber uma morada ou localidade
2. converter essa morada em coordenadas geográficas
3. procurar locais próximos de uma certa categoria
4. apresentar resultados com informação essencial
5. guardar o histórico de pesquisas numa base de dados SQLite

---

## Funcionalidades previstas

### Funcionalidades principais

* introdução de uma morada ou localidade
* seleção da categoria de serviço
* seleção do modo de deslocação
* pesquisa de locais próximos
* apresentação dos resultados
* registo do histórico de pesquisas

### Informação apresentada nos resultados

Cada resultado poderá incluir:

* nome do local
* categoria
* distância
* tempo estimado de deslocação
* eventualmente uma página de detalhe com informação adicional

---

## Tecnologias previstas

O projeto foi pensado com tecnologias simples e adequadas a um contexto de formação.

### Backend

* **Python**
* **Flask**

### Frontend

* **HTML**
* **CSS**
* JavaScript apenas se for realmente necessário mais à frente

### Base de dados

* **SQLite**

### APIs externas

A aplicação depende de APIs externas para tratar informação geográfica.

Atualmente, a ideia técnica é esta:

* **Nominatim / OpenStreetMap** para converter moradas em coordenadas
* **Overpass API / OpenStreetMap** para procurar locais por categoria
* **openrouteservice** para cálculo de rotas, distância real e tempo estimado

---

## Fluxo principal da aplicação

O fluxo principal esperado é o seguinte:

1. o utilizador introduz uma morada
2. escolhe a categoria pretendida
3. escolhe o modo de deslocação
4. o sistema converte a morada em coordenadas
5. o sistema procura locais próximos dessa categoria
6. o sistema calcula, quando possível, distância e tempo estimado
7. os resultados são apresentados ao utilizador
8. a pesquisa é guardada no histórico

---

## Arquitetura prevista

A aplicação deverá seguir uma estrutura simples, dividida em três partes:

### 1. Frontend

Responsável pela interface com o utilizador.

### 2. Backend

Responsável por:

* receber os dados do formulário
* validar os dados
* comunicar com as APIs externas
* tratar os resultados
* guardar o histórico

### 3. Base de dados SQLite

Responsável por guardar o histórico de pesquisas realizadas.

---

## Estado atual do projeto

Neste momento, o projeto ainda está numa fase inicial.

O trabalho atual está focado em:

* testar as APIs separadamente antes de integrar tudo no Flask
* validar se a morada é convertida corretamente em coordenadas
* verificar se é possível obter locais próximos por categoria
* calcular distâncias e tempos de forma controlada
* evitar uso excessivo das APIs públicas

Ou seja, antes de construir a aplicação web completa, está a ser feita uma **prova de conceito técnica**.

---

## Cuidados importantes com as APIs

Como o projeto usa serviços públicos, é importante reduzir o número de pedidos e evitar chamadas desnecessárias.

Boas práticas previstas:

* uso de `User-Agent` identificável
* uso de email de contacto configurável por variável de ambiente
* intervalo mínimo entre pedidos
* cache local durante a execução
* poucos resultados por pesquisa
* poucos cálculos de rota por pedido
* tratamento de falhas e timeouts

Isto é importante para evitar bloqueios e para manter o comportamento da aplicação responsável e estável.

---

## Estrutura funcional esperada do projeto

Mais à frente, a aplicação poderá ficar organizada de forma simples, por exemplo assim:

```text
AroundMe/
├─ app.py
├─ teste.py
├─ templates/
│  ├─ index.html
│  └─ resultados.html
├─ static/
│  └─ style.css
├─ database/
│  └─ aroundme.db
└─ README.md
```

Isto ainda pode mudar, mas a ideia é manter uma estrutura simples e fácil de explicar.

---

## Possíveis dificuldades

Algumas dificuldades já identificadas:

* pouca experiência prévia com APIs
* tratamento de moradas com diferentes formatos
* instabilidade ou limites dos serviços públicos
* diferenças entre distância em linha reta e distância real por rota
* necessidade de controlar bem os pedidos às APIs

---

## Prioridades de desenvolvimento

A ordem de trabalho mais lógica é:

1. provar que as APIs funcionam em script Python simples
2. estabilizar o fluxo morada → coordenadas → locais próximos
3. integrar cálculo de rotas quando houver chave disponível
4. passar essa lógica para Flask
5. criar a interface web
6. guardar histórico em SQLite
7. melhorar apresentação e detalhe dos resultados

---

## Público-alvo

A aplicação destina-se a qualquer utilizador que precise de encontrar serviços próximos de uma determinada localização, especialmente em zonas que não conhece bem.

---

## Resumo curto

AroundMe é uma aplicação web em Python/Flask que permite pesquisar serviços úteis perto de uma morada, com base em categorias e modo de deslocação, apresentando resultados com distância e tempo estimado e guardando o histórico em SQLite.

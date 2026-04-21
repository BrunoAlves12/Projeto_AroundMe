# AroundMe

## Visão geral

**AroundMe** é uma aplicação web desenvolvida em Python com Flask que permite ao utilizador encontrar serviços úteis perto de uma determinada morada ou localidade.

O objetivo principal é ajudar uma pessoa a identificar rapidamente locais importantes numa zona específica, sobretudo quando não conhece bem a área.

Exemplos de serviços que a aplicação pode procurar:

- farmácias
- hospitais
- escolas
- supermercados

Além disso, o utilizador pode escolher o modo de deslocação, como **a pé** ou **de carro**, para obter uma noção mais realista da distância e do tempo estimado.

---

## Problema que a aplicação resolve

Quando alguém está numa zona nova, nem sempre é fácil perceber rapidamente que serviços existem por perto e qual deles é mais conveniente.

A aplicação AroundMe pretende simplificar esse processo, permitindo:

- introduzir uma morada
- escolher uma categoria de serviço
- escolher o modo de deslocação
- ver resultados próximos com informação útil

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

- introdução de uma morada ou localidade
- seleção da categoria de serviço
- seleção do modo de deslocação
- pesquisa de locais próximos
- apresentação dos resultados
- registo do histórico de pesquisas

### Informação apresentada nos resultados

Cada resultado poderá incluir:

- nome do local
- morada
- distância aproximada
- distância por rota
- tempo estimado de deslocação
- eventualmente uma página de detalhe com informação adicional

---

## Tecnologias previstas

O projeto foi pensado com tecnologias simples e adequadas a um contexto de formação.

### Backend

- **Python**
- **Flask**

### Frontend

- **HTML**
- **CSS**
- JavaScript apenas se for realmente necessário mais à frente

### Base de dados

- **SQLite**

### APIs externas

A aplicação depende de APIs externas para tratar informação geográfica.

Atualmente, a abordagem técnica escolhida é a utilização da plataforma **Geoapify**, que permite concentrar numa única solução:

- conversão de moradas em coordenadas geográficas
- pesquisa de locais próximos por categoria
- cálculo de rotas, distância real e tempo estimado

Esta opção foi escolhida por ser mais estável e mais simples de integrar nesta fase do projeto.

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

- receber os dados do formulário
- validar os dados
- comunicar com as APIs externas
- tratar os resultados
- guardar o histórico

### 3. Base de dados SQLite

Responsável por guardar o histórico de pesquisas realizadas.

---

## Estrutura inicial da base de dados

Numa primeira fase, a aplicação irá guardar o histórico das pesquisas realizadas pelo utilizador.

A tabela principal poderá chamar-se `pesquisas` e incluir os seguintes campos:

- `id`
- `morada`
- `categoria`
- `modo_deslocacao`
- `latitude`
- `longitude`
- `data_pesquisa`

Nesta fase, o objetivo é guardar o histórico da pesquisa efetuada, e não ainda o local específico selecionado pelo utilizador. Essa funcionalidade poderá ser acrescentada numa fase posterior.

---

## Estado atual do projeto

Neste momento, o projeto encontra-se numa fase inicial, mas já foi possível validar a lógica principal através de um script Python de testes.

Até agora já foi conseguido:

- converter moradas em coordenadas geográficas
- pesquisar locais próximos por categoria
- calcular distância e tempo estimado de deslocação
- testar diferentes categorias, como farmácia e escola
- controlar melhor o número de pedidos à API

Ou seja, a prova de conceito técnica já se encontra funcional, faltando agora integrar esta lógica numa aplicação web com Flask e registo de histórico em SQLite.

---

## Cuidados importantes com as APIs

Como a aplicação depende de serviços externos, é importante controlar o número de pedidos e evitar chamadas desnecessárias.

Boas práticas previstas:

- utilização de chave de API por variável de ambiente
- limitação do número de resultados por pesquisa
- cálculo de rotas apenas para os primeiros resultados
- cache local durante a execução
- tratamento de falhas, timeouts e bloqueios temporários
- evitar pedidos repetidos sem necessidade

Isto é importante para manter a aplicação estável e para reduzir consumo desnecessário da API.

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
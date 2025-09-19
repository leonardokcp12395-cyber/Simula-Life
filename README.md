```markdown
# Simulador de Ecossistema Digital com IA Evolutiva

Bem-vindo ao Simulador de Ecossistema Digital! Este é um projeto de Vida Artificial ("Artificial Life") construído em Python, que simula um pequeno mundo onde criaturas com cérebros de redes neurais evoluem para sobreviver, reproduzir-se e formar sociedades complexas.

Este projeto foi desenvolvido como um "Petrie Dish Digital", uma caixa de areia onde se pode observar o surgimento de comportamentos complexos a partir de regras simples e da pressão da seleção natural. A inteligência das criaturas não é programada; ela é **evoluída**.

![Exemplo da Simulação](https://i.imgur.com/your-image-url.png)  ---

## Funcionalidades Principais

Este simulador é rico em funcionalidades que interagem para criar um ecossistema dinâmico:

### 1. Mundo Gerado Proceduralmente
O mundo é gerado usando **Ruído de Perlin** para criar mapas únicos a cada execução, com diferentes biomas que afetam a simulação:
* **Biomas:** Oceanos, Praias, Planícies, Florestas e Montanhas Nevadas.
* **Impacto no Jogo:** Cada terreno tem um "custo de movimento" e um "custo de energia" diferentes, forçando as criaturas a tomar decisões estratégicas sobre onde viver e caçar.

### 2. IA Evolutiva com NEAT
O cérebro de cada criatura é uma **rede neural** gerida pelo algoritmo **NEAT (NeuroEvolution of Augmenting Topologies)**.
* **Cérebro Complexo:** As criaturas processam 16 "sentidos" (inputs) diferentes para tomar decisões.
* **Evolução Contínua:** A cada duas "estações" no jogo, o sistema avalia as criaturas sobreviventes e usa os seus "genes" (genomas) para criar uma nova geração de cérebros mais inteligentes, que são distribuídos pela população.

### 3. Ecossistema e Cadeia Alimentar
O mundo é habitado por duas espécies com papéis distintos:
* **Herbívoros:** Evoluem para encontrar comida (plantas), formar rebanhos para proteção e reproduzir-se.
* **Carnívoros:** Evoluem para caçar herbívoros, desenvolver estratégias de matilha e gerir o seu território.

### 4. Ambiente Dinâmico
O mundo não é estático; ele muda constantemente, criando novos desafios:
* **Ciclo Dia/Noite:** A luz muda, afetando drasticamente a visibilidade.
* **Visão Noturna:** As criaturas podem evoluir um gene de "visão noturna" para se especializarem em caçar ou sobreviver na escuridão.
* **Estações do Ano:** A Primavera e o Verão são épocas de abundância, enquanto o Outono e o Inverno trazem a escassez de comida, atuando como um grande filtro da seleção natural.

### 5. Comportamento Social Complexo
As criaturas possuem uma inteligência social profunda:
* **Ninhos e Lares:** Cada criatura tem um ninho, que serve como ponto de referência e local seguro. Os ninhos são herdados, criando territórios familiares.
* **Memória de Curto Prazo:** As criaturas lembram-se da última localização conhecida de comida ou perigo.
* **Sistema de Tribos:** Cada espécie está dividida em tribos com identidades visuais (cores) únicas. A IA consegue distinguir entre "companheiros de tribo" e "rivais", levando a comportamentos de cooperação e conflito territorial.

### 6. Intervenção do Utilizador (Modo "Deus")
O utilizador não é apenas um observador, mas pode intervir diretamente no mundo:
* **Controlo do Tempo:** Pausar (`P`), acelerar (`Seta Direita`) e abrandar (`Seta Esquerda`) a simulação.
* **Ferramentas de Criação:** Criar comida (`F`), herbívoros (`H`) e carnívoros (`C`) com um clique do rato.
* **Ferramenta de Destruição:** Eliminar criaturas com a ferramenta "Smite" (`X`).

### 7. Interface de Observação
* **Painel de Inspeção:** Clique em qualquer criatura para ver os seus status em tempo real: tribo, energia, idade, genes (velocidade, visão) e até linhas que indicam o seu alvo atual.
* **UI Principal:** Um relógio no topo do ecrã mostra o dia, a hora e a estação atual, juntamente com a contagem da população.

---

## Como Executar

Para correr esta simulação no seu computador, siga estes passos.

**1. Pré-requisitos:**
* Ter o [Python](https://www.python.org/downloads/) instalado (versão 3.8 ou superior recomendada).

**2. Estrutura de Pastas:**
Crie a seguinte estrutura de pastas e ficheiros no seu computador:
```

simulador\_vida/
|
|--- config-feedforward.txt
|--- main.py
|--- settings.py
|
|--- core/
|    |--- **init**.py
|    |--- world\_management.py
|
|--- entities/
|    |--- **init**.py
|    |--- creature.py
|    |--- food.py
|
|--- rendering/
|--- **init**.py
|--- assets.py
|--- drawing.py

````

**3. Instalar as Bibliotecas:**
Abra o seu terminal ou prompt de comando, navegue até à pasta `simulador_vida` e execute o seguinte comando:
```bash
pip install pygame perlin-noise neat-python
````

**4. Executar a Simulação:**
Com tudo no lugar, execute o ficheiro principal a partir do seu terminal:

```bash
python main.py
```

A janela da simulação deverá aparecer e o ecossistema começará a evoluir\!

-----

## Controles do Modo "Deus"

  * **P**: Pausar / Retomar a simulação.
  * **Seta Direita**: Aumentar a velocidade da simulação (até 5x).
  * **Seta Esquerda**: Diminuir a velocidade da simulação (até 1x).
  * **F**: Ativar a ferramenta de criar **Comida**.
  * **H**: Ativar a ferramenta de criar **Herbívoro**.
  * **C**: Ativar a ferramenta de criar **Carnívoro**.
  * **X**: Ativar a ferramenta de **Eliminar** (Smite).
  * **Clique Esquerdo do Rato**: Usar a ferramenta selecionada no local do cursor.
  * **Clique Direito do Rato / ESC**: Desativar a ferramenta atual.

<!-- end list -->

```
```

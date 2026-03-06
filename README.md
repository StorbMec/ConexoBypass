# Conexo Solver

Script Python que busca as respostas do puzzle diário do [conexo.ws](https://conexo.ws) via API do Firestore.

## Requisitos

```bash
pip install requests
```

## Como usar

### 1. Pegue o AppCheck token e o DOC_ID

Abra o [conexo.ws](https://conexo.ws) no Chrome e acesse o DevTools (`F12`).

Vá em **Network** → filtre por `channel` → clique no primeiro **POST** para o Firestore → aba **Payload**.

O body da requisição vai ter um campo `headers=` com o seguinte conteúdo:

```
x-firebase-appcheck:eyJraWQiOiJrMnhhbUEi...  ← copie esse valor
```

Na mesma aba, procure o campo `req0___data__`. Dentro dele há um caminho como:

```
projects/daydashgames/databases/(default)/documents/conexo-daily-pt/887
                                                                     ^^^
                                                                  esse é o DOC_ID
```

<img src="https://i.imgur.com/C6tqGy3.png">

### 2. Rode o script

```bash
python conexo.py
```

O script vai pedir os dois valores:

```
=== Conexo Solver ===

DevTools → Network → POST channel → Payload → x-firebase-appcheck
AppCheck token: [cole aqui]

DOC_ID (ex: 887): [cole aqui]
```

### 3. Resultado

```
=== Conexo #887 ===

Grupo 1: Tecidos
  algodão, seda, lã, veludo

Grupo 2: Confusão
  bafafá, tumulto, rebuliço, alvoroço

Grupo 3: Personagens de Maurício de Sousa
  tina, rolo, pipa, zecão

Grupo 4: Ave símbolo do estado de Pernambuco
  fragata, alcatraz, tesourão, guarapirá
```

## Observações

- O **AppCheck token** expira em ~7 dias — após isso será necessário capturar um novo no DevTools.
- O **DOC_ID** muda todo dia — sempre verifique o valor atual no Payload antes de rodar.

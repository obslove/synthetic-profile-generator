# Gerador de Perfis Sintéticos

Gerador enxuto de perfis sintéticos para QA, desenvolvimento, staging e demonstrações.

## Sobre

Este projeto gera perfis claramente fictícios e seguros para teste.

Ele foi simplificado para produzir apenas:

- `identity`
- `location` somente com país
- `family` somente com pai e mãe
- `credentials` com um e-mail e uma senha
- identificador nacional sintético para `BR`, `US` e `FR`

O foco aqui é:

- saída limpa
- uso rápido via CLI e API
- nomes amplos e variados
- comportamento determinístico quando desejado
- fallback seguro de e-mail

## O que ele faz

- gera nome sintético por país
- gera gênero `male` ou `female`
- gera idade ou usa uma idade fixa
- gera pai e mãe com pelo menos 20 anos a mais
- gera e-mail via SimpleLogin quando disponível
- cai para domínio reservado (`example.*`) quando necessário
- gera senha forte
- gera identificador sintético por país:
  - `BR` -> `cpf`
  - `US` -> `ssn_like`
  - `FR` -> `nir_like`

## Regras de segurança

- não gera identidades reais
- não gera endereço residencial detalhado
- não gera inbox enganosa operacional
- não gera identificadores para uso real
- não serve para fraude, impersonação, KYC ou bypass

## Países suportados

- `BR`
- `US`
- `FR`

Cada país incluído atualmente possui:

- `900` nomes masculinos
- `900` nomes femininos
- `900` sobrenomes

## Instalação rápida

### Bash / Zsh

```bash
git clone <repo>
cd synthetic-profile-generator
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

### Fish

```fish
git clone <repo>
cd synthetic-profile-generator
python -m venv .venv
source .venv/bin/activate.fish
pip install -e .[dev]
```

## Uso rápido

Gerar um perfil:

```bash
python main.py generate --c BR --g male
```

Fixar a idade:

```bash
python main.py generate --c US --g female --a 41
```

Escolher o tamanho da senha:

```bash
python main.py generate --c FR --g female -q 32
```

Gerar em modo compacto:

```bash
python main.py generate --c BR --g male --f compact
```

Gerar um lote:

```bash
python main.py generate-batch --count 10 --c US
```

## Flags da CLI

### `generate`

- `--c` país
- `--g` gênero
- `--a` idade exata
- `-q` quantidade de caracteres da senha
- `--f` formato: `pretty` ou `compact`

### `generate-batch`

- `--count` quantidade
- `--c` país
- `--g` gênero
- `--a` idade exata aplicada ao lote
- `-q` quantidade de caracteres da senha
- `--f` formato: `pretty` ou `compact`

### `countries`

- sem flags

## Padrões da CLI

- identificador sintético vem ligado por padrão
- `pretty` é o formato padrão
- SimpleLogin é usado por padrão
- se SimpleLogin falhar, o fallback aparece de forma explícita
- `json` e `csv` não fazem parte da CLI atual

## API

Subir a API:

```bash
uvicorn synthetic_profiles.api.app:app --host 0.0.0.0 --port 8000 --reload
```

Endpoints:

- `GET /health`
- `GET /countries`
- `POST /generate-profile`
- `POST /generate-batch`

Exemplo de body:

```json
{
  "country_code": "BR",
  "gender": "male",
  "age_min": 21,
  "age_max": 45,
  "use_simplelogin": true,
  "include_cpf": true,
  "seed": 10
}
```

## Estrutura da saída

A saída limpa fica neste formato:

```json
{
  "identity": {
    "full_name": "Paulo Murilo Almeida Rangel",
    "gender": "male",
    "age": 53,
    "national_identifier": "265.683.975-04",
    "national_identifier_type": "cpf"
  },
  "location": {
    "country": "Brasil",
    "country_code": "BR"
  },
  "family": {
    "father": {
      "full_name": "Lucas Rangel",
      "gender": "male",
      "age": 80,
      "national_identifier": "761.012.547-47",
      "national_identifier_type": "cpf"
    },
    "mother": {
      "full_name": "Dandara Almeida",
      "gender": "female",
      "age": 83,
      "national_identifier": "120.975.367-78",
      "national_identifier_type": "cpf"
    }
  },
  "credentials": {
    "email": "ember-rangel441@example.org",
    "password": "aNHdN^,:ND3V6yY:G9g#-TT*"
  }
}
```

## Determinismo

- sem `seed`: varia entre execuções
- com `seed`: repete exatamente a mesma saída
- em lote com `seed`: cada índice do lote segue determinístico

## SimpleLogin

Para usar SimpleLogin de verdade, configure:

```env
SIMPLELOGIN_API_KEY=
SIMPLELOGIN_BASE_URL=https://api.simplelogin.io/api
```

Sem chave válida:

- o gerador faz fallback automático
- o e-mail continua saindo
- o motivo do fallback aparece na CLI

## Variáveis de ambiente

Veja [`.env.example`](./.env.example).

Principais:

- `SIMPLELOGIN_API_KEY`
- `SIMPLELOGIN_BASE_URL`
- `REQUEST_TIMEOUT_SECONDS`
- `FALLBACK_EMAIL_DOMAINS`
- `DEFAULT_COUNTRY_CODE`
- `STRICT_IDENTIFIER_SAFETY_MODE`

## Testes

```bash
.venv/bin/python -m pytest -q
```

## Exemplos

- [Exemplo JSON BR](./examples/sample_profile_br.json)

## Observação

O nome do campo `include_cpf` foi mantido na API por compatibilidade, mas ele já funciona como “incluir identificador nacional sintético do país atual”.

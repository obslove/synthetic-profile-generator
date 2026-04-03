# Gerador de Perfis Sintéticos

Gerador enxuto de perfis sintéticos para QA, desenvolvimento, staging e demonstrações.

## Sobre

Este projeto gera perfis claramente fictícios e seguros para teste.

Ele produz apenas:

- `identity`
- `location` com país e estado/região opcional
- `family` somente com pai e mãe
- `credentials` com um e-mail e uma senha
- identificador nacional sintético para `BR` e `US`

## Instalação rápida

`fish`

```fish
curl -fsSL https://raw.githubusercontent.com/obslove/synthetic-profile-generator/main/install.sh | bash
```

`bash`

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/obslove/synthetic-profile-generator/main/install.sh)
```

`zsh`

```zsh
bash <(curl -fsSL https://raw.githubusercontent.com/obslove/synthetic-profile-generator/main/install.sh)
```

Quando executado fora do repositório, o script:

- clona ou atualiza `~/Repositories/synthetic-profile-generator`
- cria `.venv`
- instala o projeto
- cria o comando `synthetic-profile-generator` em `~/.local/bin`

Se `~/.local/bin` ainda não estiver no `PATH`, exporte manualmente:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

## Uso rápido

Gerar um perfil:

```bash
synthetic-profile-generator generate --c BR --g male
```

Gerar em modo compacto:

```bash
synthetic-profile-generator generate --c BR --f compact
```

Escolher o estado:

```bash
synthetic-profile-generator generate --c BR --s SP --g male
```

Escolher a cidade:

```bash
synthetic-profile-generator generate --c BR --s SP --ci Campinas --g male
```

Fixar a idade:

```bash
synthetic-profile-generator generate --c US --s CA --g female --a 41
```

Gerar um lote:

```bash
synthetic-profile-generator generate-batch --n 10 --c US
```

## E-mails funcionais

Por padrão, a CLI tenta usar SimpleLogin com `--sl`.

Para isso gerar aliases reais, você precisa configurar a API key:

```bash
cp .env.example .env
```

Edite o `.env`:

```env
SIMPLELOGIN_API_KEY=sua_chave_aqui
SIMPLELOGIN_BASE_URL=https://api.simplelogin.io/api
```

Sem `SIMPLELOGIN_API_KEY`, ou se sua conta do SimpleLogin recusar a criação do alias, o projeto faz fallback para `example.*`.

Se você quiser desligar SimpleLogin explicitamente:

```bash
synthetic-profile-generator generate --c BR --s SP --ci Campinas --g male --no-sl
```

## Flags da CLI

### `generate`

- `--c` país
- `--s` estado/região do país escolhido
- `--ci` cidade da subdivisão escolhida
- `--g` gênero
- `--a` idade exata
- `--sl` ou `--no-sl` para usar SimpleLogin ou fallback local
- `--f` formato: `pretty` ou `compact`

### `generate-batch`

- `--n` quantidade
- `--c` país
- `--s` estado/região aplicada ao lote
- `--ci` cidade aplicada ao lote
- `--g` gênero
- `--a` idade exata aplicada ao lote
- `--sl` ou `--no-sl` para usar SimpleLogin ou fallback local
- `--f` formato: `pretty` ou `compact`

### `countries`

- `--f` formato: `pretty` ou `compact`

### `states`

- `--c` país
- `--f` formato: `pretty` ou `compact`

### `cities`

- `--c` país
- `--s` subdivisão
- `--f` formato: `pretty` ou `compact`

O comando retorna todas as subdivisões suportadas para o país:

- `BR`: 27 unidades federativas
- `US`: 50 estados, `DC` e territórios suportados

## Padrões da CLI

- identificador sintético vem ligado por padrão
- SimpleLogin é tentado por padrão
- aliases reais via SimpleLogin exigem `SIMPLELOGIN_API_KEY` no `.env`
- `pretty` é o formato padrão
- se SimpleLogin falhar, o fallback aparece de forma explícita
- todas as saídas da CLI seguem o mesmo padrão textual

## Países suportados

- `BR`
- `US`

Cada país incluído atualmente possui:

- `900` nomes masculinos
- `900` nomes femininos
- `900` sobrenomes

## O que ele faz

- gera nome sintético por país
- permite escolher estado/região compatível com o país
- gera gênero `male` ou `female`
- gera idade aleatória ou fixa
- gera pai e mãe com pelo menos 20 anos a mais
- gera e-mail via SimpleLogin quando disponível
- cai para domínio reservado (`example.*`) quando necessário
- gera senha forte
- gera identificador sintético por país:
  - `BR` -> `cpf`
  - `US` -> `ssn_like`

## Regras de segurança

- não gera identidades reais
- não gera endereço residencial detalhado
- não gera inbox enganosa operacional
- não gera identificadores para uso real
- não serve para fraude, impersonação, KYC ou bypass

## API

Subir a API:

```bash
uvicorn synthetic_profiles.api.app:app --host 0.0.0.0 --port 8000 --reload
```

Endpoints:

- `GET /health`
- `GET /countries`
- `GET /countries/{country_code}/states`
- `POST /generate-profile`
- `POST /generate-batch`

Exemplo de body:

```json
{
  "country_code": "BR",
  "state": "SP",
  "gender": "male",
  "age_min": 21,
  "age_max": 45,
  "use_simplelogin": true,
  "include_national_identifier": true,
  "seed": 10
}
```

Na API, opções avançadas como `include_national_identifier`, `seed`, `debug_output` e `response_mode` continuam disponíveis.

## Estrutura da saída

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
    "country_code": "BR",
    "state": "São Paulo",
    "state_code": "SP",
    "state_type": "state"
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

## Uso local

Se você já estiver dentro do repositório:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .[dev]
python main.py generate --c BR --g male
```

## Validação local

```bash
bash -n install.sh
.venv/bin/python -m pytest -q
```

## Exemplos

- [Exemplo JSON BR](./examples/sample_profile_br.json)

## Observação

O nome canônico do campo na API agora é `include_national_identifier`.

`include_cpf` continua aceito por compatibilidade e mantém o mesmo comportamento.

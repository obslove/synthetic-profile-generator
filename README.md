# Gerador de Perfis Sintéticos

Gerador de perfis sintéticos com foco em segurança para desenvolvimento, QA, demonstrações, staging e seed de dados.

Esta versão simplificada gera intencionalmente apenas:

- `identity`
- `location` apenas com país
- `family` apenas com `father` e `mother`
- `credentials` com um e-mail e uma senha
- identificador nacional sintético opcional para `BR`, `US` e `FR`

Os pacotes de locale incluídos mantêm pools amplas de prenomes e sobrenomes para reduzir repetição prática. Cada país suportado atualmente possui `900` nomes masculinos, `900` nomes femininos e `900` sobrenomes.

Países suportados:

- `BR`
- `US`
- `FR`

Regras de segurança:

- não gerar identidades reais
- não gerar endereços residenciais exatos
- não gerar caixas de entrada enganosas ativas
- não gerar identificadores de uso real além de formatos sintéticos para teste
- não apoiar fraude, impersonação, KYC ou bypass de verificação

## Estrutura da Saída

A saída JSON padrão é mínima:

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

O modo de depuração adiciona apenas diagnósticos técnicos:

- detalhes do provedor de e-mail
- motivo do fallback
- diagnósticos de RNG/seed
- avisos

## Determinismo

- sem `seed`: a geração varia entre execuções
- com `seed`: a mesma entrada produz a mesma saída
- geração em lote permanece determinística por índice do lote quando há `seed`

## Identificadores Nacionais Sintéticos

O campo `include_cpf` da API mantém o nome antigo por compatibilidade, mas agora significa:

- `BR` -> `cpf` sintético
- `US` -> `ssn_like` sintético
- `FR` -> `nir_like` sintético

Regras:

- opcional
- apenas sintético
- determinístico com `seed`
- checksum válido para testes de CPF brasileiro
- em `US` e `FR`, a saída é apenas um placeholder no formato local para testes de UI e backend
- sempre marcado internamente como `safe_for_testing_only`

Use isso apenas para testes.

## Execução

### Setup local

```bash
cd /home/ven/synthetic-profile-generator
source .venv/bin/activate
```

No Fish:

```fish
cd /home/ven/synthetic-profile-generator
source .venv/bin/activate.fish
```

### CLI

Gerar um perfil:

```bash
python main.py generate \
  --c BR \
  --g male \
  --f pretty
```

Gerar usando o modo padrão `pretty`:

```bash
python main.py generate \
  --c US \
  --g female
```

Gerar um lote:

```bash
python main.py generate-batch \
  --count 50 \
  --c FR
```

Flags da CLI:

- `--c` país: `BR`, `US`, `FR`
- `--g` gênero: `male`, `female`
- `--amin` idade mínima
- `--amax` idade máxima
- `--f` formato: `compact`, `pretty`
- `--count` tamanho do lote para `generate-batch`

Padrões da CLI:

- identificador nacional sintético incluído por padrão
- um e-mail e uma senha sempre visíveis
- `pretty` por padrão
- sem modo `json` ou `csv` na CLI
- SimpleLogin habilitado por padrão, com fallback automático

### API

```bash
uvicorn synthetic_profiles.api.app:app --host 0.0.0.0 --port 8000 --reload
```

Endpoints:

- `GET /health`
- `GET /countries`
- `POST /generate-profile`
- `POST /generate-batch`

Exemplo de requisição:

```json
{
  "country_code": "BR",
  "gender": "male",
  "age_min": 21,
  "age_max": 45,
  "use_simplelogin": true,
  "seed": 10
}
```

## Variáveis de Ambiente

Veja [`.env.example`](./.env.example).

Principais:

- `SIMPLELOGIN_API_KEY`
- `SIMPLELOGIN_BASE_URL`
- `REQUEST_TIMEOUT_SECONDS`
- `FALLBACK_EMAIL_DOMAINS`
- `DEFAULT_COUNTRY_CODE`

## Testes

```bash
.venv/bin/python -m pytest -q
```

## Exemplos

- [Exemplo JSON BR](./examples/sample_profile_br.json)

# Synthetic Profile Generator

Synthetic-first profile generator for development, QA, demos, staging, and seed data.

This simplified version intentionally generates only:

- `identity`
- `location` with country only
- `family` with only `father` and `mother`
- `credentials` with one email and one password
- optional synthetic national identifier for `BR`, `US`, and `FR`

Bundled locale packs keep very large first-name and surname pools so repeated runs stay much less repetitive. Each supported country currently ships with `900` male names, `900` female names, and `900` surnames.

Supported countries are intentionally limited to:

- `BR`
- `US`
- `FR`

Safety rules:

- no real identities
- no exact residential addresses
- no live deceptive inboxes
- no real-world identifiers beyond synthetic test-only formatting
- no fraud, impersonation, KYC, or verification-bypass use

## Output Shape

Default JSON output is minimal:

```json
{
  "identity": {
    "full_name": "Paulo Murilo Almeida Rangel",
    "gender": "male",
    "age": 53,
    "national_identifier": "031.105.283-55",
    "national_identifier_type": "cpf"
  },
  "location": {
    "country": "Brazil",
    "country_code": "BR"
  },
  "family": {
    "father": {
      "full_name": "Lucas Rangel",
      "gender": "male",
      "age": 80,
      "national_identifier": "495.231.846-01",
      "national_identifier_type": "cpf"
    },
    "mother": {
      "full_name": "Dandara Almeida",
      "gender": "female",
      "age": 83,
      "national_identifier": "852.066.438-58",
      "national_identifier_type": "cpf"
    }
  },
  "credentials": {
    "email": "ember-rangel441@example.org",
    "password": "aNHdN^,:ND3V6yY:G9g#-TT*"
  }
}
```

Debug mode adds only technical diagnostics:

- email provider details
- fallback reason
- RNG/seed diagnostics
- warnings

## Determinism

- Without `seed`: generation varies across runs
- With `seed`: same input produces the same output
- Batch generation remains deterministic per batch index when seed is provided

## Synthetic National Identifiers

The API field `include_cpf` keeps its old name for compatibility, but now means:

- `BR` -> synthetic `cpf`
- `US` -> synthetic `ssn_like`
- `FR` -> synthetic `nir_like`

Rules:

- optional
- synthetic only
- deterministic with seed
- checksum-valid for Brazilian CPF testing
- `US` and `FR` outputs are locale-shaped placeholders for UI/backend tests only
- always marked `safe_for_testing_only`

Use it only for tests.

## Run

### Local setup

```bash
cd /home/ven/synthetic-profile-generator
source .venv/bin/activate
```

Fish shell:

```fish
cd /home/ven/synthetic-profile-generator
source .venv/bin/activate.fish
```

### CLI

Generate one profile:

```bash
python main.py generate \
  --c BR \
  --g male \
  --f pretty
```

Generate using the default pretty mode:

```bash
python main.py generate \
  --c US \
  --g female
```

Generate a batch:

```bash
python main.py generate-batch \
  --count 50 \
  --c FR
```

CLI flags:

- `--c` country: `BR`, `US`, `FR`
- `--g` gender: `male`, `female`
- `--amin` minimum age
- `--amax` maximum age
- `--f` format: `compact`, `pretty`
- `--count` batch size for `generate-batch`

CLI defaults:

- synthetic national identifier included by default
- one email and one password always shown
- pretty output by default
- no `json` or `csv` output mode in CLI

### API

```bash
uvicorn synthetic_profiles.api.app:app --host 0.0.0.0 --port 8000 --reload
```

Endpoints:

- `GET /health`
- `GET /countries`
- `POST /generate-profile`
- `POST /generate-batch`

Example request:

```json
{
  "country_code": "BR",
  "gender": "male",
  "age_min": 21,
  "age_max": 45,
  "use_simplelogin": false,
  "seed": 10
}
```

## Environment Variables

See [`.env.example`](./.env.example).

Important ones:

- `SIMPLELOGIN_API_KEY`
- `SIMPLELOGIN_BASE_URL`
- `REQUEST_TIMEOUT_SECONDS`
- `FALLBACK_EMAIL_DOMAINS`
- `DEFAULT_COUNTRY_CODE`

## Testing

```bash
.venv/bin/python -m pytest -q
```

## Sample Outputs

- [BR sample JSON](./examples/sample_profile_br.json)

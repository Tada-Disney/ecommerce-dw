# E-commerce Data Warehouse

![dbt CI](https://github.com/Tada-Disney/ecommerce-dw/actions/workflows/dbt_ci.yml/badge.svg)

A dimensional data warehouse built on Azure SQL with dbt, modelling synthetic
e-commerce order data into a star schema with full change history tracking,
incremental fact loading, and automated CI.

## Architecture

Raw order, customer, and product data is generated with Python (Faker) and
loaded into Azure SQL. dbt then transforms it through three layers:

- **Staging** (views) — clean and standardise raw source tables
- **Dimensions** (tables) — `dim_customer` and `dim_product` with SCD Type 2
  history tracking via dbt snapshots, plus a `dim_date` seed
- **Facts** (incremental) — `fact_orders` loads only new records on each run
  using dbt's `is_incremental()` pattern

Data quality is enforced with `not_null` and `unique` tests on keys across
all layers.

## Star Schema

| Table | Type | Materialisation |
|---|---|---|
| `fact_orders` | Fact | Incremental |
| `dim_customer` | Dimension (SCD Type 2) | Table |
| `dim_product` | Dimension (SCD Type 2) | Table |
| `dim_date` | Dimension | Seed |

## CI/CD

Every push to `main` triggers a GitHub Actions workflow that spins up a fresh
runner, installs dbt and the SQL Server ODBC driver, builds a `profiles.yml`
from encrypted repository secrets, and runs `dbt build` against Azure SQL —
compiling all models and executing every test. The badge above reflects the
live status of the latest run.

## Tech Stack

- **Warehouse:** Azure SQL Database
- **Transformation:** dbt (dbt-sqlserver)
- **Data generation:** Python, Faker
- **CI/CD:** GitHub Actions
- **Version control:** Git / GitHub

## Project Structure

```
ecommerce_dbt/
├── models/
│   ├── staging/        # source-conformed views
│   ├── dimensions/     # dimension tables
│   └── facts/          # incremental fact models
├── seeds/              # dim_date.csv
├── snapshots/          # SCD Type 2 history tracking
└── tests/              # data quality tests
.github/workflows/      # CI pipeline (dbt_ci.yml)
src/generate_data.py    # synthetic data generation
```

## Running Locally

```bash
pip install dbt-sqlserver
cd ecommerce_dbt
dbt build
```

Requires a `~/.dbt/profiles.yml` with an `ecommerce_dbt` profile pointing at
an Azure SQL database, and the ODBC Driver 18 for SQL Server installed.
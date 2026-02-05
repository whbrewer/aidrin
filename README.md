# AIDRIN – AI Data Readiness Inspector

**AIDRIN** (AI Data Readiness Inspector) is a lightweight, open-source tool designed to evaluate the readiness of datasets for AI and machine learning workflows. It provides an intuitive web interface to assess dataset quality, completeness, and structure through quantitative metrics.

For installation, usage, and contribution guidelines, please refer to the [AIDRIN documentation](https://aidrin.readthedocs.io/en/latest/).

## Headless Mode

AIDRIN includes a headless mode for programmatic/CLI usage without the web interface. This is useful for automation, CI/CD pipelines, and integration with other tools like REDI.

### CLI Usage

```bash
# List available metrics
python -m aidrin.headless.cli list

# List metrics by category
python -m aidrin.headless.cli list --category data_quality

# Run a single metric
python -m aidrin.headless.cli run <metric_name> <file_path>

# Examples
python -m aidrin.headless.cli run completeness /path/to/data.csv
python -m aidrin.headless.cli run duplicity /path/to/data.csv
python -m aidrin.headless.cli run outliers /path/to/data.csv

# Run with options
python -m aidrin.headless.cli run class_imbalance /path/to/data.csv --target-column label
python -m aidrin.headless.cli run k_anonymity /path/to/data.csv --quasi-identifiers "age,zipcode,gender"

# Run batch metrics from config
python -m aidrin.headless.cli batch config.json
```

### Python API

```python
from aidrin.headless import run_metric, list_available_metrics, run_batch_metrics
from aidrin.headless.config import HeadlessConfig

# List available metrics
metrics = list_available_metrics()
for m in metrics:
    print(f"{m['name']} ({m['category']}): {m['description']}")

# Run a single metric
result = run_metric('completeness', '/path/to/data.csv', save_images=False)
print(result)
# {'Completeness scores': {'col1': 1.0, 'col2': 0.95, ...}, 'Overall Completeness': 0.98}

# Run multiple metrics via batch config
config = HeadlessConfig(
    file_path='/path/to/data.csv',
    metrics=['completeness', 'duplicity', 'outliers'],
)
results = run_batch_metrics(config)
```

### Available Metrics

| Category | Metric | Description | Required Args |
|----------|--------|-------------|---------------|
| data_quality | completeness | Column completeness scores | - |
| data_quality | duplicity | Dataset duplicity ratio | - |
| data_quality | outliers | Outlier proportions for numerical columns | - |
| correlation | correlations | Categorical and numerical correlation matrices | columns |
| correlation | feature_relevance | Feature relevance using Pearson correlation | cat_columns, num_columns, target_column |
| fairness | class_imbalance | Class imbalance degree and distribution | target_column |
| fairness | statistical_rates | Statistical rates across sensitive groups | y_true_column, sensitive_attribute_column |
| fairness | representation_rate | Representation rate ratios | columns |
| privacy | k_anonymity | k-anonymity score | quasi_identifiers |
| privacy | l_diversity | l-diversity score | quasi_identifiers, sensitive_column |
| privacy | t_closeness | t-closeness score | quasi_identifiers, sensitive_column |
| privacy | entropy_risk | Entropy risk score | quasi_identifiers |
| privacy | single_attribute_risk | Single attribute Markov-model risk | id_column, eval_columns |
| privacy | multiple_attribute_risk | Multiple attribute Markov-model risk | id_column, eval_columns |
| privacy | differential_privacy | Differential privacy noise statistics | columns, epsilon |

### Supported File Types

- CSV (`.csv`)
- Excel (`.xls`, `.xlsx`, `.xlsm`, `.xlsb`)
- Parquet (`.parquet`)
- JSON (`.json`)
- HDF5 (`.h5`, `.hdf5`)
- NumPy (`.npy`, `.npz`)

### Integration with REDI

AIDRIN headless mode can be used to validate REDI pipeline outputs:

```python
from aidrin.headless import run_metric

# Assess input data quality before REDI processing
input_result = run_metric('completeness', 'input_data.csv', save_images=False)
print(f"Input completeness: {input_result['Overall Completeness']}")

# Run REDI pipeline...

# Assess output data quality after REDI processing
output_result = run_metric('completeness', 'output/train.npz', save_images=False)
print(f"Output completeness: {output_result['Overall Completeness']}")
```

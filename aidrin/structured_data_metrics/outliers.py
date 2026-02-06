import base64
import io
import os

import matplotlib.pyplot as plt
import numpy as np
from celery import Task, shared_task
from celery.exceptions import SoftTimeLimitExceeded

from aidrin.file_handling.file_parser import read_file


def _headless():
    return os.environ.get("AIDRIN_HEADLESS", "").strip() not in ("", "0")


@shared_task(bind=True, ignore_result=False)
def outliers(self: Task, file_info):
    try:
        file = read_file(file_info)

        # Ensure DataFrame columns are strings to avoid numpy array issues
        if hasattr(file, 'columns'):
            file.columns = [str(col) for col in file.columns]

        try:
            out_dict = {}
            # Select numerical columns for outlier detection
            numerical_columns = file.select_dtypes(include=[np.number])

            if numerical_columns.empty:
                return {"Error": "No numerical features found in the dataset."}

            # Vectorized outlier detection across all columns at once
            q1 = numerical_columns.quantile(0.25)
            q3 = numerical_columns.quantile(0.75)
            iqr = q3 - q1

            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr

            # Boolean mask: True where value is an outlier
            outlier_mask = (numerical_columns < lower) | (numerical_columns > upper)
            # For zero-IQR columns, mark as no outliers
            zero_iqr = iqr == 0
            outlier_mask.loc[:, zero_iqr] = False

            # Proportion of outliers per column (ignoring NaNs)
            proportions = outlier_mask.mean()
            proportions_dict = {str(k): v for k, v in proportions.to_dict().items()}

            # Overall outlier score
            valid_values = [v for v in proportions_dict.values() if not np.isnan(v)]
            average_value = np.mean(valid_values) if valid_values else 0.0
            proportions_dict["Overall outlier score"] = average_value
            out_dict["Outlier scores"] = proportions_dict

            # Skip visualization in headless mode
            if not _headless():
                _MAX_BAR_FEATURES = 100
                feature_scores = {
                    k: v for k, v in proportions_dict.items() if k != "Overall outlier score"
                }
                n_features = len(feature_scores)

                if feature_scores:
                    plt.figure(figsize=(8, 8))
                    if n_features > _MAX_BAR_FEATURES:
                        scores = list(feature_scores.values())
                        plt.hist(scores, bins=min(50, n_features), color="red", edgecolor="black")
                        plt.title(f"Outlier Proportion Distribution ({n_features} features)", fontsize=14)
                        plt.xlabel("Proportion of Outliers", fontsize=14)
                        plt.ylabel("Number of Features", fontsize=14)
                    else:
                        plt.bar(feature_scores.keys(), feature_scores.values(), color="red")
                        plt.title("Proportion of Outliers for Numerical Columns", fontsize=14)
                        plt.xlabel("Columns", fontsize=14)
                        plt.ylabel("Proportion of Outliers", fontsize=14)
                        plt.ylim(0, 1)
                        plt.xticks(rotation=45, ha="right", fontsize=12)
                        plt.subplots_adjust(bottom=0.5)
                    plt.tight_layout()

                    img_buf = io.BytesIO()
                    plt.savefig(img_buf, format="png")
                    img_buf.seek(0)
                    img_base64 = base64.b64encode(img_buf.read()).decode("utf-8")

                    out_dict["Outliers Visualization"] = img_base64
                    plt.close()

            return out_dict

        except Exception as e:
            return {"Error": f"Outlier detection failed: {str(e)}"}

    except SoftTimeLimitExceeded:
        raise Exception("Outliers task timed out.")

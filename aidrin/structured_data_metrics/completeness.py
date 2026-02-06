import base64
import io
import os

import matplotlib.pyplot as plt
from celery import Task, shared_task
from celery.exceptions import SoftTimeLimitExceeded

from aidrin.file_handling.file_parser import read_file


def _headless():
    return os.environ.get("AIDRIN_HEADLESS", "").strip() not in ("", "0")


@shared_task(bind=True, ignore_result=False)
def completeness(self: Task, file_info):
    try:
        file = read_file(file_info)

        # Ensure DataFrame columns are strings to avoid numpy array issues
        if hasattr(file, 'columns'):
            file.columns = [str(col) for col in file.columns]

        # Calculate completeness metric for each column
        try:
            completeness_scores = (1 - file.isnull().mean()).to_dict()
        except Exception:
            # If to_dict() fails, manually create the dictionary
            completeness_scores = {}
            for col in file.columns:
                try:
                    completeness_scores[str(col)] = float(1 - file[col].isnull().mean())
                except Exception:
                    completeness_scores[str(col)] = 0.0

        # Ensure all column names are strings to avoid numpy array issues
        completeness_scores = {str(k): v for k, v in completeness_scores.items()}

        # Calculate overall completeness metric for the dataset
        overall_completeness = 1 - file.isnull().any(axis=1).mean()

        result_dict = {}

        # Always include completeness scores for all features
        result_dict["Completeness scores"] = completeness_scores
        result_dict["Overall Completeness"] = overall_completeness

        # Skip visualization in headless mode
        if not _headless():
            _MAX_BAR_FEATURES = 100
            n_features = len(completeness_scores)

            plt.figure(figsize=(8, 6))
            if n_features > _MAX_BAR_FEATURES:
                scores = list(completeness_scores.values())
                plt.hist(scores, bins=min(50, n_features), color="blue", edgecolor="black")
                plt.title(f"Completeness Score Distribution ({n_features} features)", fontsize=16)
                plt.xlabel("Completeness Score", fontsize=14)
                plt.ylabel("Number of Features", fontsize=14)
            else:
                plt.bar(completeness_scores.keys(), completeness_scores.values(), color="blue")
                plt.title("Feature-wise Completeness Scores", fontsize=16)
                plt.xlabel("Features", fontsize=14)
                plt.ylabel("Completeness Score", fontsize=14)
                plt.ylim(0, 1)
                plt.xticks(rotation=45, ha="right", fontsize=12)
            plt.tight_layout()

            img_buf = io.BytesIO()
            plt.savefig(img_buf, format="png")
            img_buf.seek(0)
            img_base64 = base64.b64encode(img_buf.read()).decode("utf-8")

            result_dict["Completeness Visualization"] = img_base64
            plt.close()

        return result_dict

    except SoftTimeLimitExceeded:
        raise Exception("Completeness task timed out.")

from celery import Task, shared_task
from celery.exceptions import SoftTimeLimitExceeded

from aidrin.file_handling.file_parser import read_file


def _make_hashable(val):
    """Convert unhashable types (lists, dicts) to hashable equivalents."""
    if isinstance(val, list):
        return tuple(_make_hashable(v) for v in val)
    elif isinstance(val, dict):
        return tuple(sorted((k, _make_hashable(v)) for k, v in val.items()))
    return val


@shared_task(bind=True, ignore_result=False)
def duplicity(self: Task, file_info):
    try:
        file = read_file(file_info)
        dup_dict = {}

        # Check if any columns contain unhashable types (lists, dicts)
        # and convert them to hashable equivalents for duplicate detection
        hashable_file = file.copy()
        for col in hashable_file.columns:
            if hashable_file[col].dtype == object:
                # Check first non-null value to see if it's unhashable
                first_val = hashable_file[col].dropna().iloc[0] if not hashable_file[col].dropna().empty else None
                if isinstance(first_val, (list, dict)):
                    hashable_file[col] = hashable_file[col].apply(_make_hashable)

        # Calculate the proportion of duplicate values
        duplicate_proportions = hashable_file.duplicated().sum() / len(hashable_file)

        dup_dict["Duplicity scores"] = {
            "Overall duplicity of the dataset": duplicate_proportions
        }

        return dup_dict
    except SoftTimeLimitExceeded:
        raise Exception("Duplicity task timed out.")

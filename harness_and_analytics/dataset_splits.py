"""
Dataset Curation and Abnormal-Only Evaluation Slice Manager.
Member 3 (Manya - Business Systems & CSE DS Lead).
Segments clinical ultrasound dictations into standardized train/test splits
and isolates a dedicated Abnormal-Only Evaluation Slice required by the rubric.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Tuple


class DatasetSplitManager:
    """
    Manages clinical ultrasound evaluation datasets and creates specialized slices.
    """

    def __init__(self, data_source_path: str = None):
        if data_source_path:
            with open(data_source_path, "r", encoding="utf-8") as f:
                self.raw_data = json.load(f)
        else:
            default_path = Path(__file__).parent.parent / "data" / "sample_transcripts.json"
            with open(default_path, "r", encoding="utf-8") as f:
                self.raw_data = json.load(f)

        self.cases: List[Dict[str, Any]] = self.raw_data.get("cases", [])

    def get_abnormal_only_slice(self) -> List[Dict[str, Any]]:
        """
        Extracts the specialized Abnormal-Only Evaluation Slice.
        Mandatory Rubric Outcome: Tests system sensitivity on acute pathologies.
        """
        return [c for c in self.cases if c.get("is_abnormal", False)]

    def get_normal_baseline_slice(self) -> List[Dict[str, Any]]:
        """Extracts normal/unremarkable baseline cases."""
        return [c for c in self.cases if not c.get("is_abnormal", False)]

    def create_train_val_test_splits(
        self,
        train_ratio: float = 0.6,
        val_ratio: float = 0.2,
        test_ratio: float = 0.2
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Creates stratified dataset splits balancing normal and abnormal proportions."""
        abnormals = self.get_abnormal_only_slice()
        normals = self.get_normal_baseline_slice()

        def split_subset(subset: List[Any]) -> Tuple[List[Any], List[Any], List[Any]]:
            n = len(subset)
            n_tr = max(1, int(n * train_ratio))
            n_va = max(0, int(n * val_ratio))
            return subset[:n_tr], subset[n_tr : n_tr + n_va], subset[n_tr + n_va :]

        ab_tr, ab_va, ab_te = split_subset(abnormals)
        no_tr, no_va, no_te = split_subset(normals)

        return {
            "train": ab_tr + no_tr,
            "validation": ab_va + no_va,
            "test": ab_te + no_te,
            "abnormal_evaluation_slice": abnormals
        }

"""
JSON 직렬화 유틸리티
NaN, Inf 등 JSON 비호환 값을 안전하게 처리
"""
import json
import numpy as np
import pandas as pd
from typing import Any, Dict, List

def safe_serialize(data: Any) -> Any:
    """
    JSON 직렬화 시 NaN, Inf 등을 안전하게 처리
    """
    if isinstance(data, dict):
        return {k: safe_serialize(v) for k, v in data.items()}
    elif isinstance(data, (list, tuple)):
        return [safe_serialize(item) for item in data]
    elif isinstance(data, (np.integer, np.int64, np.int32)):
        return int(data)
    elif isinstance(data, (np.floating, np.float64, np.float32, float)):
        if np.isnan(data) or np.isinf(data):
            return None
        return float(data)
    elif isinstance(data, (np.ndarray, pd.Series)):
        return safe_serialize(data.tolist())
    elif pd.isna(data):
        return None
    else:
        return data

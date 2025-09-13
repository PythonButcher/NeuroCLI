```python
from typing import List, Dict, Union

def calculate_stats(data: List[Union[int, float]]) -> Dict[str, Union[int, float]]:
  """Calculates the total and average of a list of numbers.

  Args:
    data: A list of numbers (integers or floats).

  Returns:
    A dictionary containing the total and average of the input data.
    Returns an average of 0 if the input list is empty.

    The dictionary has the following structure:
    {
        "total": <sum of numbers>,
        "average": <average of numbers>
    }
  """
  total = sum(data)
  count = len(data)
  average = total / count if count > 0 else 0
  return {"total": total, "average": average}
```

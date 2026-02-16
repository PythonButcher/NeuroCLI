def calculate_stats(data):
    # test sync after moving repo
    """Calculates the sum and average of a list of numbers.

    Args:
        data: A list of numbers.

    Returns:
        A dictionary containing the sum and average of the numbers.
        Returns an average of 0 if the input list is empty.
    """
    total = sum(data)
    count = len(data)
    average = total / count if count > 0 else 0
    return {"total": total, "average": average}

def number_to_label_nfc(n: int) -> str:
    """1 -> A, 2 -> B, ..., 26 -> Z, 27 -> AA, 28 -> AB ..."""
    label = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        label = chr(65 + remainder) + label
    return label
import random


def generate_nfc_uid() -> str:
    """
    Генерирует случайный NFC UID 7 байт в формате XX:XX:XX:XX:XX:XX:XX
    """
    uid_bytes = [0x02] + [random.randint(0x00, 0xFF) for _ in range(6)] #noqa
    uid_str = ":".join(f"{b:02X}" for b in uid_bytes)
    return uid_str

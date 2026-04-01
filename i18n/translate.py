from .translations import TRANSLATIONS


def t(key: str, lang: str = 'uz') -> str:
    """
    Translate a text key into the specified language.

    This function looks up the given translation key in the TRANSLATIONS
    dictionary and returns the corresponding text for the provided language.
    If the key or language is not found, the key itself is returned as a
    fallback to avoid raising errors.

    Args:
        key (str): Translation key (e.g., "greeting", "bye").
        lang (str, optional): Language code ("uz", "ru"). Defaults to "uz".

    Returns:
        str: Translated text if found, otherwise the key itself.

    Example:
        >>> t("greeting", "ru")
        'Привет'
        >>> t("unknown_key", "uz")
        'unknown_key'
    """
    return TRANSLATIONS.get(key, {}).get(lang, key)

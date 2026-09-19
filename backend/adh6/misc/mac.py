import string


def get_mac_variations(addr: str) -> list[str]:
    normalized = "".join(character for character in addr if character in string.hexdigits).lower()
    variations: list[str] = []
    variations += ["{}:{}:{}:{}:{}:{}".format(*(normalized[i * 2 : (i + 1) * 2] for i in range(6)))]
    variations += ["{}-{}-{}-{}-{}-{}".format(*(normalized[i * 2 : (i + 1) * 2] for i in range(6)))]
    variations += ["{}.{}.{}".format(*(normalized[i * 4 : (i + 1) * 4] for i in range(3)))]
    variations += [x.upper() for x in variations]
    return variations

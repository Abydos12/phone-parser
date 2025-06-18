from dataclasses import dataclass, field
from enum import StrEnum, auto
from typing import Generator


class PhoneCategory(StrEnum):
    MOBILE = "MOBILE"
    FIXE = "FIXE"
    M2M = "M2M"

@dataclass
class PhoneMetadata:
    international_prefix: str
    country: str
    territory: str
    category: PhoneCategory
    length: int  # expected length without international_prefix
    roots: list[str]

    @property
    def international_length(self):
        return len(self.international_prefix) + self.length


def roots(*raw_roots: str) -> list[str]:
    return list(parse_roots(*raw_roots))


def parse_roots(*raw_roots: str) -> Generator[str]:
    """
    Parse list like ["40", "42-44"] into ["40", "42", "43", "44"]
    :param raw_roots:
    :return:
    """

    for raw_root in raw_roots:
        if "-" in raw_root:
            start, end = raw_root.split("-")
        else:
            start, end = raw_root, raw_root
        for r in range(int(start), int(end) + 1):
            yield str(r)


metadata = [
    PhoneMetadata(
        international_prefix="33",
        country="FR",
        territory="France Métropolitaine",
        category=PhoneCategory.MOBILE,
        length=9,
        roots=roots(
            "61",
            "62",
            "64",
            "66-68",
            "73-78",
            "601-609",
            "630-638",
            "650-652",
            "656-659",
            "695",
            "698",
            "699",
        ),
    ),
    PhoneMetadata(
        international_prefix="590",
        country="FR",
        territory="Guadeloupe, Saint-Martin et Saint-Barthélemy",
        category=PhoneCategory.MOBILE,
        length=9,
        roots=roots("690", "691"),
    ),
    PhoneMetadata(
        international_prefix="594",
        country="FR",
        territory="Guyane",
        category=PhoneCategory.MOBILE,
        length=9,
        roots=roots("694"),
    ),
    PhoneMetadata(
        international_prefix="596",
        country="FR",
        territory="Martinique",
        category=PhoneCategory.MOBILE,
        length=9,
        roots=roots("696","697"),
    ),
    PhoneMetadata(
        international_prefix="262",
        country="FR",
        territory="La Réunion, Mayotte et autres territoires de l’Océan Indien",
        category=PhoneCategory.MOBILE,
        length=9,
        roots=roots("639", "692", "693"),
    ),
    PhoneMetadata(
        international_prefix="508",
        country="FR",
        territory="Saint-Pierre-et-Miquelon",
        category=PhoneCategory.MOBILE,
        length=9,
        roots=roots( "70840-70845", "70850-70855"),
    ),
]


@dataclass
class Node:
    metadata: PhoneMetadata | None = None
    children: dict[str, "Node"] = field(default_factory=dict)


def insert(node: Node, meta: list[PhoneMetadata]) -> None:
    for m in meta:
        for r in m.roots:
            location = f"{m.international_prefix}{r}"
            _insert(node, m, location)


def _insert(node: Node, meta: PhoneMetadata, location: str):
    if location == "":
        node.metadata = meta
        return

    char: str = location[0]

    if char not in node.children:
        node.children[char] = Node()

    _insert(node.children[char], meta, location[1:])


international_tree: Node = Node()


insert(international_tree, metadata)


def parse(phone: str) -> PhoneMetadata | None:
    def _parse(chars: str, node: Node) -> PhoneMetadata | None:
        if chars == "":
            return node.metadata

        child = node.children.get(chars[0])
        # if no next node to explore and current node is not a leaf
        if child is None and node.metadata is None:
            return None

        # if no next node to explore and current node is a leaf
        elif child is None and node.metadata is not None:
            # we only match root digits so number can be longer than where is current node is
            # I'm lazy I'm just writing an international tree but we could also do local parsing with this kind of trees
            if node.metadata.international_length == len(phone):
                return node.metadata
            return None

        return _parse(chars[1:], child)

    return _parse(phone, international_tree)


if __name__ == "__main__":
    phones = ["33695919388"]

    for phone in phones:
        result = parse(phone)
        if result is None:
            print(f"{phone}: UNKNOWN")
        else:
            print(f"{phone}: {result.country} | {result.category} | {result.territory}")

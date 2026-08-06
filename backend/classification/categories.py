from enum import Enum
from typing import Dict


class SpeciesCategory(str, Enum):
    MARINE = "Marine"
    FRESHWATER = "Freshwater"
    TERRESTRIAL = "Terrestrial"
    PLANT = "Plant"
    ANIMAL = "Animal"
    FUNGI = "Fungi"
    PROTIST = "Protist"
    BACTERIA = "Bacteria"
    ARCHAEA = "Archaea"
    UNKNOWN = "Unknown"


# TODO:
# Externalize this mapping into a configuration file / database table once
# the real taxonomy-to-category rules are defined by domain experts.
KINGDOM_CATEGORY_MAP: Dict[str, SpeciesCategory] = {
    "Animalia": SpeciesCategory.ANIMAL,
    "Plantae": SpeciesCategory.PLANT,
    "Fungi": SpeciesCategory.FUNGI,
    "Protista": SpeciesCategory.PROTIST,
    "Bacteria": SpeciesCategory.BACTERIA,
    "Archaea": SpeciesCategory.ARCHAEA,
}

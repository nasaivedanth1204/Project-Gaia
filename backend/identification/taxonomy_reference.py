from typing import Any, Dict, List

# TODO:
# Replace this static template with a real taxonomic reference database
# (e.g. NCBI, SILVA, BOLD) or the output of a trained classifier. These
# entries exist only to demonstrate the hierarchical response shape.
TAXONOMY_TEMPLATE: List[Dict[str, Any]] = [
    {
        "kingdom": "Animalia",
        "phylum": "Chordata",
        "class": "Actinopterygii",
        "order": "Perciformes",
        "family": "Example_Family_A",
        "genus": "Example_Genus_A",
        "species": "Example_species_a",
    },
    {
        "kingdom": "Plantae",
        "phylum": "Tracheophyta",
        "class": "Magnoliopsida",
        "order": "Example_Order_B",
        "family": "Example_Family_B",
        "genus": "Example_Genus_B",
        "species": "Example_species_b",
    },
    {
        "kingdom": "Protista",
        "phylum": "Example_Phylum_C",
        "class": "Example_Class_C",
        "order": "Example_Order_C",
        "family": "Example_Family_C",
        "genus": "Example_Genus_C",
        "species": "Example_species_c",
    },
    {
        "kingdom": "Bacteria",
        "phylum": "Example_Phylum_D",
        "class": "Example_Class_D",
        "order": "Example_Order_D",
        "family": "Example_Family_D",
        "genus": "Example_Genus_D",
        "species": "Example_species_d",
    },
    {
        "kingdom": "Unknown",
        "phylum": "Unknown",
        "class": "Unknown",
        "order": "Unknown",
        "family": "Unknown",
        "genus": "Unknown",
        "species": "Unknown",
    },
]

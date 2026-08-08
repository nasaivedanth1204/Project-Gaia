"""Curated reference tables for the Gaia synthetic seed database.

These tables are hand-authored (rather than randomly generated) because
they form the referential spine of the dataset:

    Biosphere -> Biome -> Terrain -> Ecosystem -> Location -> Sampling Site

Taxonomic names are real scientific names, used so the prototype exercises
realistic hierarchies. The OBSERVATIONS built on top of them in build.py
are entirely synthetic: no record here asserts that any organism was
actually detected at any location.
"""

# ---------------------------------------------------------------------------
# Biospheres
# ---------------------------------------------------------------------------
BIOSPHERES = [
    ("BIOS-001", "Terrestrial", "Land-based environments including forests, grasslands and deserts.", "Terrestrial"),
    ("BIOS-002", "Freshwater", "Freshwater environments including rivers, lakes and wetlands.", "Aquatic"),
    ("BIOS-003", "Marine", "Saltwater environments from coastal shelves to the open and deep ocean.", "Aquatic"),
    ("BIOS-004", "Transitional", "Land-water interfaces such as estuaries, mangroves and salt marshes.", "Transitional"),
    ("BIOS-005", "Anthropogenic", "Human-modified environments including agricultural, urban and industrial systems.", "Anthropogenic"),
    ("BIOS-006", "Subterranean", "Below-ground environments including caves, karst systems and groundwater.", "Subterranean"),
    ("BIOS-007", "Cryospheric", "Permanently or seasonally frozen environments such as glaciers and permafrost.", "Cryospheric"),
    ("BIOS-008", "Atmospheric", "Airborne environments sampled for suspended biological material.", "Aerial"),
    ("BIOS-009", "Coastal", "Nearshore environments influenced by both marine and terrestrial processes.", "Transitional"),
    ("BIOS-010", "Extreme", "Environments with extreme chemistry or temperature, including hydrothermal and hypersaline systems.", "Extreme"),
]

# ---------------------------------------------------------------------------
# Biomes  (biome_id, biosphere_id, name, description, climate, temp_c, precip_mm)
# ---------------------------------------------------------------------------
BIOMES = [
    ("BIOM-001", "BIOS-001", "Tropical Rainforest", "Closed-canopy evergreen forest with high year-round rainfall.", "Tropical humid", [22, 32], [2000, 4000]),
    ("BIOM-002", "BIOS-001", "Temperate Forest", "Deciduous and mixed forest with pronounced seasonality.", "Temperate", [5, 25], [750, 1500]),
    ("BIOM-003", "BIOS-001", "Grassland", "Herbaceous vegetation with limited tree cover.", "Semi-arid to temperate", [10, 30], [400, 900]),
    ("BIOM-004", "BIOS-001", "Savanna", "Grassland with scattered drought-tolerant trees.", "Tropical wet-dry", [20, 35], [500, 1200]),
    ("BIOM-005", "BIOS-001", "Desert", "Arid environment with sparse vegetation and high diurnal range.", "Arid", [5, 45], [50, 250]),
    ("BIOM-006", "BIOS-007", "Tundra", "Treeless environment underlain by seasonally frozen ground.", "Polar / alpine", [-25, 12], [150, 400]),
    ("BIOM-007", "BIOS-001", "Alpine", "High-altitude environment above the tree line.", "Alpine", [-15, 15], [700, 1800]),
    ("BIOM-008", "BIOS-004", "Mangrove", "Intertidal forest of salt-tolerant trees.", "Tropical coastal", [22, 34], [1500, 3000]),
    ("BIOM-009", "BIOS-003", "Coral Reef", "Shallow marine ecosystem built by reef-forming corals.", "Tropical marine", [24, 30], None),
    ("BIOM-010", "BIOS-003", "Open Ocean", "Pelagic waters beyond the continental shelf.", "Oceanic", [4, 29], None),
    ("BIOM-011", "BIOS-003", "Deep Sea", "Aphotic waters and sediments below 200 m.", "Deep oceanic", [1, 6], None),
    ("BIOM-012", "BIOS-002", "Freshwater Lentic", "Standing freshwater such as lakes and reservoirs.", "Variable", [4, 30], None),
    ("BIOM-013", "BIOS-002", "Freshwater Lotic", "Flowing freshwater such as rivers and streams.", "Variable", [2, 30], None),
    ("BIOM-014", "BIOS-002", "Wetland", "Seasonally or permanently waterlogged land.", "Variable", [10, 32], [800, 2500]),
    ("BIOM-015", "BIOS-009", "Coastal", "Nearshore shelf waters, beaches and rocky shores.", "Coastal", [18, 31], None),
    ("BIOM-016", "BIOS-004", "Estuarine", "Semi-enclosed water bodies where rivers meet the sea.", "Coastal", [15, 32], None),
    ("BIOM-017", "BIOS-005", "Agricultural", "Cultivated land under managed cropping regimes.", "Managed", [10, 38], [400, 2000]),
]

# ---------------------------------------------------------------------------
# Terrains  (terrain_id, name, description, environment_type, climate,
#            temp_c, humidity_pct, altitude_m, salinity_psu, parent_biome_id)
# Terrain describes physical form; ecosystem describes the functioning
# biological system. They are deliberately kept as separate concepts.
# ---------------------------------------------------------------------------
TERRAINS = [
    ("TER-001", "Tropical Forest", "Dense multi-layered forest on humid lowland terrain.", "Terrestrial", "Tropical humid", [22, 32], [70, 95], [0, 1200], None, "BIOM-001"),
    ("TER-002", "Temperate Forest", "Seasonal broadleaf and mixed forest terrain.", "Terrestrial", "Temperate", [5, 25], [55, 85], [100, 2000], None, "BIOM-002"),
    ("TER-003", "Mangrove", "Tidal mudflat terrain colonised by aerial-rooted trees.", "Transitional", "Tropical coastal", [22, 34], [75, 95], [0, 5], [5, 25], "BIOM-008"),
    ("TER-004", "Coastal", "Beach, dune and rocky-shore terrain along the shoreline.", "Transitional", "Coastal", [18, 33], [60, 90], [0, 50], [28, 35], "BIOM-015"),
    ("TER-005", "Coral Reef", "Shallow calcium-carbonate reef structure.", "Marine", "Tropical marine", [24, 30], None, [-40, 0], [32, 36], "BIOM-009"),
    ("TER-006", "Open Ocean", "Unbounded pelagic water column.", "Marine", "Oceanic", [4, 29], None, [-2000, 0], [33, 37], "BIOM-010"),
    ("TER-007", "Estuary", "Tidal river mouth with strong salinity gradient.", "Transitional", "Coastal", [15, 32], [70, 95], [0, 10], [0.5, 30], "BIOM-016"),
    ("TER-008", "River", "Channelised flowing freshwater terrain.", "Freshwater", "Variable", [2, 30], None, [0, 3500], [0, 0.5], "BIOM-013"),
    ("TER-009", "Lake", "Enclosed standing freshwater basin.", "Freshwater", "Variable", [4, 30], None, [0, 4500], [0, 0.5], "BIOM-012"),
    ("TER-010", "Wetland", "Waterlogged terrain with emergent vegetation.", "Freshwater", "Variable", [10, 32], [80, 100], [0, 1000], [0, 2], "BIOM-014"),
    ("TER-011", "Grassland", "Open herbaceous terrain with deep soils.", "Terrestrial", "Semi-arid to temperate", [10, 30], [40, 70], [100, 1500], None, "BIOM-003"),
    ("TER-012", "Savanna", "Open woodland-grassland mosaic.", "Terrestrial", "Tropical wet-dry", [20, 35], [35, 70], [100, 1200], None, "BIOM-004"),
    ("TER-013", "Desert", "Sand or rock terrain with minimal vegetation cover.", "Terrestrial", "Arid", [5, 45], [10, 35], [0, 1000], None, "BIOM-005"),
    ("TER-014", "Semi-Arid", "Transitional scrub terrain between grassland and desert.", "Terrestrial", "Semi-arid", [10, 42], [20, 50], [50, 1200], None, "BIOM-005"),
    ("TER-015", "Mountain", "Steep high-relief terrain below the tree line.", "Terrestrial", "Montane", [-5, 22], [45, 85], [1000, 3500], None, "BIOM-007"),
    ("TER-016", "Alpine", "High-altitude terrain above the tree line.", "Terrestrial", "Alpine", [-15, 15], [40, 80], [3000, 5500], None, "BIOM-007"),
    ("TER-017", "Tundra", "Frozen or seasonally thawed treeless terrain.", "Terrestrial", "Polar / alpine", [-25, 12], [50, 90], [0, 4000], None, "BIOM-006"),
    ("TER-018", "Agricultural", "Managed cropland and irrigation terrain.", "Anthropogenic", "Managed", [10, 38], [40, 85], [0, 2000], None, "BIOM-017"),
    ("TER-019", "Urban", "Built terrain with impervious surfaces and drainage networks.", "Anthropogenic", "Managed", [12, 40], [35, 80], [0, 1500], None, "BIOM-017"),
    ("TER-020", "Deep Marine", "Abyssal sediment and deep water-column terrain.", "Marine", "Deep oceanic", [1, 6], None, [-4000, -200], [34, 35], "BIOM-011"),
    ("TER-021", "Freshwater", "Generic inland freshwater terrain.", "Freshwater", "Variable", [4, 30], None, [0, 4000], [0, 0.5], "BIOM-012"),
]

# ---------------------------------------------------------------------------
# Ecosystems  (ecosystem_id, biome_id, terrain_id, biosphere_id, name,
#              description, ecosystem_type, climate)
# ---------------------------------------------------------------------------
ECOSYSTEMS = [
    ("ECO-001", "BIOM-001", "TER-001", "BIOS-001", "Tropical Rainforest Ecosystem", "Evergreen closed-canopy forest system with high endemism.", "Terrestrial", "Tropical humid"),
    ("ECO-002", "BIOM-002", "TER-002", "BIOS-001", "Temperate Forest Ecosystem", "Seasonal forest system with deciduous leaf turnover.", "Terrestrial", "Temperate"),
    ("ECO-003", "BIOM-003", "TER-011", "BIOS-001", "Grassland Ecosystem", "Grazing-adapted herbaceous system.", "Terrestrial", "Semi-arid to temperate"),
    ("ECO-004", "BIOM-004", "TER-012", "BIOS-001", "Savanna Ecosystem", "Fire- and grazing-maintained wooded grassland.", "Terrestrial", "Tropical wet-dry"),
    ("ECO-005", "BIOM-005", "TER-013", "BIOS-001", "Desert Ecosystem", "Water-limited system with drought-adapted biota.", "Terrestrial", "Arid"),
    ("ECO-006", "BIOM-007", "TER-015", "BIOS-001", "Montane Forest Ecosystem", "Mid-altitude forest system on steep relief.", "Terrestrial", "Montane"),
    ("ECO-007", "BIOM-007", "TER-016", "BIOS-001", "Alpine Meadow Ecosystem", "Short-season high-altitude herbaceous system.", "Terrestrial", "Alpine"),
    ("ECO-008", "BIOM-013", "TER-008", "BIOS-002", "River Ecosystem", "Flowing freshwater system with longitudinal zonation.", "Freshwater", "Variable"),
    ("ECO-009", "BIOM-012", "TER-009", "BIOS-002", "Lake Ecosystem", "Standing freshwater system with stratification.", "Freshwater", "Variable"),
    ("ECO-010", "BIOM-013", "TER-008", "BIOS-002", "Headwater Stream Ecosystem", "Cool, well-oxygenated first-order stream system.", "Freshwater", "Montane"),
    ("ECO-011", "BIOM-014", "TER-010", "BIOS-002", "Wetland Ecosystem", "Seasonally inundated system with emergent macrophytes.", "Freshwater", "Variable"),
    ("ECO-012", "BIOM-012", "TER-009", "BIOS-005", "Reservoir Ecosystem", "Impounded freshwater system under managed flow.", "Anthropogenic", "Managed"),
    ("ECO-013", "BIOM-010", "TER-006", "BIOS-003", "Open Ocean Ecosystem", "Pelagic system dominated by plankton production.", "Marine", "Oceanic"),
    ("ECO-014", "BIOM-009", "TER-005", "BIOS-003", "Coral Reef Ecosystem", "High-diversity reef system built on scleractinian corals.", "Marine", "Tropical marine"),
    ("ECO-015", "BIOM-011", "TER-020", "BIOS-003", "Deep Sea Ecosystem", "Aphotic system reliant on detrital and chemosynthetic input.", "Marine", "Deep oceanic"),
    ("ECO-016", "BIOM-015", "TER-004", "BIOS-009", "Coastal Waters Ecosystem", "Productive nearshore shelf system.", "Marine", "Coastal"),
    ("ECO-017", "BIOM-016", "TER-007", "BIOS-004", "Estuarine Ecosystem", "Salinity-gradient system with high nutrient turnover.", "Transitional", "Coastal"),
    ("ECO-018", "BIOM-008", "TER-003", "BIOS-004", "Mangrove Ecosystem", "Intertidal forest system acting as nursery habitat.", "Transitional", "Tropical coastal"),
    ("ECO-019", "BIOM-016", "TER-007", "BIOS-004", "Lagoon Ecosystem", "Shallow semi-enclosed brackish system.", "Transitional", "Coastal"),
    ("ECO-020", "BIOM-008", "TER-003", "BIOS-004", "Salt Marsh Ecosystem", "Halophyte-dominated intertidal system.", "Transitional", "Coastal"),
    ("ECO-021", "BIOM-017", "TER-018", "BIOS-005", "Agricultural Ecosystem", "Managed cropping system with periodic disturbance.", "Anthropogenic", "Managed"),
    ("ECO-022", "BIOM-017", "TER-019", "BIOS-005", "Urban Freshwater Ecosystem", "Channelised urban drainage and pond system.", "Anthropogenic", "Managed"),
    ("ECO-023", "BIOM-015", "TER-004", "BIOS-005", "Industrial Coastal Ecosystem", "Nearshore system under industrial effluent pressure.", "Anthropogenic", "Coastal"),
    ("ECO-024", "BIOM-001", "TER-001", "BIOS-005", "Restored Forest Ecosystem", "Actively restored secondary forest system.", "Anthropogenic", "Tropical humid"),
]

# ---------------------------------------------------------------------------
# Locations — India-focused, globally extensible.
# Coordinates are plausible regional centroids for SYNTHETIC sampling
# scenarios. They do not denote real sampling campaigns.
# (location_id, country, state, region, lat, lon, elevation_m, climate_zone,
#  terrain_id, ecosystem_id)
# ---------------------------------------------------------------------------
LOCATIONS = [
    ("LOC-001", "India", "Kerala", "Western Ghats", 10.1632, 76.9500, 980, "Tropical humid", "TER-001", "ECO-001"),
    ("LOC-002", "India", "Karnataka", "Western Ghats", 13.3400, 75.1200, 760, "Tropical humid", "TER-001", "ECO-001"),
    ("LOC-003", "India", "Tamil Nadu", "Nilgiri Hills", 11.4100, 76.6950, 2200, "Montane", "TER-015", "ECO-006"),
    ("LOC-004", "India", "Sikkim", "Eastern Himalayas", 27.5330, 88.5122, 3400, "Alpine", "TER-016", "ECO-007"),
    ("LOC-005", "India", "Arunachal Pradesh", "Eastern Himalayas", 27.1000, 93.6200, 1850, "Montane", "TER-015", "ECO-006"),
    ("LOC-006", "India", "West Bengal", "Sundarbans", 21.9497, 88.9000, 3, "Tropical coastal", "TER-003", "ECO-018"),
    ("LOC-007", "India", "Andaman & Nicobar Islands", "Andaman Islands", 11.7401, 92.6586, -12, "Tropical marine", "TER-005", "ECO-014"),
    ("LOC-008", "India", "Lakshadweep", "Lakshadweep Atolls", 10.5667, 72.6417, -8, "Tropical marine", "TER-005", "ECO-014"),
    ("LOC-009", "India", "Rajasthan", "Thar Desert", 27.0238, 71.5000, 240, "Arid", "TER-013", "ECO-005"),
    ("LOC-010", "India", "Maharashtra", "Deccan Plateau", 18.5204, 74.8567, 560, "Semi-arid", "TER-014", "ECO-003"),
    ("LOC-011", "India", "Assam", "Brahmaputra Basin", 26.6528, 92.7926, 55, "Tropical humid", "TER-008", "ECO-008"),
    ("LOC-012", "India", "Uttar Pradesh", "Ganga Basin", 25.3176, 82.9739, 80, "Subtropical", "TER-008", "ECO-008"),
    ("LOC-013", "India", "Telangana", "Godavari Basin", 18.6725, 79.0900, 145, "Tropical wet-dry", "TER-008", "ECO-008"),
    ("LOC-014", "India", "Odisha", "Chilika Lagoon", 19.7100, 85.3200, 1, "Tropical coastal", "TER-007", "ECO-019"),
    ("LOC-015", "India", "Tamil Nadu", "Gulf of Mannar", 9.1200, 79.1500, -18, "Tropical marine", "TER-004", "ECO-016"),
    ("LOC-016", "India", "Gujarat", "Rann of Kutch", 23.8500, 70.2000, 12, "Arid", "TER-014", "ECO-020"),
    ("LOC-017", "India", "Assam", "Kaziranga Floodplain", 26.5775, 93.1711, 70, "Tropical humid", "TER-010", "ECO-011"),
    ("LOC-018", "India", "Punjab", "Indo-Gangetic Plain", 30.9010, 75.8573, 244, "Subtropical", "TER-018", "ECO-021"),
    ("LOC-019", "India", "Maharashtra", "Mumbai Metropolitan", 19.0760, 72.8777, 14, "Tropical coastal", "TER-019", "ECO-022"),
    ("LOC-020", "India", "Andhra Pradesh", "Bay of Bengal Shelf", 15.9129, 81.6800, -850, "Deep oceanic", "TER-020", "ECO-015"),
]

# ---------------------------------------------------------------------------
# Sampling sites
# (site_id, location_id, terrain_id, ecosystem_id, name, sampling_method,
#  sample_medium, water_or_soil_type, depth_m, season)
# ---------------------------------------------------------------------------
SAMPLING_SITES = [
    ("SITE-001", "LOC-001", "TER-001", "ECO-001", "Western Ghats Stream Transect", "Water filtration", "Freshwater", "Softwater stream", 0.4, "Monsoon"),
    ("SITE-002", "LOC-001", "TER-001", "ECO-001", "Western Ghats Forest Soil Plot", "Soil core", "Soil", "Lateritic forest soil", 0.15, "Post-monsoon"),
    ("SITE-003", "LOC-002", "TER-001", "ECO-024", "Karnataka Restoration Plot", "Soil core", "Soil", "Restored lateritic soil", 0.2, "Winter"),
    ("SITE-004", "LOC-003", "TER-015", "ECO-006", "Nilgiri Montane Stream", "Water filtration", "Freshwater", "Cool montane stream", 0.3, "Post-monsoon"),
    ("SITE-005", "LOC-004", "TER-016", "ECO-007", "Sikkim Alpine Meltwater Site", "Water filtration", "Freshwater", "Glacial meltwater", 0.25, "Summer"),
    ("SITE-006", "LOC-005", "TER-015", "ECO-006", "Arunachal Montane Biofilm Site", "Biofilm swab", "Biofilm", "Rock biofilm", 0.1, "Pre-monsoon"),
    ("SITE-007", "LOC-006", "TER-003", "ECO-018", "Sundarbans Mangrove Channel", "Water filtration", "Brackish water", "Tidal channel", 1.2, "Monsoon"),
    ("SITE-008", "LOC-006", "TER-003", "ECO-018", "Sundarbans Mangrove Sediment", "Sediment grab", "Sediment", "Anoxic tidal mud", 0.3, "Winter"),
    ("SITE-009", "LOC-007", "TER-005", "ECO-014", "Andaman Reef Flat", "Water filtration", "Marine water", "Reef-flat seawater", 6.0, "Winter"),
    ("SITE-010", "LOC-008", "TER-005", "ECO-014", "Lakshadweep Lagoon Reef", "Water filtration", "Marine water", "Atoll lagoon seawater", 4.5, "Pre-monsoon"),
    ("SITE-011", "LOC-009", "TER-013", "ECO-005", "Thar Desert Soil Transect", "Soil core", "Soil", "Aeolian sand", 0.1, "Winter"),
    ("SITE-012", "LOC-010", "TER-014", "ECO-003", "Deccan Semi-Arid Grassland Plot", "Soil core", "Soil", "Black cotton soil", 0.15, "Post-monsoon"),
    ("SITE-013", "LOC-011", "TER-008", "ECO-008", "Brahmaputra Main Channel", "Water filtration", "Freshwater", "Turbid river water", 2.5, "Monsoon"),
    ("SITE-014", "LOC-012", "TER-008", "ECO-008", "Ganga Midstream Station", "Water filtration", "Freshwater", "Turbid river water", 3.0, "Post-monsoon"),
    ("SITE-015", "LOC-013", "TER-008", "ECO-008", "Godavari Reservoir Outflow", "Water filtration", "Freshwater", "Regulated river water", 1.8, "Summer"),
    ("SITE-016", "LOC-014", "TER-007", "ECO-019", "Chilika Lagoon Mouth", "Water filtration", "Brackish water", "Lagoon water", 1.5, "Winter"),
    ("SITE-017", "LOC-015", "TER-004", "ECO-016", "Gulf of Mannar Seagrass Bed", "Water filtration", "Marine water", "Coastal seawater", 5.0, "Pre-monsoon"),
    ("SITE-018", "LOC-016", "TER-014", "ECO-020", "Rann Salt Marsh Flat", "Sediment grab", "Sediment", "Hypersaline flat", 0.1, "Winter"),
    ("SITE-019", "LOC-017", "TER-010", "ECO-011", "Kaziranga Floodplain Wetland", "Water filtration", "Freshwater", "Floodplain wetland", 0.8, "Monsoon"),
    ("SITE-020", "LOC-018", "TER-018", "ECO-021", "Punjab Irrigation Canal", "Water filtration", "Freshwater", "Agricultural runoff", 0.9, "Summer"),
    ("SITE-021", "LOC-019", "TER-019", "ECO-022", "Mumbai Urban Creek", "Water filtration", "Freshwater", "Urban drainage", 1.1, "Monsoon"),
    ("SITE-022", "LOC-020", "TER-020", "ECO-015", "Bay of Bengal Deep Station", "Sediment grab", "Sediment", "Abyssal sediment", 850.0, "Winter"),
]

# ---------------------------------------------------------------------------
# Taxonomy + organisms.
#
# Scientific names are real. The synthetic layer is the *observation*: no
# claim is made that these organisms were detected at the locations above.
#
# (key, kingdom, phylum, class, order, family, genus, species, common_name,
#  habitat_type, preferred_ecosystem_id, trophic_level, functional_group,
#  native_status, environmental_sensitivity)
# ---------------------------------------------------------------------------
ORGANISM_SPECS = [
    # --- Animalia: terrestrial vertebrates ---
    ("tiger", "Animalia", "Chordata", "Mammalia", "Carnivora", "Felidae", "Panthera", "Panthera tigris", "Bengal Tiger", "Terrestrial", "ECO-001", "Apex Predator", "Carnivore", "Native", "High"),
    ("elephant", "Animalia", "Chordata", "Mammalia", "Proboscidea", "Elephantidae", "Elephas", "Elephas maximus", "Asian Elephant", "Terrestrial", "ECO-001", "Primary Consumer", "Herbivore", "Native", "High"),
    ("rhino", "Animalia", "Chordata", "Mammalia", "Perissodactyla", "Rhinocerotidae", "Rhinoceros", "Rhinoceros unicornis", "Indian Rhinoceros", "Terrestrial", "ECO-011", "Primary Consumer", "Herbivore", "Native", "High"),
    ("macaque", "Animalia", "Chordata", "Mammalia", "Primates", "Cercopithecidae", "Macaca", "Macaca silenus", "Lion-tailed Macaque", "Terrestrial", "ECO-001", "Primary Consumer", "Omnivore", "Native", "Very High"),
    ("tahr", "Animalia", "Chordata", "Mammalia", "Artiodactyla", "Bovidae", "Nilgiritragus", "Nilgiritragus hylocrius", "Nilgiri Tahr", "Terrestrial", "ECO-006", "Primary Consumer", "Herbivore", "Native", "Very High"),
    ("bustard", "Animalia", "Chordata", "Aves", "Otidiformes", "Otididae", "Ardeotis", "Ardeotis nigriceps", "Great Indian Bustard", "Terrestrial", "ECO-003", "Secondary Consumer", "Omnivore", "Native", "Very High"),
    ("fishing_cat", "Animalia", "Chordata", "Mammalia", "Carnivora", "Felidae", "Prionailurus", "Prionailurus viverrinus", "Fishing Cat", "Transitional", "ECO-018", "Secondary Consumer", "Carnivore", "Native", "High"),
    ("otter", "Animalia", "Chordata", "Mammalia", "Carnivora", "Mustelidae", "Lutrogale", "Lutrogale perspicillata", "Smooth-coated Otter", "Freshwater", "ECO-008", "Tertiary Consumer", "Predator", "Native", "High"),
    # --- Animalia: aquatic vertebrates ---
    ("dolphin", "Animalia", "Chordata", "Mammalia", "Artiodactyla", "Platanistidae", "Platanista", "Platanista gangetica", "Ganges River Dolphin", "Freshwater", "ECO-008", "Tertiary Consumer", "Predator", "Native", "Very High"),
    ("dugong", "Animalia", "Chordata", "Mammalia", "Sirenia", "Dugongidae", "Dugong", "Dugong dugon", "Dugong", "Marine", "ECO-016", "Primary Consumer", "Herbivore", "Native", "Very High"),
    ("gharial", "Animalia", "Chordata", "Reptilia", "Crocodilia", "Gavialidae", "Gavialis", "Gavialis gangeticus", "Gharial", "Freshwater", "ECO-008", "Tertiary Consumer", "Predator", "Native", "Very High"),
    ("mugger", "Animalia", "Chordata", "Reptilia", "Crocodilia", "Crocodylidae", "Crocodylus", "Crocodylus palustris", "Mugger Crocodile", "Freshwater", "ECO-009", "Tertiary Consumer", "Predator", "Native", "Moderate"),
    ("turtle", "Animalia", "Chordata", "Reptilia", "Testudines", "Cheloniidae", "Chelonia", "Chelonia mydas", "Green Sea Turtle", "Marine", "ECO-016", "Primary Consumer", "Herbivore", "Native", "High"),
    ("terrapin", "Animalia", "Chordata", "Reptilia", "Testudines", "Geoemydidae", "Batagur", "Batagur baska", "Northern River Terrapin", "Transitional", "ECO-017", "Primary Consumer", "Omnivore", "Native", "Very High"),
    ("mahseer", "Animalia", "Chordata", "Actinopterygii", "Cypriniformes", "Cyprinidae", "Tor", "Tor putitora", "Golden Mahseer", "Freshwater", "ECO-010", "Secondary Consumer", "Omnivore", "Native", "High"),
    ("hilsa", "Animalia", "Chordata", "Actinopterygii", "Clupeiformes", "Dorosomatidae", "Tenualosa", "Tenualosa ilisha", "Hilsa Shad", "Transitional", "ECO-017", "Filter Feeder", "Filter Feeder", "Native", "Moderate"),
    ("eel", "Animalia", "Chordata", "Actinopterygii", "Anguilliformes", "Anguillidae", "Anguilla", "Anguilla bengalensis", "Indian Mottled Eel", "Freshwater", "ECO-008", "Secondary Consumer", "Predator", "Native", "Moderate"),
    ("tilapia", "Animalia", "Chordata", "Actinopterygii", "Cichliformes", "Cichlidae", "Oreochromis", "Oreochromis mossambicus", "Mozambique Tilapia", "Freshwater", "ECO-012", "Primary Consumer", "Omnivore", "Introduced", "Low"),
    # --- Animalia: invertebrates ---
    ("coral", "Animalia", "Cnidaria", "Anthozoa", "Scleractinia", "Acroporidae", "Acropora", "Acropora cervicornis", "Staghorn Coral", "Marine", "ECO-014", "Filter Feeder", "Filter Feeder", "Native", "Very High"),
    ("mussel", "Animalia", "Mollusca", "Bivalvia", "Mytilida", "Mytilidae", "Perna", "Perna viridis", "Asian Green Mussel", "Marine", "ECO-016", "Filter Feeder", "Filter Feeder", "Native", "Low"),
    ("crab", "Animalia", "Arthropoda", "Malacostraca", "Decapoda", "Ocypodidae", "Uca", "Uca lactea", "Milky Fiddler Crab", "Transitional", "ECO-018", "Detritivore", "Detritivore", "Native", "Moderate"),
    ("mayfly", "Animalia", "Arthropoda", "Insecta", "Ephemeroptera", "Baetidae", "Baetis", "Baetis rhodani", "Olive Dun Mayfly", "Freshwater", "ECO-010", "Primary Consumer", "Herbivore", "Native", "Very High"),
    ("earthworm", "Animalia", "Annelida", "Clitellata", "Opisthopora", "Megascolecidae", "Perionyx", "Perionyx excavatus", "Blue Composting Worm", "Terrestrial", "ECO-021", "Detritivore", "Detritivore", "Native", "Low"),
    # --- Plantae ---
    ("rhizophora", "Plantae", "Tracheophyta", "Magnoliopsida", "Malpighiales", "Rhizophoraceae", "Rhizophora", "Rhizophora mucronata", "Loop-root Mangrove", "Transitional", "ECO-018", "Producer", "Producer", "Native", "High"),
    ("avicennia", "Plantae", "Tracheophyta", "Magnoliopsida", "Lamiales", "Acanthaceae", "Avicennia", "Avicennia marina", "Grey Mangrove", "Transitional", "ECO-018", "Producer", "Producer", "Native", "Moderate"),
    ("shorea", "Plantae", "Tracheophyta", "Magnoliopsida", "Malvales", "Dipterocarpaceae", "Shorea", "Shorea robusta", "Sal Tree", "Terrestrial", "ECO-002", "Producer", "Producer", "Native", "Moderate"),
    ("teak", "Plantae", "Tracheophyta", "Magnoliopsida", "Lamiales", "Lamiaceae", "Tectona", "Tectona grandis", "Teak", "Terrestrial", "ECO-002", "Producer", "Producer", "Native", "Low"),
    ("nepenthes", "Plantae", "Tracheophyta", "Magnoliopsida", "Caryophyllales", "Nepenthaceae", "Nepenthes", "Nepenthes khasiana", "Indian Pitcher Plant", "Terrestrial", "ECO-006", "Producer", "Producer", "Native", "Very High"),
    ("prosopis", "Plantae", "Tracheophyta", "Magnoliopsida", "Fabales", "Fabaceae", "Prosopis", "Prosopis cineraria", "Khejri", "Terrestrial", "ECO-005", "Producer", "Producer", "Native", "Moderate"),
    ("rhododendron", "Plantae", "Tracheophyta", "Magnoliopsida", "Ericales", "Ericaceae", "Rhododendron", "Rhododendron arboreum", "Tree Rhododendron", "Terrestrial", "ECO-007", "Producer", "Producer", "Native", "High"),
    ("seagrass", "Plantae", "Tracheophyta", "Liliopsida", "Alismatales", "Hydrocharitaceae", "Halophila", "Halophila ovalis", "Spoon Seagrass", "Marine", "ECO-016", "Producer", "Producer", "Native", "High"),
    ("vallisneria", "Plantae", "Tracheophyta", "Liliopsida", "Alismatales", "Hydrocharitaceae", "Vallisneria", "Vallisneria spiralis", "Tape Grass", "Freshwater", "ECO-009", "Producer", "Producer", "Native", "Moderate"),
    ("waterhyacinth", "Plantae", "Tracheophyta", "Liliopsida", "Commelinales", "Pontederiaceae", "Pontederia", "Pontederia crassipes", "Water Hyacinth", "Freshwater", "ECO-011", "Producer", "Producer", "Introduced", "Low"),
    # --- Fungi ---
    ("termitomyces", "Fungi", "Basidiomycota", "Agaricomycetes", "Agaricales", "Lyophyllaceae", "Termitomyces", "Termitomyces heimii", "Termite Mushroom", "Terrestrial", "ECO-004", "Decomposer", "Decomposer", "Native", "Moderate"),
    ("ganoderma", "Fungi", "Basidiomycota", "Agaricomycetes", "Polyporales", "Ganodermataceae", "Ganoderma", "Ganoderma lucidum", "Reishi", "Terrestrial", "ECO-002", "Decomposer", "Decomposer", "Native", "Low"),
    ("trichoderma", "Fungi", "Ascomycota", "Sordariomycetes", "Hypocreales", "Hypocreaceae", "Trichoderma", "Trichoderma harzianum", "Soil Trichoderma", "Terrestrial", "ECO-021", "Decomposer", "Decomposer", "Native", "Low"),
    ("aspergillus", "Fungi", "Ascomycota", "Eurotiomycetes", "Eurotiales", "Aspergillaceae", "Aspergillus", "Aspergillus niger", "Black Mould", "Terrestrial", "ECO-021", "Decomposer", "Decomposer", "Native", "Low"),
    # --- Bacteria ---
    ("nitrosomonas", "Bacteria", "Pseudomonadota", "Betaproteobacteria", "Nitrosomonadales", "Nitrosomonadaceae", "Nitrosomonas", "Nitrosomonas europaea", "Ammonia-oxidising Bacterium", "Freshwater", "ECO-008", "Microbial Decomposer", "Microbial Decomposer", "Native", "Moderate"),
    ("synechococcus", "Bacteria", "Cyanobacteriota", "Cyanophyceae", "Synechococcales", "Synechococcaceae", "Synechococcus", "Synechococcus elongatus", "Marine Picocyanobacterium", "Marine", "ECO-013", "Producer", "Producer", "Native", "Moderate"),
    ("vibrio", "Bacteria", "Pseudomonadota", "Gammaproteobacteria", "Vibrionales", "Vibrionaceae", "Vibrio", "Vibrio harveyi", "Luminous Vibrio", "Marine", "ECO-016", "Microbial Decomposer", "Microbial Decomposer", "Native", "Low"),
    ("bacillus", "Bacteria", "Bacillota", "Bacilli", "Bacillales", "Bacillaceae", "Bacillus", "Bacillus subtilis", "Hay Bacillus", "Terrestrial", "ECO-021", "Microbial Decomposer", "Microbial Decomposer", "Native", "Low"),
    ("pseudomonas", "Bacteria", "Pseudomonadota", "Gammaproteobacteria", "Pseudomonadales", "Pseudomonadaceae", "Pseudomonas", "Pseudomonas putida", "Soil Pseudomonad", "Terrestrial", "ECO-022", "Microbial Decomposer", "Microbial Decomposer", "Native", "Low"),
    # --- Archaea ---
    ("halobacterium", "Archaea", "Euryarchaeota", "Halobacteria", "Halobacteriales", "Halobacteriaceae", "Halobacterium", "Halobacterium salinarum", "Halophilic Archaeon", "Extreme", "ECO-020", "Microbial Decomposer", "Microbial Decomposer", "Native", "Moderate"),
    ("methanobrevibacter", "Archaea", "Euryarchaeota", "Methanobacteria", "Methanobacteriales", "Methanobacteriaceae", "Methanobrevibacter", "Methanobrevibacter smithii", "Methanogenic Archaeon", "Freshwater", "ECO-011", "Microbial Decomposer", "Microbial Decomposer", "Native", "Moderate"),
    ("nitrososphaera", "Archaea", "Thermoproteota", "Nitrososphaeria", "Nitrososphaerales", "Nitrososphaeraceae", "Nitrososphaera", "Nitrososphaera viennensis", "Soil Ammonia-oxidising Archaeon", "Terrestrial", "ECO-021", "Microbial Decomposer", "Microbial Decomposer", "Native", "Moderate"),
    # --- Protista ---
    ("noctiluca", "Protista", "Myzozoa", "Dinophyceae", "Noctilucales", "Noctilucaceae", "Noctiluca", "Noctiluca scintillans", "Sea Sparkle", "Marine", "ECO-013", "Secondary Consumer", "Predator", "Native", "Low"),
    ("navicula", "Protista", "Bacillariophyta", "Bacillariophyceae", "Naviculales", "Naviculaceae", "Navicula", "Navicula cryptocephala", "Boat Diatom", "Freshwater", "ECO-010", "Producer", "Producer", "Native", "High"),
    ("paramecium", "Protista", "Ciliophora", "Oligohymenophorea", "Peniculida", "Parameciidae", "Paramecium", "Paramecium caudatum", "Slipper Ciliate", "Freshwater", "ECO-009", "Primary Consumer", "Filter Feeder", "Native", "Moderate"),
    ("ceratium", "Protista", "Myzozoa", "Dinophyceae", "Gonyaulacales", "Ceratiaceae", "Tripos", "Tripos furca", "Horned Dinoflagellate", "Marine", "ECO-013", "Producer", "Producer", "Native", "Moderate"),
]

# Additional species-level taxonomy records that are NOT yet linked to an
# organism record. These represent taxa present in the reference taxonomy
# but not (yet) characterised by Gaia — useful for demonstrating the
# distinction between "known taxonomy" and "assessed organism".
UNLINKED_TAXA = [
    ("Animalia", "Chordata", "Actinopterygii", "Siluriformes", "Bagridae", "Mystus", "Mystus cavasius", "Gangetic Mystus"),
    ("Animalia", "Chordata", "Amphibia", "Anura", "Rhacophoridae", "Rhacophorus", "Rhacophorus malabaricus", "Malabar Gliding Frog"),
    ("Animalia", "Chordata", "Aves", "Pelecaniformes", "Ardeidae", "Ardea", "Ardea cinerea", "Grey Heron"),
    ("Animalia", "Arthropoda", "Insecta", "Odonata", "Libellulidae", "Orthetrum", "Orthetrum sabina", "Slender Skimmer"),
    ("Animalia", "Mollusca", "Gastropoda", "Architaenioglossa", "Ampullariidae", "Pila", "Pila globosa", "Apple Snail"),
    ("Animalia", "Echinodermata", "Echinoidea", "Camarodonta", "Toxopneustidae", "Tripneustes", "Tripneustes gratilla", "Collector Urchin"),
    ("Plantae", "Tracheophyta", "Magnoliopsida", "Myrtales", "Lythraceae", "Sonneratia", "Sonneratia alba", "Mangrove Apple"),
    ("Plantae", "Tracheophyta", "Polypodiopsida", "Polypodiales", "Pteridaceae", "Adiantum", "Adiantum caudatum", "Trailing Maidenhair"),
    ("Plantae", "Bryophyta", "Bryopsida", "Hypnales", "Brachytheciaceae", "Brachythecium", "Brachythecium rutabulum", "Rough-stalked Feather Moss"),
    ("Fungi", "Basidiomycota", "Agaricomycetes", "Russulales", "Russulaceae", "Russula", "Russula emetica", "The Sickener"),
    ("Fungi", "Ascomycota", "Leotiomycetes", "Helotiales", "Sclerotiniaceae", "Botrytis", "Botrytis cinerea", "Grey Mould"),
    ("Bacteria", "Actinomycetota", "Actinomycetes", "Streptomycetales", "Streptomycetaceae", "Streptomyces", "Streptomyces coelicolor", "Soil Streptomycete"),
    ("Bacteria", "Bacteroidota", "Flavobacteriia", "Flavobacteriales", "Flavobacteriaceae", "Flavobacterium", "Flavobacterium johnsoniae", "Gliding Flavobacterium"),
    ("Bacteria", "Cyanobacteriota", "Cyanophyceae", "Nostocales", "Nostocaceae", "Anabaena", "Anabaena variabilis", "Nitrogen-fixing Cyanobacterium"),
    ("Archaea", "Euryarchaeota", "Methanomicrobia", "Methanosarcinales", "Methanosarcinaceae", "Methanosarcina", "Methanosarcina barkeri", "Acetoclastic Methanogen"),
    ("Archaea", "Thermoproteota", "Thermoprotei", "Sulfolobales", "Sulfolobaceae", "Sulfolobus", "Sulfolobus acidocaldarius", "Thermoacidophilic Archaeon"),
    ("Protista", "Bacillariophyta", "Coscinodiscophyceae", "Chaetocerotales", "Chaetocerotaceae", "Chaetoceros", "Chaetoceros curvisetus", "Chain Diatom"),
    ("Protista", "Amoebozoa", "Tubulinea", "Euamoebida", "Amoebidae", "Amoeba", "Amoeba proteus", "Common Amoeba"),
    ("Protista", "Euglenozoa", "Euglenoidea", "Euglenales", "Euglenaceae", "Euglena", "Euglena gracilis", "Green Euglena"),
    ("Protista", "Foraminifera", "Globothalamea", "Rotaliida", "Ammoniidae", "Ammonia", "Ammonia beccarii", "Benthic Foraminiferan"),
]

# ---------------------------------------------------------------------------
# Threat catalogue  (name -> category)
# ---------------------------------------------------------------------------
THREAT_CATALOGUE = {
    "Habitat Loss": "Habitat Degradation",
    "Deforestation": "Habitat Degradation",
    "Urban Expansion": "Land Use Change",
    "Agricultural Expansion": "Land Use Change",
    "Pollution": "Pollution",
    "Climate Change": "Climate",
    "Overfishing": "Resource Exploitation",
    "Hunting": "Resource Exploitation",
    "Illegal Collection": "Resource Exploitation",
    "Invasive Species": "Biological Invasion",
    "Disease": "Biological",
    "Mining": "Extractive Industry",
    "Infrastructure Development": "Land Use Change",
    "Water Extraction": "Hydrological Alteration",
    "Ocean Acidification": "Climate",
    "Extreme Weather": "Climate",
    "Fire": "Disturbance",
    "Human Disturbance": "Disturbance",
    "Unknown": "Unknown",
}

# ---------------------------------------------------------------------------
# Scenario assignment.
#
# Section 37 of the specification requires the dataset to contain concrete
# examples of 16 named situations. Rather than hoping random generation
# produces them, each scenario is pinned to specific organisms so the
# prototype can always demonstrate it.
# ---------------------------------------------------------------------------
SCENARIOS = {
    "S01_healthy_stable": ["tilapia", "bacillus", "teak", "earthworm"],
    "S02_declining": ["elephant", "mahseer", "shorea", "hilsa"],
    "S03_rapidly_declining": ["bustard", "gharial", "coral"],
    "S04_small_population": ["bustard", "tahr", "terrapin"],
    "S05_restricted_range": ["macaque", "nepenthes", "tahr"],
    "S06_high_habitat_loss": ["rhino", "dolphin", "rhizophora", "bustard", "gharial"],
    "S07_severe_fragmentation": ["tiger", "macaque", "fishing_cat", "gharial", "dolphin"],
    "S08_multiple_threats": ["tiger", "dolphin", "coral", "dugong", "bustard", "gharial"],
    "S09_high_detection_low_population_data": ["vibrio", "navicula", "synechococcus"],
    "S10_low_detection_confidence": ["nitrososphaera", "ceratium", "aspergillus"],
    "S11_data_deficient": ["methanobrevibacter", "halobacterium", "eel"],
    "S12_very_high_extinction_risk": ["bustard", "gharial", "dolphin"],
    "S13_low_biodiversity": ["SITE-011", "SITE-018", "SITE-020"],
    "S14_high_biodiversity": ["SITE-001", "SITE-007", "SITE-009"],
    "S15_high_microbial_diversity": ["SITE-008", "SITE-022", "SITE-021"],
    "S16_potential_invasive": ["tilapia", "waterhyacinth", "mussel"],
}

MARKER_REGIONS = ["COI", "16S", "18S", "ITS", "12S", "rbcL"]

# Which marker regions are plausible for which kingdom. Used so that a
# generated sequence's marker is at least internally consistent with the
# organism the mock identification assigns to it.
KINGDOM_MARKERS = {
    "Animalia": ["COI", "12S", "16S"],
    "Plantae": ["rbcL", "ITS", "18S"],
    "Fungi": ["ITS", "18S"],
    "Bacteria": ["16S"],
    "Archaea": ["16S"],
    "Protista": ["18S", "COI"],
}

SEASONS = ["Monsoon", "Post-monsoon", "Winter", "Summer", "Pre-monsoon"]

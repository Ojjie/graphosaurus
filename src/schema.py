# src/schema.py

GRAPH_SCHEMA = """
Node Labels:
- Dinosaur (properties: name, diet, length_m, class, start_ma, end_ma, source)
- Period (properties: name)
- Clade (properties: name)
- Continent (properties: name)

Relationships:
- (:Dinosaur)-[:LIVED_IN]->(:Period)
- (:Dinosaur)-[:BELONGS_TO]->(:Clade)
- (:Dinosaur)-[:FOUND_IN]->(:Continent)

Example:
MATCH (p:Period)-[:LIVED_IN]-(d:Dinosaur)-[:FOUND_IN]-(c:Continent)
WHERE p.name CONTAINS 'Jurassic'
WITH c, collect(DISTINCT d.diet) AS diets
WHERE 'Carnivore' IN diets AND 'Herbivore' IN diets
RETURN c.name AS Continent

Rules:
- Use toFloat(d.length_m) for numerical comparisons.
- Always return the 'source' property if the user asks for evidence.
"""

FEW_SHOT_EXAMPLES = """

Use the following examples to guide your Cypher generation:

Question: "Which dinosaurs lived in the Jurassic?"
Cypher: MATCH (d:Dinosaur)-[:LIVED_IN]->(p:Period) WHERE toLower(p.name) CONTAINS 'jurassic' RETURN d.name, d.source

Question: "List carnivorous dinosaurs from North America"
Cypher: MATCH (d:Dinosaur)-[:FOUND_IN]-(c:Continent) WHERE d.diet = 'Carnivore' AND toLower(c.name) CONTAINS 'north america' RETURN d.name, d.diet, c.name

Question: "Which clade contains the largest species?"
Cypher: MATCH (d:Dinosaur)-[:BELONGS_TO]->(c:Clade) WITH d, c, toFloat(d.length_m) AS Size RETURN c.name, d.name, Size ORDER BY Size DESC LIMIT 1

Question: "Which herbivorous dinosaurs lived in the Late Cretaceous in Asia?"
Cypher: MATCH (c:Continent)-[:FOUND_IN]-(d:Dinosaur)-[:LIVED_IN]-(p:Period) WHERE toLower(c.name) CONTAINS 'asia' AND d.diet = 'Herbivore' AND toLower(p.name) CONTAINS 'late cretaceous' RETURN d.name, p.name, c.name

Question: "Which continents had both carnivores and herbivores during the Jurassic?"
Cypher: MATCH (p:Period)-[:LIVED_IN]-(d:Dinosaur)-[:FOUND_IN]-(c:Continent) WHERE toLower(p.name) CONTAINS 'jurassic' WITH c, collect(DISTINCT d.diet) AS diets WHERE 'Carnivore' IN diets AND 'Herbivore' IN diets RETURN c.name

Question: "Which clades span multiple geological periods?"
Cypher: MATCH (p:Period)-[:LIVED_IN]-(d:Dinosaur)-[:BELONGS_TO]-(c:Clade) WITH c.name AS Clade, collect(DISTINCT p.name) AS Periods WHERE size(Periods) > 1 RETURN Clade, Periods, size(Periods) AS NumberOfPeriods

Question: "What period had the highest species diversity?"
Cypher: MATCH (d:Dinosaur)-[:LIVED_IN]->(p:Period) WITH p.name AS PeriodName, count(d) AS SpeciesCount RETURN PeriodName, SpeciesCount ORDER BY SpeciesCount DESC LIMIT 1

Question: "What is the average body length per clade?"
Cypher: MATCH (d:Dinosaur)-[:BELONGS_TO]->(c:Clade) WHERE toFloat(d.length_m) > 0 WITH c.name AS Clade, avg(toFloat(d.length_m)) AS AverageLength RETURN Clade, AverageLength ORDER BY AverageLength DESC

Question: "Which dinosaurs lived in the Ice Age?"
Cypher: MATCH (d:Dinosaur) WHERE toFloat(d.end_ma) <= 2.6 RETURN d.name, d.end_ma, d.source

Question: "Which dinosaurs were mammals?"
Cypher: MATCH (d:Dinosaur) WHERE d.class CONTAINS 'Mammal' OR d.class CONTAINS 'Synapsid' RETURN d.name, d.class, d.source

"""
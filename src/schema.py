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
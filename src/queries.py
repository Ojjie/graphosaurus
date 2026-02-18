"""
queries.py: A collection of Cypher queries for the graphosaurus Knowledge Graph.
This file contains both Table-based analytical queries and Graph-based visualization queries.
"""

# --- BASIC QUERIES ---

# 1. Which dinosaurs lived in the Jurassic?
QUERY_1_TABLE = """
MATCH (d:Dinosaur)-[:LIVED_IN]->(p:Period {name: 'Jurassic'}) 
RETURN d.name, d.source
"""
QUERY_1_GRAPH = """
MATCH (d:Dinosaur)-[r:LIVED_IN]-(p:Period)
WHERE p.name = 'Jurassic'
RETURN d, r, p
"""

# 2. List carnivorous dinosaurs from North America
QUERY_2_TABLE = """
MATCH (d:Dinosaur)-[:FOUND_IN]-(c:Continent)
WHERE d.diet = 'Carnivore' 
  AND c.name CONTAINS 'North America'
RETURN d.name AS Dinosaur, d.diet AS Diet, c.name AS Continent
"""
QUERY_2_GRAPH = """
MATCH (d:Dinosaur)-[r:FOUND_IN]-(c:Continent)
WHERE d.diet = 'Carnivore' 
  AND c.name CONTAINS 'North America'
RETURN d, r, c
"""

# 3. Which clade contains the largest species?
QUERY_3_TABLE = """
MATCH (d:Dinosaur)-[:BELONGS_TO]->(c:Clade)
WITH d, c, toFloat(d.length_m) AS Size
RETURN c.name AS Clade, d.name AS Species, Size AS Length_Meters
ORDER BY Size DESC
LIMIT 1
"""
QUERY_3_GRAPH = """
MATCH (d:Dinosaur)-[r:BELONGS_TO]->(c:Clade)
WHERE toFloat(d.length_m) > 0
RETURN d, r, c
ORDER BY toFloat(d.length_m) DESC
LIMIT 1
"""

# --- MULTI-HOP QUERIES ---

# 4. Which herbivorous dinosaurs lived in the Late Cretaceous in Asia?
QUERY_4_TABLE = """
MATCH (c:Continent)-[:FOUND_IN]-(d:Dinosaur)-[:LIVED_IN]-(p:Period)
WHERE c.name CONTAINS 'Asia' 
  AND d.diet = 'Herbivore' 
  AND p.name CONTAINS 'Late Cretaceous'
RETURN d.name AS Dinosaur, p.name AS Period, c.name AS Continent
"""
QUERY_4_GRAPH = """
MATCH (c:Continent)-[r1]-(d:Dinosaur)-[r2]-(p:Period)
WHERE c.name CONTAINS 'Asia' 
  AND d.diet = 'Herbivore' 
  AND p.name CONTAINS 'Late Cretaceous'
RETURN c, r1, d, r2, p
"""

# 5. Which continents had both carnivores and herbivores during the Jurassic?
QUERY_5_TABLE = """
MATCH (p:Period)-[:LIVED_IN]-(d:Dinosaur)-[:FOUND_IN]-(c:Continent)
WHERE p.name CONTAINS 'Jurassic'
WITH c.name AS Continent, collect(DISTINCT d.diet) AS diets
WHERE 'Carnivore' IN diets AND 'Herbivore' IN diets
RETURN Continent
"""
QUERY_5_GRAPH = """
MATCH (p:Period)-[:LIVED_IN]-(d:Dinosaur)-[:FOUND_IN]-(c:Continent)
WHERE p.name = 'Jurassic'
WITH c, collect(DISTINCT d.diet) AS diets, collect(d) AS dinos, collect(p) AS periods
WHERE 'Carnivore' IN diets AND 'Herbivore' IN diets
RETURN c, dinos, periods
"""

# 6. Which clades span multiple geological periods?
QUERY_6_TABLE = """
MATCH (p:Period)-[:LIVED_IN]-(d:Dinosaur)-[:BELONGS_TO]-(c:Clade)
WITH c.name AS Clade, collect(DISTINCT p.name) AS Periods
WHERE size(Periods) > 1
RETURN Clade, Periods, size(Periods) AS NumberOfPeriods
ORDER BY NumberOfPeriods DESC
"""
QUERY_6_GRAPH = """
MATCH (p:Period)-[:LIVED_IN]-(d:Dinosaur)-[:BELONGS_TO]-(c:Clade)
WITH c, collect(DISTINCT p) AS periods, collect(d) AS dinos
WHERE size(periods) > 1
RETURN c, periods, dinos
"""

# --- ANALYTICAL QUERIES ---

# 7. What period had the highest species diversity?
QUERY_7_TABLE = """
MATCH (d:Dinosaur)-[:LIVED_IN]->(p:Period)
WITH p.name AS PeriodName, count(d) AS SpeciesCount
RETURN PeriodName, SpeciesCount
ORDER BY SpeciesCount DESC
LIMIT 1
"""
QUERY_7_GRAPH = """
MATCH (d:Dinosaur)-[r:LIVED_IN]->(p:Period)
WITH p, count(d) AS SpeciesCount
ORDER BY SpeciesCount DESC
LIMIT 1
MATCH (p)<-[r:LIVED_IN]-(d:Dinosaur)
RETURN p, r, d
"""

# 8. What is the average body length per clade?
QUERY_8_TABLE = """
MATCH (d:Dinosaur)-[:BELONGS_TO]->(c:Clade)
WHERE toFloat(d.length_m) > 0
WITH c.name AS Clade, avg(toFloat(d.length_m)) AS AverageLength
RETURN Clade, AverageLength
ORDER BY AverageLength DESC
"""

# --- "NOT FOUND" / SAFETY CHECK QUERIES ---

# 9. Which dinosaurs lived in the Ice Age? (Expected Result: Empty or modern Avian Dinosaurs)
QUERY_9_SAFETY = """
MATCH (d:Dinosaur)
WHERE toFloat(d.end_ma) <= 2.6
RETURN d.name, d.end_ma, d.source
"""

# 10. Which dinosaurs were mammals? (Expected Result: Empty)
QUERY_10_SAFETY = """
MATCH (d:Dinosaur)
WHERE d.class CONTAINS 'Mammal' OR d.class CONTAINS 'Synapsid'
RETURN d.name, d.class, d.source
"""
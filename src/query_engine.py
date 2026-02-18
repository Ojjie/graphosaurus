# src/query_engine.py
import json
from groq import Groq
from falkordb import FalkorDB
from src.schema import GRAPH_SCHEMA

class DinoGraphRAG:
    def __init__(self, groq_key):
        self.client = Groq(api_key=groq_key)
        self.db = FalkorDB(host='localhost', port=6379)
        self.graph = self.db.select_graph('graphosaurus')

    def generate_cypher(self, user_question):
        prompt = f"""
        You are a FalkorDB Cypher expert. Convert this question into a Cypher query.
        Schema: {GRAPH_SCHEMA}

        #Few shot example 
        EXAMPLE OF SET LOGIC:
        Question: "Which continents had both carnivores and herbivores during the Jurassic?"
        Cypher: 
        MATCH (p:Period)-[:LIVED_IN]-(d:Dinosaur)-[:FOUND_IN]-(c:Continent)
        WHERE p.name CONTAINS 'Jurassic'
        WITH c.name AS Continent, collect(DISTINCT d.diet) AS diets
        WHERE 'Carnivore' IN diets AND 'Herbivore' IN diets
        RETURN Continent
        
        Question: {user_question}
        Only output the Cypher query. No preamble.
        """
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip().replace("```cypher", "").replace("```", "")

    def ask(self, question):
        # 1. Text -> Cypher
        cypher = self.generate_cypher(question)
        print(f"DEBUG: Generated Cypher: {cypher}")

        # 2. Execute on FalkorDB
        try:
            result = self.graph.query(cypher).result_set
        except Exception as e:
            return f"Error executing query: {e}"

        # 3. Cypher Result -> Natural Language
        synthesis_prompt = f"""
        Based on these database results: {result}
        Answer the user's question: {question}
        Include mentions of sources/Wikipedia links if present in the data.
        """
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": synthesis_prompt}]
        )
        return response.choices[0].message.content
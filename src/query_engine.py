# src/query_engine.py
import json
from groq import Groq
from falkordb import FalkorDB
from schema import GRAPH_SCHEMA, FEW_SHOT_EXAMPLES
import os 
from dotenv import load_dotenv

# Initialize Clients
load_dotenv() # This loads the variables from .env
api_key = os.getenv("GROQ_API_KEY")

class DinoGraphRAG:
    def __init__(self, groq_key):
        self.client = Groq(api_key=api_key)
        self.db = FalkorDB(host='localhost', port=6379)
        self.graph = self.db.select_graph('graphosaurus')

    def generate_cypher(self, user_question):
        prompt = f"""
        You are a FalkorDB Cypher expert. Convert this question into a Cypher query.
        Schema: {GRAPH_SCHEMA}

        REFERENCE EXAMPLES:{FEW_SHOT_EXAMPLES}

        INSTRUCTIONS:
        - If the user question matches a reference example, use that logic.
        - Always use 'toLower()' and 'CONTAINS' for names.
        - Always use 'toFloat()' for 'length_m', 'start_ma', and 'end_ma'
        
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
        Include mentions of sources/Wikipedia links if present in the data..
        """
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": synthesis_prompt}]
        )
        return response.choices[0].message.content
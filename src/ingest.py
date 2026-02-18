import json
import time
import wikipediaapi  
from groq import Groq
from falkordb import FalkorDB

# Initialize Clients
client = Groq(api_key="YOUR_GROQ_API_KEY")
db = FalkorDB(host='localhost', port=6379)
graph = db.select_graph('graphosaurus')

# Initialize Wikipedia API with a User-Agent
wiki = wikipediaapi.Wikipedia(user_agent="DinoGroundingBot/1.0", language='en')

# Pre-create indexes
graph.query("CREATE INDEX ON :Dinosaur(name)")
graph.query("CREATE INDEX ON :Period(name)")
graph.query("CREATE INDEX ON :Clade(name)")
graph.query("CREATE INDEX ON :Continent(name)")

def verify_dino(dino_data):
    """Checks if the dinosaur exists on Wikipedia and gets the real URL."""
    name = dino_data.get('name')
    page = wiki.page(name)
    
    if page.exists():
        # Override the LLM's URL with the verified one
        dino_data['wikipedia_url'] = page.fullurl
        return dino_data
    else:
        print(f"Skipping {name}: Not found on Wikipedia.")
        return None

def fetch_and_ingest_dinos(total_needed=200, batch_size=50):
    count = 0
    while count < total_needed:
        print(f"Fetching dinosaurs {count} to {count + batch_size}...")
        
        try:
            prompt = (
                f"Generate a JSON list of {batch_size} unique dinosaurs (starting from index {count}). "
                "Provide ONLY species that have well-documented Wikipedia pages. "
                "Fields: 'name', 'diet', 'period', 'clade', 'length_m', 'continent', 'class', "
                "'start_ma', 'end_ma', and 'wikipedia_url'."
            )

            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a paleontology data curator. Every species must exist on Wikipedia. Output ONLY valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            data = json.loads(completion.choices[0].message.content)
            dinos = data.get('dinosaurs', [])

            # 1. VERIFICATION STEP
            # We filter the LLM's output against the real Wikipedia API
            batch_params = []
            for d in dinos:
                verified_d = verify_dino(d)
                if verified_d:
                    batch_params.append({
                        'name': verified_d['name'],
                        'diet': verified_d['diet'],
                        'length': float(verified_d.get('length_m', 0)),
                        'class': verified_d.get('class', 'Reptilia'),
                        'start': float(verified_d.get('start_ma', 0)),
                        'end': float(verified_d.get('end_ma', 0)),
                        'period': verified_d['period'],
                        'clade': verified_d['clade'],
                        'continent': verified_d['continent'],
                        'source': verified_d['wikipedia_url']
                    })

            # 2. OPTIMIZED BATCH INGESTION
            if batch_params:
                query = """
                UNWIND $batch AS d
                MERGE (dino:Dinosaur {name: d.name})
                SET dino.diet = d.diet, 
                    dino.length_m = d.length,
                    dino.class = d.class,
                    dino.start_ma = d.start,
                    dino.end_ma = d.end,
                    dino.source = d.source
                
                MERGE (p:Period {name: d.period})
                MERGE (c:Clade {name: d.clade})
                MERGE (con:Continent {name: d.continent})
                
                MERGE (dino)-[:LIVED_IN]->(p)
                MERGE (dino)-[:BELONGS_TO]->(c)
                MERGE (dino)-[:FOUND_IN]->(con)
                """
                graph.query(query, {'batch': batch_params})
                count += len(batch_params)
            
            time.sleep(1) 
            
        except Exception as e:
            print(f"Error during batch: {e}")
            break

    print(f"Finished! Total grounded dinosaurs in graph: {count}")

fetch_and_ingest_dinos(200, 50)
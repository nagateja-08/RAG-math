"""
Cypher Queries for Neo4j Mathematical Knowledge Graph
"""

# Constraints & Indexes
CREATE_CONSTRAINTS = [
    "CREATE CONSTRAINT concept_name_unique IF NOT EXISTS FOR (c:Concept) REQUIRE c.name IS UNIQUE",
    "CREATE CONSTRAINT formula_name_unique IF NOT EXISTS FOR (f:Formula) REQUIRE f.name IS UNIQUE",
    "CREATE CONSTRAINT theorem_name_unique IF NOT EXISTS FOR (t:Theorem) REQUIRE t.name IS UNIQUE",
    "CREATE CONSTRAINT topic_name_unique IF NOT EXISTS FOR (top:Topic) REQUIRE top.name IS UNIQUE",
    "CREATE CONSTRAINT node_id_unique IF NOT EXISTS FOR (n:Node) REQUIRE n.id IS UNIQUE"
]

# Concept Identification & Lookup
FIND_CONCEPT_BY_NAME = """
MATCH (c)
WHERE (c:Concept OR c:Topic OR c:Theorem) AND (toLower(c.name) = toLower($name) OR toLower(c.id) = toLower($name))
RETURN c.id AS id, c.name AS name, labels(c)[0] AS type, c.subject AS subject,
       c.difficulty AS difficulty, c.description AS description, c.latex AS latex
LIMIT 1
"""

# Fuzzy Search Concepts
SEARCH_CONCEPTS = """
MATCH (c)
WHERE (c:Concept OR c:Topic OR c:Theorem OR c:Formula)
  AND (toLower(c.name) CONTAINS toLower($query) OR toLower(coalesce(c.description, '')) CONTAINS toLower($query))
RETURN c.id AS id, c.name AS name, labels(c)[0] AS type, c.subject AS subject,
       c.difficulty AS difficulty, c.description AS description, c.latex AS latex
LIMIT 15
"""

# Concept Neighborhood: Prerequisites, Formulas, Theorems, Related
GET_CONCEPT_NEIGHBORHOOD = """
MATCH (c {name: $concept_name})
OPTIONAL MATCH (p)-[:PREREQUISITE_OF]->(c)
OPTIONAL MATCH (c)-[:PREREQUISITE_OF]->(d)
OPTIONAL MATCH (c)-[:USES_FORMULA]->(f:Formula)
OPTIONAL MATCH (t:Theorem)-[:EXPLAINS|PROVES]->(c)
OPTIONAL MATCH (c)-[:RELATED_TO]-(r)
RETURN c.name AS concept,
       c.subject AS subject,
       c.difficulty AS difficulty,
       c.description AS description,
       collect(DISTINCT p.name) AS prerequisites,
       collect(DISTINCT d.name) AS enables_topics,
       collect(DISTINCT {name: f.name, latex: f.latex, description: f.description}) AS formulas,
       collect(DISTINCT {name: t.name, statement: t.description}) AS theorems,
       collect(DISTINCT r.name) AS related_concepts
"""

# Prerequisite Traversal (Transitive Closure)
GET_PREREQUISITE_CHAIN = """
MATCH path = (p)-[:PREREQUISITE_OF*1..4]->(target {name: $concept_name})
RETURN [n in nodes(path) | {id: n.id, name: n.name, subject: n.subject, difficulty: n.difficulty}] AS path_nodes,
       length(path) AS depth
ORDER BY depth ASC
"""

# Get Subgraph (for React Flow / Graph Explorer)
GET_ENTIRE_GRAPH = """
MATCH (n)
OPTIONAL MATCH (n)-[r]->(m)
RETURN n.id AS source_id, n.name AS source_name, labels(n)[0] AS source_type,
       n.subject AS source_subject, n.difficulty AS source_difficulty,
       n.description AS source_description, n.latex AS source_latex,
       type(r) AS rel_type,
       m.id AS target_id, m.name AS target_name, labels(m)[0] AS target_type
LIMIT 500
"""

# Dynamic Node Insertion (Ensuring Zero Duplicates)
MERGE_CONCEPT_NODE = """
MERGE (c:Concept {name: $name})
ON CREATE SET c.id = $id,
              c.type = 'Concept',
              c.subject = $subject,
              c.difficulty = $difficulty,
              c.description = $description,
              c.source = $source,
              c.created_at = datetime()
ON MATCH SET c.description = coalesce(c.description, $description),
             c.source = coalesce(c.source, $source)
RETURN c
"""

MERGE_RELATIONSHIP = """
MATCH (a {name: $source_name})
MATCH (b {name: $target_name})
MERGE (a)-[r:RELATED_TO]->(b)
RETURN r
"""

MERGE_PREREQUISITE_RELATIONSHIP = """
MATCH (prereq {name: $prereq_name})
MATCH (target {name: $target_name})
MERGE (prereq)-[r:PREREQUISITE_OF]->(target)
RETURN r
"""

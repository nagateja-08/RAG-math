import logging
import re
from typing import List, Dict, Any, Optional
from .neo4j_client import get_neo4j_client
from ...models.schemas import GraphNode, GraphEdge, GraphDataResponse, ConceptDetailResponse

logger = logging.getLogger("mathgpt.graph_service")

class GraphService:
    def __init__(self):
        self.client = get_neo4j_client()

    def get_status(self) -> Dict[str, Any]:
        return {
            "is_live": self.client.is_live,
            "mode": "live_neo4j" if self.client.is_live else "in_memory_resilient_store",
            "total_nodes": len(self.client._in_memory_graph.nodes)
        }

    def find_concept(self, query: str) -> Optional[Dict[str, Any]]:
        """Find a concept node by exact or fuzzy name match."""
        q_norm = query.strip().lower()

        # If live Neo4j
        if self.client.is_live and self.client.driver:
            try:
                with self.client.driver.session(database=self.client.settings.neo4j_database) as session:
                    res = session.run("""
                        MATCH (c)
                        WHERE (c:Concept OR c:Topic OR c:Theorem)
                          AND (toLower(c.name) = toLower($q) OR toLower(c.name) CONTAINS toLower($q))
                        RETURN c.id AS id, c.name AS name, labels(c)[0] AS type,
                               c.subject AS subject, c.difficulty AS difficulty,
                               c.description AS description, c.latex AS latex
                        LIMIT 1
                    """, q=q_norm).single()
                    if res:
                        return dict(res)
            except Exception as e:
                logger.error(f"Live Neo4j lookup failed ({e}), falling back to memory.")

        # In-memory graph search
        g = self.client._in_memory_graph
        # 1. Exact match
        for nid, data in g.nodes(data=True):
            if data.get("name", "").lower() == q_norm or nid.lower() == q_norm:
                return data
        # 2. Substring match
        for nid, data in g.nodes(data=True):
            name = data.get("name", "").lower()
            if q_norm in name or name in q_norm:
                return data

        return None

    def search_concepts(self, query: str, limit: int = 15) -> List[Dict[str, Any]]:
        """Search concepts matching query string."""
        q_norm = query.strip().lower()
        results = []

        if self.client.is_live and self.client.driver:
            try:
                with self.client.driver.session(database=self.client.settings.neo4j_database) as session:
                    cursor = session.run("""
                        MATCH (c)
                        WHERE toLower(c.name) CONTAINS toLower($q)
                           OR toLower(coalesce(c.description, '')) CONTAINS toLower($q)
                        RETURN c.id AS id, c.name AS name, labels(c)[0] AS type,
                               c.subject AS subject, c.difficulty AS difficulty,
                               c.description AS description, c.latex AS latex
                        LIMIT $limit
                    """, q=q_norm, limit=limit)
                    return [dict(record) for record in cursor]
            except Exception as e:
                logger.error(f"Neo4j search failed ({e}), using in-memory.")

        g = self.client._in_memory_graph
        for nid, data in g.nodes(data=True):
            name = data.get("name", "").lower()
            desc = data.get("description", "").lower()
            if q_norm in name or q_norm in desc:
                results.append(data)
                if len(results) >= limit:
                    break
        return results

    def get_concept_neighborhood(self, concept_name: str) -> Dict[str, Any]:
        """
        Retrieve complete neighborhood for answer generation:
        - Prerequisites
        - Dependents (concepts enabled by this)
        - Relevant formulas
        - Relevant theorems
        - Related concepts
        """
        target = self.find_concept(concept_name)
        if not target:
            return {
                "concept": concept_name,
                "subject": "General",
                "difficulty": "Intermediate",
                "description": "",
                "prerequisites": [],
                "formulas": [],
                "theorems": [],
                "related_concepts": []
            }

        target_name = target["name"]
        target_id = target.get("id", target_name)

        if self.client.is_live and self.client.driver:
            try:
                with self.client.driver.session(database=self.client.settings.neo4j_database) as session:
                    res = session.run("""
                        MATCH (c {name: $name})
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
                               collect(DISTINCT d.name) AS dependents,
                               collect(DISTINCT {name: f.name, latex: f.latex, description: f.description}) AS formulas,
                               collect(DISTINCT {name: t.name, statement: t.description}) AS theorems,
                               collect(DISTINCT r.name) AS related_concepts
                    """, name=target_name).single()
                    if res:
                        data = dict(res)
                        # Clean empty dictionaries
                        data["formulas"] = [f for f in data["formulas"] if f.get("name")]
                        data["theorems"] = [t for t in data["theorems"] if t.get("name")]
                        return data
            except Exception as e:
                logger.error(f"Neo4j neighborhood query failed ({e}), falling back.")

        # In-memory graph traversal
        g = self.client._in_memory_graph
        # Find node id
        nid = target_id
        if nid not in g:
            for k, d in g.nodes(data=True):
                if d.get("name", "").lower() == target_name.lower():
                    nid = k
                    break

        prereqs = []
        dependents = []
        formulas = []
        theorems = []
        related = []

        if nid in g:
            # Inbound edges
            for pred in g.predecessors(nid):
                edge_data = g.get_edge_data(pred, nid)
                rel_type = edge_data.get("type")
                node_data = g.nodes[pred]
                if rel_type == "PREREQUISITE_OF":
                    prereqs.append(node_data.get("name", pred))
                elif rel_type in ("EXPLAINS", "PROVES") and node_data.get("type") == "Theorem":
                    theorems.append({"name": node_data.get("name"), "statement": node_data.get("description", "")})
                elif rel_type == "RELATED_TO":
                    related.append(node_data.get("name", pred))

            # Outbound edges
            for succ in g.successors(nid):
                edge_data = g.get_edge_data(nid, succ)
                rel_type = edge_data.get("type")
                node_data = g.nodes[succ]
                if rel_type == "PREREQUISITE_OF":
                    dependents.append(node_data.get("name", succ))
                elif rel_type == "USES_FORMULA":
                    formulas.append({
                        "name": node_data.get("name", succ),
                        "latex": node_data.get("latex", ""),
                        "description": node_data.get("description", "")
                    })
                elif rel_type == "RELATED_TO":
                    related.append(node_data.get("name", succ))

        return {
            "concept": target_name,
            "subject": target.get("subject", "General"),
            "difficulty": target.get("difficulty", "Intermediate"),
            "description": target.get("description", ""),
            "prerequisites": list(set(prereqs)),
            "dependents": list(set(dependents)),
            "formulas": formulas,
            "theorems": theorems,
            "related_concepts": list(set(related))
        }

    def get_prerequisites_chain(self, concept_name: str) -> Dict[str, Any]:
        """
        Compute multi-level prerequisite tree using graph traversal.
        Used for Feature 2: Prerequisite-Based Learning.
        """
        target = self.find_concept(concept_name)
        if not target:
            return {
                "target_concept": concept_name,
                "direct_prerequisites": [],
                "prerequisite_chain": [],
                "readiness_assessment_available": False
            }

        target_name = target["name"]
        target_id = target.get("id", target_name)
        g = self.client._in_memory_graph

        # Find target node id in graph
        nid = target_id
        if nid not in g:
            for k, d in g.nodes(data=True):
                if d.get("name", "").lower() == target_name.lower():
                    nid = k
                    break

        direct_prereqs = []
        chain = []
        visited = set()

        def dfs(current_id, depth):
            if depth > 4 or current_id in visited:
                return
            visited.add(current_id)

            for pred in g.predecessors(current_id):
                edge = g.get_edge_data(pred, current_id)
                if edge and edge.get("type") == "PREREQUISITE_OF":
                    p_data = g.nodes[pred]
                    p_name = p_data.get("name", pred)
                    if depth == 1:
                        direct_prereqs.append(p_name)
                    chain.append({
                        "name": p_name,
                        "difficulty": p_data.get("difficulty", "Intermediate"),
                        "subject": p_data.get("subject", target.get("subject", "General")),
                        "depth": depth
                    })
                    dfs(pred, depth + 1)

        dfs(nid, 1)

        return {
            "target_concept": target_name,
            "direct_prerequisites": list(set(direct_prereqs)),
            "prerequisite_chain": chain,
            "readiness_assessment_available": len(direct_prereqs) > 0
        }

    def get_entire_graph(self, subject: Optional[str] = None) -> GraphDataResponse:
        """Return all nodes and edges formatted for React Flow or Graph visualizers."""
        nodes = []
        edges = []

        g = self.client._in_memory_graph
        for nid, data in g.nodes(data=True):
            if subject and subject.lower() != "all" and data.get("subject", "").lower() != subject.lower():
                continue
            nodes.append(GraphNode(
                id=nid,
                name=data.get("name", nid),
                type=data.get("type", "Concept"),
                subject=data.get("subject", "General"),
                difficulty=data.get("difficulty", "Intermediate"),
                description=data.get("description", ""),
                latex=data.get("latex", "")
            ))

        valid_node_ids = {n.id for n in nodes}
        for u, v, data in g.edges(data=True):
            if u in valid_node_ids and v in valid_node_ids:
                edges.append(GraphEdge(
                    source=u,
                    target=v,
                    type=data.get("type", "RELATED_TO"),
                    description=data.get("description", "")
                ))

        return GraphDataResponse(
            nodes=nodes,
            edges=edges,
            total_nodes=len(nodes),
            total_edges=len(edges)
        )

    def get_topics_and_subjects(self) -> Dict[str, Any]:
        """List all topics organized by subject for curriculum browsing."""
        g = self.client._in_memory_graph
        subjects_dict = {}

        for nid, data in g.nodes(data=True):
            if data.get("type") in ("Concept", "Topic"):
                subj = data.get("subject", "General")
                if subj not in subjects_dict:
                    subjects_dict[subj] = []
                subjects_dict[subj].append(data.get("name", nid))

        for k in subjects_dict:
            subjects_dict[k] = sorted(list(set(subjects_dict[k])))

        return {
            "subjects": sorted(list(subjects_dict.keys())),
            "topics_by_subject": subjects_dict,
            "total_concepts": sum(len(v) for v in subjects_dict.values())
        }

    def add_concept_dynamically(self, name: str, subject: str = "General",
                               difficulty: str = "Intermediate", description: str = "",
                               source: str = "Uploaded Document",
                               prerequisites: List[str] = None,
                               related: List[str] = None) -> Dict[str, Any]:
        """
        Dynamically add a new concept extracted from an uploaded document.
        Idempotent: prevents duplicate nodes using name normalization.
        """
        name_clean = name.strip()
        cid = "dyn_" + re.sub(r'[^a-zA-Z0-9_]', '_', name_clean.lower())

        # Check existing
        existing = self.find_concept(name_clean)
        if existing:
            return {"status": "exists", "concept": existing["name"]}

        # Add to memory DiGraph
        self.client._in_memory_graph.add_node(
            cid,
            id=cid,
            name=name_clean,
            type="Concept",
            subject=subject,
            difficulty=difficulty,
            description=description,
            latex="",
            source=source
        )

        if prerequisites:
            for p in prerequisites:
                p_node = self.find_concept(p)
                if p_node:
                    p_id = p_node.get("id", p)
                    self.client._in_memory_graph.add_edge(p_id, cid, type="PREREQUISITE_OF")

        if related:
            for r in related:
                r_node = self.find_concept(r)
                if r_node:
                    r_id = r_node.get("id", r)
                    self.client._in_memory_graph.add_edge(cid, r_id, type="RELATED_TO")

        # Sync to live Neo4j if online
        if self.client.is_live and self.client.driver:
            try:
                with self.client.driver.session(database=self.client.settings.neo4j_database) as session:
                    session.run("""
                        MERGE (c:Concept {name: $name})
                        ON CREATE SET c.id = $id, c.subject = $subject, c.difficulty = $difficulty,
                                      c.description = $description, c.source = $source
                    """, name=name_clean, id=cid, subject=subject, difficulty=difficulty,
                         description=description, source=source)
            except Exception as e:
                logger.error(f"Failed to sync dynamic node to live Neo4j: {e}")

        return {"status": "created", "concept": name_clean, "id": cid}

# Singleton
_graph_service_instance: Optional[GraphService] = None

def get_graph_service() -> GraphService:
    global _graph_service_instance
    if _graph_service_instance is None:
        _graph_service_instance = GraphService()
    return _graph_service_instance

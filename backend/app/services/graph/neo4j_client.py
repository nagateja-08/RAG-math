import logging
from typing import List, Dict, Any, Optional
import networkx as nx

from ...core.config import get_settings
from .seed_data import SEED_NODES, SEED_RELATIONSHIPS
from .cypher_queries import CREATE_CONSTRAINTS

logger = logging.getLogger("mathgpt.graph")

class Neo4jClient:
    """
    Dual-mode Neo4j Client:
    - Connects to live Neo4j via official neo4j bolt driver if available.
    - Gracefully switches to high-performance in-memory DiGraph fallback if Neo4j is unavailable.
    - Zero downtime, 100% resilient.
    """

    def __init__(self):
        self.settings = get_settings()
        self.driver = None
        self.is_live = False
        self._in_memory_graph = nx.DiGraph()
        self._init_in_memory_store()
        self._try_connect_live()

    def _init_in_memory_store(self):
        """Seed the in-memory graph store with the mathematical curriculum."""
        self._in_memory_graph.clear()
        for node in SEED_NODES:
            self._in_memory_graph.add_node(
                node["id"],
                id=node["id"],
                name=node["name"],
                type=node.get("type", "Concept"),
                subject=node.get("subject", "General"),
                difficulty=node.get("difficulty", "Intermediate"),
                description=node.get("description", ""),
                latex=node.get("latex", ""),
                source=node.get("source", "Seed Curriculum")
            )

        for rel in SEED_RELATIONSHIPS:
            self._in_memory_graph.add_edge(
                rel["source"],
                rel["target"],
                type=rel["type"]
            )
        logger.info(f"Initialized in-memory graph with {len(self._in_memory_graph.nodes)} nodes and {len(self._in_memory_graph.edges)} edges.")

    def _try_connect_live(self):
        """Attempt to connect to Neo4j instance if configured and port is open."""
        import socket
        from urllib.parse import urlparse

        uri = self.settings.neo4j_uri
        user = self.settings.neo4j_username
        password = self.settings.neo4j_password

        if not uri or not password or password == "password" and "localhost" in uri:
            # Check if localhost:7687 port is actually listening
            parsed = urlparse(uri)
            host = parsed.hostname or "localhost"
            port = parsed.port or 7687
            is_open = False
            try:
                with socket.create_connection((host, port), timeout=0.2):
                    is_open = True
            except (socket.timeout, ConnectionRefusedError, OSError):
                is_open = False

            if not is_open:
                logger.info(f"Neo4j instance not reachable at {host}:{port}. Running on resilient in-memory mathematical knowledge graph.")
                self.is_live = False
                self.driver = None
                return

        try:
            from neo4j import GraphDatabase
            self.driver = GraphDatabase.driver(uri, auth=(user, password), connection_timeout=1.0)
            with self.driver.session(database=self.settings.neo4j_database) as session:
                session.run("RETURN 1").single()
            self.is_live = True
            logger.info("Successfully connected to live Neo4j database!")
            self._bootstrap_live_neo4j()
        except Exception as e:
            logger.info(f"Running on resilient in-memory mathematical knowledge graph (Live Neo4j: {e}).")
            self.is_live = False
            self.driver = None

    def _bootstrap_live_neo4j(self):
        """Apply schema constraints and seed initial mathematical graph in live Neo4j."""
        if not self.is_live or not self.driver:
            return
        try:
            with self.driver.session(database=self.settings.neo4j_database) as session:
                # Apply constraints
                for stmt in CREATE_CONSTRAINTS:
                    try:
                        session.run(stmt)
                    except Exception as ce:
                        logger.debug(f"Constraint notice: {ce}")

                # Check if seed nodes exist
                res = session.run("MATCH (c:Concept) RETURN count(c) AS cnt").single()
                count = res["cnt"] if res else 0
                if count < 5:
                    logger.info("Seeding live Neo4j with mathematical knowledge graph...")
                    for n in SEED_NODES:
                        label = n.get("type", "Concept")
                        cypher = f"""
                        MERGE (n:{label} {{name: $name}})
                        ON CREATE SET n.id = $id,
                                      n.type = $type,
                                      n.subject = $subject,
                                      n.difficulty = $difficulty,
                                      n.description = $description,
                                      n.latex = $latex,
                                      n.source = 'Seed'
                        """
                        session.run(cypher, **n)

                    for r in SEED_RELATIONSHIPS:
                        rel_type = r["type"]
                        cypher = f"""
                        MATCH (a {{id: $source}}), (b {{id: $target}})
                        MERGE (a)-[r:{rel_type}]->(b)
                        """
                        session.run(cypher, source=r["source"], target=r["target"])
                    logger.info("Live Neo4j successfully seeded!")
        except Exception as e:
            logger.error(f"Error bootstrapping live Neo4j: {e}")

    def close(self):
        if self.driver:
            self.driver.close()

# Singleton
_neo4j_client_instance: Optional[Neo4jClient] = None

def get_neo4j_client() -> Neo4jClient:
    global _neo4j_client_instance
    if _neo4j_client_instance is None:
        _neo4j_client_instance = Neo4jClient()
    return _neo4j_client_instance

import logging
from typing import Dict, Set, Iterable, List, Tuple, Optional, Any
from src.logger import PipelineLogger

# Retrieve pipeline-specific logger
logger = PipelineLogger.get_logger()

# Predefined bidirectional semantic relations between skills.
# All skills are defined in lowercase and stripped format.
BASE_RELATIONS: List[Tuple[str, str]] = [
    # embeddings ↔ dense retrieval ↔ semantic search ↔ vector search
    ("embeddings", "dense retrieval"),
    ("dense retrieval", "semantic search"),
    ("semantic search", "vector search"),
    
    # faiss ↔ vector database ↔ vector indexing
    ("faiss", "vector database"),
    ("vector database", "vector indexing"),
    
    # pinecone ↔ vector database
    ("pinecone", "vector database"),
    
    # bm25 ↔ lexical search ↔ sparse retrieval
    ("bm25", "lexical search"),
    ("lexical search", "sparse retrieval"),
    
    # ndcg ↔ ranking metrics
    ("ndcg", "ranking metrics"),
    
    # mrr ↔ ranking metrics
    ("mrr", "ranking metrics"),
    
    # Extra industry-standard additions for search and retrieval matching robustness
    ("qdrant", "vector database"),
    ("weaviate", "vector database"),
    ("milvus", "vector database"),
    ("opensearch", "vector database"),
    ("elasticsearch", "vector database"),
    ("map", "ranking metrics"),
    ("mean average precision", "ranking metrics"),

    # Added in expansion v2
    # DOMAIN 1 — LLM Models & Providers
    ("gpt", "openai"),
    ("gpt", "gpt-4"),
    ("gpt", "chatgpt"),
    ("gpt", "gpt-3.5"),
    ("claude", "anthropic"),
    ("claude", "claude-3"),
    ("claude", "claude-sonnet"),
    ("gemini", "google ai"),
    ("gemini", "bard"),
    ("gemini", "palm"),
    ("gemini", "gemini-pro"),
    ("llama", "meta ai"),
    ("llama", "llama-2"),
    ("llama", "llama-3"),
    ("llama", "codellama"),
    ("mistral", "mixtral"),
    ("mistral", "mistral-7b"),
    ("mistral", "mistral-large"),
    ("phi", "microsoft phi"),
    ("phi", "phi-2"),
    ("phi", "phi-3"),
    ("phi", "small language model"),

    # DOMAIN 2 — Vector Databases
    ("qdrant", "qdrant cloud"),
    ("qdrant", "vector search"),
    ("qdrant", "approximate nearest neighbor"),
    ("pinecone", "pinecone index"),
    ("pinecone", "serverless vector db"),
    ("weaviate", "weaviate cloud"),
    ("weaviate", "graphql vector search"),
    ("chroma", "chromadb"),
    ("chroma", "local vector store"),
    ("milvus", "milvus lite"),
    ("milvus", "zilliz"),
    ("faiss", "facebook ai similarity search"),
    ("faiss", "ivf index"),
    ("faiss", "hnsw"),
    ("pgvector", "postgres vector"),
    ("pgvector", "supabase vector"),

    # DOMAIN 3 — Fine-tuning Techniques
    ("lora", "low rank adaptation"),
    ("lora", "lora rank"),
    ("lora", "lora alpha"),
    ("qlora", "quantized lora"),
    ("qlora", "4-bit lora"),
    ("qlora", "nf4"),
    ("peft", "parameter efficient fine tuning"),
    ("peft", "adapter tuning"),
    ("rlhf", "reinforcement learning from human feedback"),
    ("rlhf", "reward model"),
    ("dpo", "direct preference optimization"),
    ("dpo", "preference learning"),
    ("sft", "supervised fine tuning"),
    ("sft", "instruction tuning"),
    ("sft", "chat tuning"),
    ("unsloth", "fast lora training"),
    ("unsloth", "memory efficient training"),

    # DOMAIN 4 — MLOps & Experiment Tracking
    ("mlflow", "ml experiment tracking"),
    ("mlflow", "mlflow registry"),
    ("wandb", "weights and biases"),
    ("wandb", "experiment tracking"),
    ("wandb", "w&b"),
    ("kubeflow", "ml pipeline orchestration"),
    ("kubeflow", "kfp"),
    ("vertex ai", "google vertex"),
    ("vertex ai", "vertex pipelines"),
    ("vertex ai", "vertex training"),
    ("sagemaker", "aws sagemaker"),
    ("sagemaker", "sagemaker training"),
    ("sagemaker", "sagemaker endpoints"),
    ("bentoml", "model serving"),
    ("bentoml", "bento service"),
    ("triton", "triton inference server"),
    ("triton", "nvidia triton"),
    ("triton", "tensorrt"),

    # DOMAIN 5 — Data Engineering
    ("spark", "apache spark"),
    ("spark", "pyspark"),
    ("spark", "spark sql"),
    ("spark", "databricks"),
    ("kafka", "apache kafka"),
    ("kafka", "kafka streams"),
    ("kafka", "confluent"),
    ("airflow", "apache airflow"),
    ("airflow", "dag"),
    ("airflow", "workflow orchestration"),
    ("dbt", "data build tool"),
    ("dbt", "dbt cloud"),
    ("dbt", "sql transformation"),
    ("flink", "apache flink"),
    ("flink", "stream processing"),
    ("ray", "ray tune"),
    ("ray", "ray train"),
    ("ray", "distributed ml"),

    # DOMAIN 6 — Retrieval & Search
    ("rag", "retrieval augmented generation"),
    ("rag", "retrieval pipeline"),
    ("bm25", "okapi bm25"),
    ("bm25", "sparse retrieval"),
    ("bm25", "term frequency"),
    ("embeddings", "dense vectors"),
    ("embeddings", "sentence embeddings"),
    ("embeddings", "text embeddings"),
    ("reranking", "cross encoder reranking"),
    ("reranking", "two stage retrieval"),
    ("semantic search", "dense retrieval"),
    ("semantic search", "neural search"),
    ("hybrid search", "sparse dense fusion"),
    ("hybrid search", "rrf"),
    ("hybrid search", "reciprocal rank fusion"),
    ("langchain", "lcel"),
    ("langchain", "langchain tools"),
    ("langchain", "langchain agents"),
    ("llamaindex", "llama index"),
    ("llamaindex", "gpt index"),
    ("llamaindex", "node parser"),
]


def build_skill_graph() -> Dict[str, Set[str]]:
    """Builds and returns the skill knowledge graph as an adjacency list.

    The graph is constructed bidirectionally from predefined semantic relations.
    All nodes are normalized to lowercase and stripped of outer whitespace.

    Returns:
        Dict[str, Set[str]]: Adjacency list representation mapping a skill to its neighbors.
    """
    graph: Dict[str, Set[str]] = {}

    def _add_edge(u: str, v: str) -> None:
        u_norm = u.strip().lower()
        v_norm = v.strip().lower()
        if not u_norm or not v_norm:
            return
        if u_norm not in graph:
            graph[u_norm] = set()
        if v_norm not in graph:
            graph[v_norm] = set()
        graph[u_norm].add(v_norm)
        graph[v_norm].add(u_norm)

    for u, v in BASE_RELATIONS:
        _add_edge(u, v)

    logger.info("Skill knowledge graph successfully built with %d nodes.", len(graph))
    return graph


# Build and export global graph instance
SKILL_GRAPH: Dict[str, Set[str]] = build_skill_graph()


def get_global_graph() -> Dict[str, Set[str]]:
    """Retrieves the global singleton skill graph.

    Returns:
        Dict[str, Set[str]]: The global skill graph instance.
    """
    return SKILL_GRAPH


def expand_skill(skill: str, max_depth: Optional[int] = None) -> Set[str]:
    """Expands a single skill into a set of its semantically related skills in the graph.

    Performs a Breadth-First Search (BFS) traversal starting from the normalized skill.
    If the skill is not present in the graph, returns a set containing only the
    normalized input skill itself.

    Args:
        skill (str): The skill name string to expand.
        max_depth (Optional[int]): Maximum traversal depth (hops). If None, traverses
                                   the entire connected component.

    Returns:
        Set[str]: A set of related skill names, including the original skill.
    """
    norm_skill = skill.strip().lower()
    if not norm_skill:
        return set()

    graph = get_global_graph()
    if norm_skill not in graph:
        return {norm_skill}

    visited: Set[str] = {norm_skill}
    queue: List[Tuple[str, int]] = [(norm_skill, 0)]

    head = 0
    while head < len(queue):
        curr, depth = queue[head]
        head += 1

        if max_depth is not None and depth >= max_depth:
            continue

        for neighbor in graph.get(curr, set()):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, depth + 1))

    return visited


def expand_skill_set(skills: Iterable[str], max_depth: Optional[int] = None) -> Set[str]:
    """Expands a collection of skills into their union of semantically related skills.

    Args:
        skills (Iterable[str]): An iterable of skill name strings.
        max_depth (Optional[int]): Maximum traversal depth for each individual skill.

    Returns:
        Set[str]: The union set of all related skills.
    """
    expanded: Set[str] = set()
    if not skills:
        return expanded

    for skill in skills:
        if isinstance(skill, str):
            expanded.update(expand_skill(skill, max_depth=max_depth))

    return expanded


_BFS_CACHE: Dict[Tuple[str, Optional[int]], Dict[str, int]] = {}

def expand_skill_cached(skill: str, graph: Dict[str, Set[str]], max_hops: Optional[int] = 2) -> Dict[str, int]:
    """Expands a single skill using BFS and returns distances to all reachable nodes within max_hops.
    Caches the results for fast O(1) distance lookups.
    """
    global _BFS_CACHE
    if len(_BFS_CACHE) > 500:
        logger.info("BFS cache size exceeded 500. Clearing cache to prevent memory bloat.")
        _BFS_CACHE.clear()

    cache_key = (skill, max_hops)
    if cache_key in _BFS_CACHE:
        return _BFS_CACHE[cache_key]

    norm_skill = skill.strip().lower()
    if not norm_skill:
        return {}

    if norm_skill not in graph:
        return {norm_skill: 0}

    distances = {norm_skill: 0}
    queue = [(norm_skill, 0)]
    head = 0
    while head < len(queue):
        curr, dist = queue[head]
        head += 1

        if max_hops is not None and dist >= max_hops:
            continue

        for neighbor in graph.get(curr, set()):
            if neighbor not in distances:
                distances[neighbor] = dist + 1
                queue.append((neighbor, dist + 1))

    _BFS_CACHE[cache_key] = distances
    return distances


def clear_bfs_cache() -> None:
    """Clears the global BFS cache."""
    _BFS_CACHE.clear()


def find_shortest_path_distance(
    start_node: str,
    target_nodes: Set[str],
    graph: Dict[str, Set[str]]
) -> Tuple[Optional[str], int]:
    """Finds the shortest path distance in the graph from start_node to any node in target_nodes.

    Uses cached BFS distances to optimize performance.

    Args:
        start_node (str): The starting node in the graph.
        target_nodes (Set[str]): The set of target nodes we want to reach.
        graph (Dict[str, Set[str]]): The skill knowledge graph.

    Returns:
        Tuple[Optional[str], int]: A tuple of:
            - The nearest target node found (or None if unreachable).
            - The shortest distance as an integer hops count (or -1 if unreachable).
    """
    distances = expand_skill_cached(start_node, graph, max_hops=2)

    min_dist = float('inf')
    best_node = None

    for target in target_nodes:
        t_norm = target.strip().lower()
        if t_norm in distances:
            dist = distances[t_norm]
            if dist < min_dist:
                min_dist = dist
                best_node = target

    if best_node is not None:
        return best_node, min_dist

    return None, -1


def compute_skill_overlap(
    candidate_skills: Iterable[str],
    jd_skills: Iterable[str],
    decay_factor: float = 0.8
) -> Dict[str, Any]:
    """Computes a detailed semantic overlap score between candidate skills and JD skills.

    For each JD skill, it finds the closest matching candidate skill using direct
    matching (score = 1.0) or shortest-path search in the skill graph
    (score = decay_factor^distance).

    Args:
        candidate_skills (Iterable[str]): Skills possessed by the candidate.
        jd_skills (Iterable[str]): Skills required by the job description.
        decay_factor (float): Decay multiplier per hop distance (default: 0.8).

    Returns:
        Dict[str, Any]: A dictionary containing:
            - "overlap_score": float, sum of similarity scores for all JD skills.
            - "normalized_overlap_score": float, average score (overlap_score / len(jd_skills)).
            - "direct_matches": List[str], JD skills matched directly (distance = 0).
            - "semantic_matches": List[str], JD skills matched semantically (distance > 0).
            - "unmatched_skills": List[str], JD skills with no direct or semantic match.
            - "match_details": Dict[str, Dict[str, Any]], maps each JD skill to details:
                {"matched_candidate_skill": str or None, "distance": int, "score": float}
    """
    # Normalize inputs
    cand_set = {s.strip().lower() for s in candidate_skills if s and isinstance(s, str)}
    jd_list = [s.strip().lower() for s in jd_skills if s and isinstance(s, str)]

    if not jd_list:
        return {
            "overlap_score": 0.0,
            "normalized_overlap_score": 0.0,
            "direct_matches": [],
            "semantic_matches": [],
            "unmatched_skills": [],
            "match_details": {}
        }

    graph = get_global_graph()

    overlap_score = 0.0
    direct_matches: List[str] = []
    semantic_matches: List[str] = []
    unmatched_skills: List[str] = []
    match_details: Dict[str, Dict[str, Any]] = {}

    for jd_skill in jd_list:
        if jd_skill in cand_set:
            # Direct match
            overlap_score += 1.0
            direct_matches.append(jd_skill)
            match_details[jd_skill] = {
                "matched_candidate_skill": jd_skill,
                "distance": 0,
                "score": 1.0
            }
        else:
            # Check for semantic matches in the graph
            matched_node, distance = find_shortest_path_distance(jd_skill, cand_set, graph)
            if matched_node is not None and distance > 0:
                score = float(decay_factor ** distance)
                overlap_score += score
                semantic_matches.append(jd_skill)
                match_details[jd_skill] = {
                    "matched_candidate_skill": matched_node,
                    "distance": distance,
                    "score": score
                }
            else:
                unmatched_skills.append(jd_skill)
                match_details[jd_skill] = {
                    "matched_candidate_skill": None,
                    "distance": -1,
                    "score": 0.0
                }

    normalized_score = float(overlap_score / len(jd_list))

    return {
        "overlap_score": float(overlap_score),
        "normalized_overlap_score": normalized_score,
        "direct_matches": direct_matches,
        "semantic_matches": semantic_matches,
        "unmatched_skills": unmatched_skills,
        "match_details": match_details
    }

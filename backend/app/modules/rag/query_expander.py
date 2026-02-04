"""
RAG Module - Query Expander
Expansión de consultas con términos legales y ontología
"""

from typing import List, Dict


# Ontología legal básica para Perú
LEGAL_ONTOLOGY: Dict[str, List[str]] = {
    # Cooperación internacional
    "donaciones internacionales": [
        "cooperación internacional",
        "recepción de fondos externos",
        "requisitos regulatorios ONG",
        "APCI registro",
        "transferencias internacionales regulación",
        "recursos de fuente extranjera",
    ],
    "apci": [
        "Agencia Peruana de Cooperación Internacional",
        "registro APCI",
        "cooperación técnica internacional",
        "ENIEX",
        "IPREDA",
        "ONGD",
    ],

    # Tributario
    "sunat": [
        "Superintendencia Nacional de Aduanas y de Administración Tributaria",
        "obligaciones tributarias",
        "impuesto a la renta",
        "IGV",
        "RUC",
        "régimen tributario",
    ],
    "exoneración": [
        "inafectación",
        "beneficio tributario",
        "exención",
        "liberación tributaria",
    ],

    # Organizaciones
    "ong": [
        "organización no gubernamental",
        "organización sin fines de lucro",
        "asociación civil",
        "ONGD",
        "entidad receptora",
    ],
    "asociación civil": [
        "persona jurídica sin fines de lucro",
        "asociación sin fines de lucro",
        "organización civil",
        "estatutos",
        "asamblea general",
    ],
    "colectivo": [
        "agrupación informal",
        "organización sin personería",
        "grupo ciudadano",
        "colectivo ciudadano",
    ],

    # Laboral
    "contrato laboral": [
        "relación laboral",
        "contrato de trabajo",
        "vínculo laboral",
        "empleador",
        "trabajador",
        "planilla",
    ],
    "locación de servicios": [
        "recibo por honorarios",
        "contrato civil",
        "prestación de servicios",
        "independiente",
        "cuarta categoría",
    ],

    # Formalización
    "personería jurídica": [
        "registro SUNARP",
        "inscripción registral",
        "partida registral",
        "escritura pública",
        "constitución de asociación",
    ],
    "formalización": [
        "constitución legal",
        "registro formal",
        "regularización",
        "inscripción",
    ],

    # Propiedad intelectual
    "propiedad intelectual": [
        "derechos de autor",
        "marca registrada",
        "INDECOPI",
        "patente",
        "copyright",
    ],

    # Protección de datos
    "datos personales": [
        "protección de datos",
        "Ley 29733",
        "privacidad",
        "consentimiento informado",
        "banco de datos",
    ],
}


class LegalQueryExpander:
    """
    Expande consultas legales usando ontología y términos relacionados.
    """

    def __init__(self, ontology: Dict[str, List[str]] | None = None):
        self.ontology = ontology or LEGAL_ONTOLOGY

    def expand(self, query: str, max_expansions: int = 10) -> List[str]:
        """
        Expande la consulta con términos relacionados.

        Args:
            query: Consulta original
            max_expansions: Máximo número de términos a agregar

        Returns:
            Lista de términos expandidos (incluye query original)
        """
        query_lower = query.lower()
        expansions = set()

        # Buscar coincidencias en ontología
        for key, related_terms in self.ontology.items():
            if key in query_lower:
                expansions.update(related_terms[:max_expansions // 2])

            # También buscar si algún término relacionado está en la query
            for term in related_terms:
                if term.lower() in query_lower:
                    expansions.add(key)
                    expansions.update(related_terms[:3])
                    break

        # Limitar expansiones
        expansion_list = list(expansions)[:max_expansions]

        return expansion_list

    def get_search_queries(self, query: str) -> List[str]:
        """
        Genera múltiples queries de búsqueda para el retriever.

        Returns:
            Lista de queries incluyendo original y expansiones
        """
        expansions = self.expand(query)

        # Query original siempre primero
        queries = [query]

        # Agregar expansiones como queries adicionales
        for exp in expansions:
            if exp.lower() not in query.lower():
                queries.append(f"{query} {exp}")

        return queries[:5]  # Máximo 5 queries

    def extract_legal_entities(self, query: str) -> Dict[str, List[str]]:
        """
        Extrae entidades legales mencionadas en la query.

        Returns:
            Dict con categorías y entidades encontradas
        """
        query_lower = query.lower()
        entities = {
            "authorities": [],      # SUNAT, APCI, INDECOPI, etc.
            "org_types": [],        # ONG, asociación, colectivo
            "legal_concepts": [],   # exoneración, personería, etc.
            "document_types": [],   # contrato, estatutos, etc.
        }

        # Autoridades
        authorities = ["sunat", "apci", "sunarp", "indecopi", "mtpe"]
        for auth in authorities:
            if auth in query_lower:
                entities["authorities"].append(auth.upper())

        # Tipos de organización
        org_types = ["ong", "asociación", "fundación", "colectivo", "cooperativa"]
        for org in org_types:
            if org in query_lower:
                entities["org_types"].append(org)

        # Conceptos legales
        concepts = ["exoneración", "personería", "registro", "tributario", "laboral"]
        for concept in concepts:
            if concept in query_lower:
                entities["legal_concepts"].append(concept)

        return entities

    def add_custom_terms(self, key: str, terms: List[str]):
        """Agrega términos personalizados a la ontología"""
        if key in self.ontology:
            self.ontology[key].extend(terms)
        else:
            self.ontology[key] = terms

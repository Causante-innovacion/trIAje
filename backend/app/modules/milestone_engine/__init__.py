# Milestone Engine Module
"""
Construye ruta paso a paso para cumplimiento.

Funciones:
- dependency_graph_builder
- prerequisite_ordering
- milestone_grouping
- authority_mapping
- document_mapping

Output:
- milestone_dag
- execution_sequence
"""

from .service import MilestoneEngine
from .dag_builder import Milestone, MilestoneDAG, ExecutionSequence

__all__ = [
    "MilestoneEngine",
    "Milestone",
    "MilestoneDAG",
    "ExecutionSequence",
]

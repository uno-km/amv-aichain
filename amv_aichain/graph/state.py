# Copyright (c) 2026 Uno Kim / AMEVA Foundation. All rights reserved.
# SPDX-License-Identifier: Apache-2.0 OR Commercial-License
"""
==============================================================================
amv-aichain Graph Engine: StateGraph & Parallel Fan-Out/Fan-In Orchestration
==============================================================================
Ultra-lightweight state machine and cyclic multi-agent graph engine supporting
concurrent multi-branch Fan-Out and Fan-In node convergence with State Reducers.
Zero external heavy dependencies - Pure Python 3.10+ standard library.
"""

from __future__ import annotations
import inspect
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any, AsyncIterator, Callable, Dict, Iterator, List, Optional, Sequence, Set, Tuple, Union
from amv_aichain.core.base import Runnable

START = "__start__"
END = "__end__"

class StateGraph:
    """Cyclic state graph orchestrator replacing heavy LangGraph dependencies."""

    def __init__(self, state_schema: Optional[type] = None):
        self.state_schema = state_schema or dict
        self.nodes: Dict[str, Callable[[Dict[str, Any]], Union[Dict[str, Any], Any]]] = {}
        self.edges: Dict[str, Union[str, List[str]]] = {}
        self.conditional_edges: Dict[str, Tuple[Callable[[Dict[str, Any]], Union[str, Sequence[str]]], Optional[Dict[str, str]]]] = {}
        self.entry_point: Optional[str] = None

    def add_node(self, name: str, action: Callable[[Dict[str, Any]], Union[Dict[str, Any], Any]]) -> StateGraph:
        if name in (START, END):
            raise ValueError(f"Cannot name node '{name}': reserved keyword.")
        self.nodes[name] = action
        return self

    def add_edge(self, from_node: str, to_node: Union[str, Sequence[str]]) -> StateGraph:
        """
        Adds a static transition edge from one node to another.
        Supports multi-branch Fan-Out if to_node is a list or sequence of node names.
        """
        if from_node == START:
            if isinstance(to_node, str):
                self.entry_point = to_node
            else:
                raise ValueError("START node must point to a single initial entry point.")
        else:
            if isinstance(to_node, (list, tuple)):
                self.edges[from_node] = list(to_node)
            else:
                self.edges[from_node] = to_node
        return self

    def add_conditional_edges(
        self,
        source: str,
        router: Callable[[Dict[str, Any]], Union[str, Sequence[str]]],
        path_map: Optional[Dict[str, str]] = None
    ) -> StateGraph:
        """
        Adds dynamic transition router. If router returns multiple targets (list),
        the graph executes them in parallel (Fan-Out).
        """
        self.conditional_edges[source] = (router, path_map)
        return self

    def set_entry_point(self, node_name: str) -> StateGraph:
        self.entry_point = node_name
        return self

    def set_finish_point(self, node_name: str) -> StateGraph:
        self.edges[node_name] = END
        return self

    def compile(self) -> CompiledGraph:
        if not self.entry_point:
            raise ValueError("StateGraph requires an entry point. Call set_entry_point() or add_edge(START, ...).")
        return CompiledGraph(
            nodes=dict(self.nodes),
            edges=dict(self.edges),
            conditional_edges=dict(self.conditional_edges),
            entry_point=self.entry_point,
            state_schema=self.state_schema
        )


class CompiledGraph(Runnable):
    """Executable compiled state graph instance supporting concurrent multi-branch Fan-Out."""

    def __init__(
        self,
        nodes: Dict[str, Callable[[Dict[str, Any]], Any]],
        edges: Dict[str, Union[str, List[str]]],
        conditional_edges: Dict[str, Tuple[Callable[[Dict[str, Any]], Union[str, Sequence[str]]], Optional[Dict[str, str]]]],
        entry_point: str,
        state_schema: type
    ):
        self.nodes = nodes
        self.edges = edges
        self.conditional_edges = conditional_edges
        self.entry_point = entry_point
        self.state_schema = state_schema

    def _get_next_targets(self, current_node: str, state: Dict[str, Any]) -> List[str]:
        """Resolves target node(s) for the next execution step."""
        # 1. Check conditional edge
        if current_node in self.conditional_edges:
            router, path_map = self.conditional_edges[current_node]
            route_res = router(state)
            if isinstance(route_res, (list, tuple)):
                targets = []
                for item in route_res:
                    mapped = path_map.get(item, item) if path_map else item
                    targets.append(mapped)
                return targets
            elif path_map and route_res in path_map:
                return [path_map[route_res]]
            return [route_res]

        # 2. Check static edge
        if current_node in self.edges:
            edge_val = self.edges[current_node]
            if isinstance(edge_val, list):
                return list(edge_val)
            return [edge_val]

        return [END]

    @staticmethod
    def _merge_state(base_state: Dict[str, Any], update: Dict[str, Any]) -> None:
        """State Reducer: merges updates into state resolving list/dict collisions safely."""
        for k, v in update.items():
            if k in base_state:
                orig = base_state[k]
                if isinstance(orig, list) and isinstance(v, list):
                    base_state[k] = orig + v
                elif isinstance(orig, dict) and isinstance(v, dict):
                    base_state[k] = {**orig, **v}
                else:
                    base_state[k] = v
            else:
                base_state[k] = v

    def invoke(self, input_val: Dict[str, Any], max_iterations: int = 50, **kwargs: Any) -> Dict[str, Any]:
        state = dict(input_val) if isinstance(input_val, dict) else {"input": input_val}
        active_nodes: List[str] = [self.entry_point]
        iteration = 0

        while active_nodes and iteration < max_iterations:
            # Filter out END markers
            real_nodes = [n for n in active_nodes if n != END]
            if not real_nodes:
                break

            for node in real_nodes:
                if node not in self.nodes:
                    raise KeyError(f"Node '{node}' not registered in StateGraph.")

            next_candidates: List[str] = []

            if len(real_nodes) == 1:
                # Single node execution
                node_name = real_nodes[0]
                action = self.nodes[node_name]
                update = action(state)
                if isinstance(update, dict):
                    self._merge_state(state, update)
                next_candidates.extend(self._get_next_targets(node_name, state))
            else:
                # Parallel Fan-Out execution
                max_w = min(len(real_nodes), 8)
                with ThreadPoolExecutor(max_workers=max_w) as executor:
                    futures = [executor.submit(self.nodes[n], dict(state)) for n in real_nodes]
                    for node_name, fut in zip(real_nodes, futures):
                        update = fut.result()
                        if isinstance(update, dict):
                            self._merge_state(state, update)
                        next_candidates.extend(self._get_next_targets(node_name, state))

            # Deduplicate targets while preserving order (Fan-In convergence)
            seen: Set[str] = set()
            active_nodes = [n for n in next_candidates if not (n in seen or seen.add(n))]
            iteration += 1

        if iteration >= max_iterations:
            raise RuntimeError(f"StateGraph exceeded maximum iteration safety limit ({max_iterations}). Possible infinite cycle.")

        return state

    async def ainvoke(self, input_val: Dict[str, Any], max_iterations: int = 50, **kwargs: Any) -> Dict[str, Any]:
        state = dict(input_val) if isinstance(input_val, dict) else {"input": input_val}
        active_nodes: List[str] = [self.entry_point]
        iteration = 0

        while active_nodes and iteration < max_iterations:
            real_nodes = [n for n in active_nodes if n != END]
            if not real_nodes:
                break

            for node in real_nodes:
                if node not in self.nodes:
                    raise KeyError(f"Node '{node}' not registered in StateGraph.")

            next_candidates: List[str] = []

            if len(real_nodes) == 1:
                node_name = real_nodes[0]
                action = self.nodes[node_name]
                if inspect.iscoroutinefunction(action):
                    update = await action(state)
                else:
                    update = action(state)
                if isinstance(update, dict):
                    self._merge_state(state, update)
                next_candidates.extend(self._get_next_targets(node_name, state))
            else:
                # True Async Concurrent Fan-Out
                async def _exec_single(n_name: str, st_copy: Dict[str, Any]) -> Tuple[str, Any]:
                    act = self.nodes[n_name]
                    if inspect.iscoroutinefunction(act):
                        res = await act(st_copy)
                    else:
                        res = await asyncio.to_thread(act, st_copy)
                    return n_name, res

                tasks = [_exec_single(n, dict(state)) for n in real_nodes]
                results = await asyncio.gather(*tasks)

                for node_name, update in results:
                    if isinstance(update, dict):
                        self._merge_state(state, update)
                    next_candidates.extend(self._get_next_targets(node_name, state))

            # Fan-In convergence
            seen: Set[str] = set()
            active_nodes = [n for n in next_candidates if not (n in seen or seen.add(n))]
            iteration += 1

        if iteration >= max_iterations:
            raise RuntimeError(f"StateGraph exceeded maximum iteration safety limit ({max_iterations}).")

        return state

    def stream(self, input_val: Dict[str, Any], max_iterations: int = 50, **kwargs: Any) -> Iterator[Tuple[str, Dict[str, Any]]]:
        state = dict(input_val) if isinstance(input_val, dict) else {"input": input_val}
        active_nodes: List[str] = [self.entry_point]
        iteration = 0

        while active_nodes and iteration < max_iterations:
            real_nodes = [n for n in active_nodes if n != END]
            if not real_nodes:
                break

            next_candidates: List[str] = []
            for node_name in real_nodes:
                if node_name not in self.nodes:
                    raise KeyError(f"Node '{node_name}' not registered in StateGraph.")
                action = self.nodes[node_name]
                update = action(state)
                if isinstance(update, dict):
                    self._merge_state(state, update)
                yield (node_name, dict(state))
                next_candidates.extend(self._get_next_targets(node_name, state))

            seen: Set[str] = set()
            active_nodes = [n for n in next_candidates if not (n in seen or seen.add(n))]
            iteration += 1

    async def astream(self, input_val: Dict[str, Any], max_iterations: int = 50, **kwargs: Any) -> AsyncIterator[Tuple[str, Dict[str, Any]]]:
        state = dict(input_val) if isinstance(input_val, dict) else {"input": input_val}
        active_nodes: List[str] = [self.entry_point]
        iteration = 0

        while active_nodes and iteration < max_iterations:
            real_nodes = [n for n in active_nodes if n != END]
            if not real_nodes:
                break

            next_candidates: List[str] = []
            for node_name in real_nodes:
                if node_name not in self.nodes:
                    raise KeyError(f"Node '{node_name}' not registered in StateGraph.")
                action = self.nodes[node_name]
                if inspect.iscoroutinefunction(action):
                    update = await action(state)
                else:
                    update = action(state)
                if isinstance(update, dict):
                    self._merge_state(state, update)
                yield (node_name, dict(state))
                next_candidates.extend(self._get_next_targets(node_name, state))

            seen: Set[str] = set()
            active_nodes = [n for n in next_candidates if not (n in seen or seen.add(n))]
            iteration += 1

    def __repr__(self) -> str:
        return f"CompiledGraph(nodes={list(self.nodes.keys())}, entry_point='{self.entry_point}')"
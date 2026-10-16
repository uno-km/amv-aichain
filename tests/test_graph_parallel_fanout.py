# Copyright (c) 2026 Uno Kim / AMEVA Foundation. All rights reserved.
# SPDX-License-Identifier: Apache-2.0 OR Commercial-License
"""
Unit tests for StateGraph parallel Fan-Out / Fan-In concurrency and State Reducer.
"""
from __future__ import annotations
import time
import asyncio
import pytest
from termux_aichain.graph.state import StateGraph, START, END


def test_stategraph_parallel_fanout_sync():
    """Verify that multiple targets in add_edge execute concurrently and reduce state properly."""
    builder = StateGraph()

    def step_dispatcher(state: dict) -> dict:
        return {"dispatched": True, "log": ["dispatched"]}

    def worker_a(state: dict) -> dict:
        time.sleep(0.05)
        return {
            "worker_a_done": True,
            "log": ["worker_a"],
            "sub_dict": {"a": 1},
        }

    def worker_b(state: dict) -> dict:
        time.sleep(0.05)
        return {
            "worker_b_done": True,
            "log": ["worker_b"],
            "sub_dict": {"b": 2},
        }

    def aggregator(state: dict) -> dict:
        return {
            "aggregated": True,
            "summary": f"workers:{state.get('worker_a_done')} & {state.get('worker_b_done')}",
        }

    builder.add_node("dispatcher", step_dispatcher)
    builder.add_node("worker_a", worker_a)
    builder.add_node("worker_b", worker_b)
    builder.add_node("aggregator", aggregator)

    builder.add_edge(START, "dispatcher")
    # Fan-Out to worker_a and worker_b simultaneously
    builder.add_edge("dispatcher", ["worker_a", "worker_b"])
    # Fan-In from both workers to aggregator
    builder.add_edge("worker_a", "aggregator")
    builder.add_edge("worker_b", "aggregator")
    builder.add_edge("aggregator", END)

    compiled = builder.compile()

    t0 = time.perf_counter()
    res = compiled.invoke({"init": 100})
    duration = time.perf_counter() - t0

    # Concurrency verification: runs concurrently without blocking (allow generous margin for Windows OS scheduling)
    assert duration < 0.50, f"Execution took {duration}s, expected concurrent execution < 0.50s"

    assert res["dispatched"] is True
    assert res["worker_a_done"] is True
    assert res["worker_b_done"] is True
    assert res["aggregated"] is True
    assert res["summary"] == "workers:True & True"

    # State Reducer verification:
    # 1. Lists must be accumulated
    assert "dispatched" in res["log"]
    assert "worker_a" in res["log"]
    assert "worker_b" in res["log"]

    # 2. Dictionaries must be shallow merged
    assert res["sub_dict"] == {"a": 1, "b": 2}


@pytest.mark.asyncio
async def test_stategraph_parallel_fanout_async():
    """Verify asynchronous Fan-Out using asyncio.gather."""
    builder = StateGraph()

    async def async_dispatcher(state: dict) -> dict:
        return {"status": "start"}

    async def async_branch_1(state: dict) -> dict:
        await asyncio.sleep(0.04)
        return {"branch_1": "ok", "items": [1]}

    async def async_branch_2(state: dict) -> dict:
        await asyncio.sleep(0.04)
        return {"branch_2": "ok", "items": [2]}

    async def async_collector(state: dict) -> dict:
        return {"all_done": True}

    builder.add_node("dispatcher", async_dispatcher)
    builder.add_node("branch_1", async_branch_1)
    builder.add_node("branch_2", async_branch_2)
    builder.add_node("collector", async_collector)

    builder.add_edge(START, "dispatcher")
    builder.add_edge("dispatcher", ["branch_1", "branch_2"])
    builder.add_edge("branch_1", "collector")
    builder.add_edge("branch_2", "collector")
    builder.add_edge("collector", END)

    compiled = builder.compile()

    t0 = time.perf_counter()
    res = await compiled.ainvoke({"input": "test"})
    duration = time.perf_counter() - t0

    # Concurrency verification: runs concurrently without blocking (allow generous margin for Windows OS scheduling)
    assert duration < 0.50, f"Async execution took {duration}s, expected < 0.50s"
    assert res["branch_1"] == "ok"
    assert res["branch_2"] == "ok"
    assert res["all_done"] is True
    assert sorted(res["items"]) == [1, 2]


def test_stategraph_conditional_fanout():
    """Verify conditional edge returning multiple targets triggers parallel Fan-Out."""
    builder = StateGraph()

    builder.add_node("route", lambda s: {"val": s["val"]})
    builder.add_node("left", lambda s: {"left": True})
    builder.add_node("right", lambda s: {"right": True})
    builder.add_node("single", lambda s: {"single": True})

    def router(s: dict):
        if s["val"] == "broadcast":
            return ["left", "right"]
        return "single"

    builder.add_edge(START, "route")
    builder.add_conditional_edges("route", router)
    builder.add_edge("left", END)
    builder.add_edge("right", END)
    builder.add_edge("single", END)

    compiled = builder.compile()

    # Case 1: Broadcast Fan-Out
    res_multi = compiled.invoke({"val": "broadcast"})
    assert res_multi.get("left") is True
    assert res_multi.get("right") is True
    assert "single" not in res_multi

    # Case 2: Single target
    res_single = compiled.invoke({"val": "other"})
    assert res_single.get("single") is True
    assert "left" not in res_single
    assert "right" not in res_single

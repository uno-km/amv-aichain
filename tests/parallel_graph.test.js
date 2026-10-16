/**
 * Copyright (c) 2026 Uno Kim / AMEVA Foundation. All rights reserved.
 * SPDX-License-Identifier: Apache-2.0 OR Commercial-License
 */
import test from "node:test";
import assert from "node:assert";

import { StateGraph, START, END } from "../js/esm/index.js";

test("Node.js: StateGraph parallel Fan-Out / Fan-In with State Reducer", async () => {
  const builder = new StateGraph();

  builder.addNode("dispatcher", (state) => ({
    dispatched: true,
    logs: ["dispatched"],
  }));

  builder.addNode("branch_a", async (state) => {
    await new Promise((r) => setTimeout(r, 30));
    return {
      branch_a_done: true,
      logs: ["branch_a"],
      sub_dict: { a: 1 },
    };
  });

  builder.addNode("branch_b", async (state) => {
    await new Promise((r) => setTimeout(r, 30));
    return {
      branch_b_done: true,
      logs: ["branch_b"],
      sub_dict: { b: 2 },
    };
  });

  builder.addNode("aggregator", (state) => ({
    aggregated: true,
    summary: `${state.branch_a_done && state.branch_b_done}`,
  }));

  builder.addEdge(START, "dispatcher");
  // Parallel Fan-Out
  builder.addEdge("dispatcher", ["branch_a", "branch_b"]);
  // Fan-In to aggregator
  builder.addEdge("branch_a", "aggregator");
  builder.addEdge("branch_b", "aggregator");
  builder.addEdge("aggregator", END);

  const compiled = builder.compile();

  const t0 = Date.now();
  const res = await compiled.invoke({ init: true });
  const duration = Date.now() - t0;

  // Since branch_a and branch_b run in parallel via Promise.all, 30ms + 30ms completes in ~30-60ms, well under 100ms
  assert.ok(duration < 100, `Execution duration was ${duration}ms, expected parallel < 100ms`);

  assert.strictEqual(res.dispatched, true);
  assert.strictEqual(res.branch_a_done, true);
  assert.strictEqual(res.branch_b_done, true);
  assert.strictEqual(res.aggregated, true);
  assert.strictEqual(res.summary, "true");

  // State Reducer: lists are concatenated
  assert.ok(res.logs.includes("dispatched"));
  assert.ok(res.logs.includes("branch_a"));
  assert.ok(res.logs.includes("branch_b"));

  // State Reducer: dictionaries are merged
  assert.deepStrictEqual(res.sub_dict, { a: 1, b: 2 });
});

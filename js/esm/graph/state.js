/**
 * Copyright (c) 2026 Uno Kim / AMEVA Foundation. All rights reserved.
 * SPDX-License-Identifier: Apache-2.0 OR Commercial-License
 */
/**
 * ==============================================================================
 * @termux-ai/chain Graph Engine: StateGraph & Cyclic State Machine (TypeScript ESM)
 * ==============================================================================
 */
export const START = "__start__";
export const END = "__end__";

export function mergeState(current, update) {
    const merged = { ...current };
    for (const [key, val] of Object.entries(update)) {
        if (val === undefined)
            continue;
        const existing = merged[key];
        if (Array.isArray(existing) && Array.isArray(val)) {
            merged[key] = [...existing, ...val];
        }
        else if (existing &&
            typeof existing === "object" &&
            !Array.isArray(existing) &&
            val &&
            typeof val === "object" &&
            !Array.isArray(val)) {
            merged[key] = { ...existing, ...val };
        }
        else {
            merged[key] = val;
        }
    }
    return merged;
}

export class StateGraph {
    nodes = new Map();
    edges = new Map();
    conditionalEdges = new Map();
    entryPoints = [];
    constructor(stateSchema) { }
    addNode(name, fn) {
        this.nodes.set(name, fn);
        return this;
    }
    addEdge(fromNode, toNode) {
        const targets = Array.isArray(toNode) ? toNode : [toNode];
        if (fromNode === START) {
            this.entryPoints = targets;
        }
        else {
            const existing = this.edges.get(fromNode) ?? [];
            this.edges.set(fromNode, [...existing, ...targets]);
        }
        return this;
    }
    setEntryPoint(nodeName) {
        this.entryPoints = [nodeName];
        return this;
    }
    setFinishPoint(nodeName) {
        const existing = this.edges.get(nodeName) ?? [];
        this.edges.set(nodeName, [...existing, END]);
        return this;
    }
    addConditionalEdges(fromNode, condition, pathMap) {
        this.conditionalEdges.set(fromNode, { condition, pathMap });
        return this;
    }
    compile() {
        if (this.entryPoints.length === 0) {
            throw new Error("No entry point defined. Call setEntryPoint or addEdge(START, ...).");
        }
        return new CompiledGraph(new Map(this.nodes), new Map(this.edges), new Map(this.conditionalEdges), [...this.entryPoints]);
    }
}

export class CompiledGraph {
    nodes;
    edges;
    conditionalEdges;
    entryPoints;
    constructor(nodes, edges, conditionalEdges, entryPoints) {
        this.nodes = nodes;
        this.edges = edges;
        this.conditionalEdges = conditionalEdges;
        this.entryPoints = entryPoints;
    }
    async invoke(initialState, maxIterations = 25) {
        let currentState = { ...initialState };
        let currentNodes = [...this.entryPoints];
        let iterations = 0;
        while (currentNodes.length > 0 && !currentNodes.every(n => n === END)) {
            iterations++;
            if (iterations > maxIterations) {
                throw new Error(`Graph execution exceeded max iterations limit (${maxIterations}).`);
            }
            const activeNodes = currentNodes.filter(n => n !== END);
            if (activeNodes.length === 0)
                break;
            const results = await Promise.all(activeNodes.map(async (nodeName) => {
                const nodeFn = this.nodes.get(nodeName);
                if (!nodeFn) {
                    throw new Error(`Node '${nodeName}' is not defined in graph.`);
                }
                const res = await nodeFn(currentState);
                return { nodeName, res };
            }));
            for (const { res } of results) {
                if (res && typeof res === "object") {
                    currentState = mergeState(currentState, res);
                }
            }
            const nextNodeSet = new Set();
            for (const { nodeName } of results) {
                const condEdge = this.conditionalEdges.get(nodeName);
                if (condEdge) {
                    const targetKey = await Promise.resolve(condEdge.condition(currentState));
                    const targetKeys = Array.isArray(targetKey) ? targetKey : [targetKey];
                    for (const tk of targetKeys) {
                        const resolved = condEdge.pathMap ? (condEdge.pathMap[tk] ?? tk) : tk;
                        nextNodeSet.add(resolved);
                    }
                }
                else if (this.edges.has(nodeName)) {
                    for (const target of this.edges.get(nodeName)) {
                        nextNodeSet.add(target);
                    }
                }
                else {
                    nextNodeSet.add(END);
                }
            }
            currentNodes = Array.from(nextNodeSet);
        }
        return currentState;
    }
    async *stream(initialState, maxIterations = 25) {
        let currentState = { ...initialState };
        let currentNodes = [...this.entryPoints];
        let iterations = 0;
        while (currentNodes.length > 0 && !currentNodes.every(n => n === END)) {
            iterations++;
            if (iterations > maxIterations) {
                throw new Error(`Graph execution exceeded max iterations limit (${maxIterations}).`);
            }
            const activeNodes = currentNodes.filter(n => n !== END);
            if (activeNodes.length === 0)
                break;
            const results = await Promise.all(activeNodes.map(async (nodeName) => {
                const nodeFn = this.nodes.get(nodeName);
                if (!nodeFn) {
                    throw new Error(`Node '${nodeName}' is not defined in graph.`);
                }
                const res = await nodeFn(currentState);
                return { nodeName, res };
            }));
            for (const { res } of results) {
                if (res && typeof res === "object") {
                    currentState = mergeState(currentState, res);
                }
            }
            yield [activeNodes, currentState];
            const nextNodeSet = new Set();
            for (const { nodeName } of results) {
                const condEdge = this.conditionalEdges.get(nodeName);
                if (condEdge) {
                    const targetKey = await Promise.resolve(condEdge.condition(currentState));
                    const targetKeys = Array.isArray(targetKey) ? targetKey : [targetKey];
                    for (const tk of targetKeys) {
                        const resolved = condEdge.pathMap ? (condEdge.pathMap[tk] ?? tk) : tk;
                        nextNodeSet.add(resolved);
                    }
                }
                else if (this.edges.has(nodeName)) {
                    for (const target of this.edges.get(nodeName)) {
                        nextNodeSet.add(target);
                    }
                }
                else {
                    nextNodeSet.add(END);
                }
            }
            currentNodes = Array.from(nextNodeSet);
        }
    }
}

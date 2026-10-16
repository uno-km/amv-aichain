/**
 * Copyright (c) 2026 Uno Kim / AMEVA Foundation. All rights reserved.
 * SPDX-License-Identifier: Apache-2.0 OR Commercial-License
 */
/**
 * ==============================================================================
 * @termux-ai/chain Core Runnable & Pipeline Abstractions
 * ==============================================================================
 */
export class RunnableLambda {
    fn;
    constructor(fn) {
        this.fn = fn;
    }
    async invoke(input, options) {
        return await this.fn(input, options);
    }
    pipe(next) {
        return createPipeline([this, next]);
    }
}
export class RunnableSequence {
    steps;
    constructor(steps) {
        this.steps = steps;
    }
    async invoke(input, options) {
        let current = input;
        for (let i = 0; i < this.steps.length; i++) {
            if (i === 0 && options) {
                current = await this.steps[i].invoke(current, options);
            }
            else {
                current = await this.steps[i].invoke(current);
            }
        }
        return current;
    }
    async *stream(input, options) {
        if (this.steps.length === 0)
            return;
        let current = input;
        for (let i = 0; i < this.steps.length - 1; i++) {
            if (i === 0 && options) {
                current = await this.steps[i].invoke(current, options);
            }
            else {
                current = await this.steps[i].invoke(current);
            }
        }
        const last = this.steps[this.steps.length - 1];
        if (last.stream) {
            for await (const chunk of last.stream(current)) {
                yield chunk;
            }
        }
        else {
            yield await last.invoke(current);
        }
    }
    pipe(next) {
        const nextRunnable = typeof next === "function" ? new RunnableLambda(next) : next;
        if (nextRunnable instanceof RunnableSequence) {
            return new RunnableSequence([...this.steps, ...nextRunnable.steps]);
        }
        return new RunnableSequence([...this.steps, nextRunnable]);
    }
}
export class RunnablePassthrough {
    constructor(fn) {
        this.fn = fn;
    }
    async invoke(input, options) {
        if (this.fn) {
            return await this.fn(input);
        }
        return input;
    }
    pipe(next) {
        return createPipeline([this, next]);
    }
}
export class RunnableParallel {
    constructor(steps) {
        this.steps = {};
        for (const [k, v] of Object.entries(steps)) {
            if (typeof v === "function") {
                this.steps[k] = new RunnableLambda(v);
            }
            else if (typeof v === "object" && v !== null && "invoke" in v) {
                this.steps[k] = v;
            }
            else {
                throw new TypeError(`RunnableParallel step '${k}' must be runnable or function`);
            }
        }
    }
    async invoke(input, options) {
        const keys = Object.keys(this.steps);
        const promises = keys.map(k => this.steps[k].invoke(input, options));
        const values = await Promise.all(promises);
        const result = {};
        for (let i = 0; i < keys.length; i++) {
            result[keys[i]] = values[i];
        }
        return result;
    }
    pipe(next) {
        return createPipeline([this, next]);
    }
}
export function createPipeline(steps) {
    const normalized = [];
    for (const s of steps) {
        if (typeof s === "function") {
            normalized.push(new RunnableLambda(s));
        }
        else if (s instanceof RunnableSequence) {
            normalized.push(...s.steps);
        }
        else if (typeof s === "object" && s !== null && "invoke" in s) {
            normalized.push(s);
        }
        else if (typeof s === "object" && s !== null) {
            normalized.push(new RunnableParallel(s));
        }
        else {
            throw new TypeError(`Cannot compose non-runnable element: ${typeof s}`);
        }
    }
    return new RunnableSequence(normalized);
}
export class BaseChatModel {
    async invoke(input, options) {
        const res = await this.generate(input, options);
        return res.message;
    }
    pipe(next) {
        return createPipeline([this, next]);
    }
}

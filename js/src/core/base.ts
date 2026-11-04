/**
 * Copyright (c) 2026 Uno Kim / AMEVA Foundation. All rights reserved.
 * SPDX-License-Identifier: Apache-2.0 OR Commercial-License
 */
﻿/**
 * ==============================================================================
 * amv-aichain Core Runnable & Pipeline Abstractions
 * ==============================================================================
 */

import { Message, AIMessage, GenerationResult, StreamChunk } from "./schema.js";

export interface Runnable<Input = any, Output = any> {
  invoke(input: Input, options?: any): Promise<Output>;
  stream?(input: Input, options?: any): AsyncIterable<any>;
  pipe<NextOutput>(next: Runnable<Output, NextOutput> | ((input: Output) => Promise<NextOutput> | NextOutput)): Runnable<Input, NextOutput>;
}

export class RunnableLambda<Input = any, Output = any> implements Runnable<Input, Output> {
  private fn: (input: Input, options?: any) => Promise<Output> | Output;

  constructor(fn: (input: Input, options?: any) => Promise<Output> | Output) {
    this.fn = fn;
  }

  async invoke(input: Input, options?: any): Promise<Output> {
    return await this.fn(input, options);
  }

  pipe<NextOutput>(next: Runnable<Output, NextOutput> | ((input: Output) => Promise<NextOutput> | NextOutput)): Runnable<Input, NextOutput> {
    return createPipeline([this, next]);
  }
}

export class RunnableSequence<Input = any, Output = any> implements Runnable<Input, Output> {
  steps: Runnable[];

  constructor(steps: Runnable[]) {
    this.steps = steps;
  }

  async invoke(input: Input, options?: any): Promise<Output> {
    let current: any = input;
    for (let i = 0; i < this.steps.length; i++) {
      if (i === 0 && options) {
        current = await this.steps[i].invoke(current, options);
      } else {
        current = await this.steps[i].invoke(current);
      }
    }
    return current;
  }

  async *stream(input: Input, options?: any): AsyncIterable<any> {
    if (this.steps.length === 0) return;
    let current: any = input;
    for (let i = 0; i < this.steps.length - 1; i++) {
      if (i === 0 && options) {
        current = await this.steps[i].invoke(current, options);
      } else {
        current = await this.steps[i].invoke(current);
      }
    }
    const last = this.steps[this.steps.length - 1];
    if (last.stream) {
      for await (const chunk of last.stream(current)) {
        yield chunk;
      }
    } else {
      yield await last.invoke(current);
    }
  }

  pipe<NextOutput>(next: Runnable<Output, NextOutput> | ((input: Output) => Promise<NextOutput> | NextOutput)): Runnable<Input, NextOutput> {
    const nextRunnable = typeof next === "function" ? new RunnableLambda(next) : next;
    if (nextRunnable instanceof RunnableSequence) {
      return new RunnableSequence([...this.steps, ...nextRunnable.steps]);
    }
    return new RunnableSequence([...this.steps, nextRunnable]);
  }
}

export class RunnablePassthrough<T = any> implements Runnable<T, T> {
  private fn?: (input: T) => any;

  constructor(fn?: (input: T) => any) {
    this.fn = fn;
  }

  async invoke(input: T, options?: any): Promise<T> {
    if (this.fn) {
      return await this.fn(input);
    }
    return input;
  }

  pipe<NextOutput>(next: Runnable<T, NextOutput> | ((input: T) => Promise<NextOutput> | NextOutput)): Runnable<T, NextOutput> {
    return createPipeline([this, next]);
  }
}

export class RunnableParallel<Input = any, Output = Record<string, any>> implements Runnable<Input, Output> {
  steps: Record<string, Runnable>;

  constructor(steps: Record<string, any>) {
    this.steps = {};
    for (const [k, v] of Object.entries(steps)) {
      if (typeof v === "function") {
        this.steps[k] = new RunnableLambda(v);
      } else if (typeof v === "object" && v !== null && "invoke" in v) {
        this.steps[k] = v;
      } else {
        throw new TypeError(`RunnableParallel step '${k}' must be runnable or function`);
      }
    }
  }

  async invoke(input: Input, options?: any): Promise<Output> {
    const keys = Object.keys(this.steps);
    const promises = keys.map(k => this.steps[k].invoke(input, options));
    const values = await Promise.all(promises);
    const result: Record<string, any> = {};
    for (let i = 0; i < keys.length; i++) {
      result[keys[i]] = values[i];
    }
    return result as Output;
  }

  pipe<NextOutput>(next: Runnable<Output, NextOutput> | ((input: Output) => Promise<NextOutput> | NextOutput)): Runnable<Input, NextOutput> {
    return createPipeline([this, next]);
  }
}

export function createPipeline(steps: any[]): RunnableSequence {
  const normalized: Runnable[] = [];
  for (const s of steps) {
    if (typeof s === "function") {
      normalized.push(new RunnableLambda(s));
    } else if (s instanceof RunnableSequence) {
      normalized.push(...s.steps);
    } else if (typeof s === "object" && s !== null && "invoke" in s) {
      normalized.push(s);
    } else if (typeof s === "object" && s !== null) {
      normalized.push(new RunnableParallel(s));
    } else {
      throw new TypeError(`Cannot compose non-runnable element: ${typeof s}`);
    }
  }
  return new RunnableSequence(normalized);
}

export abstract class BaseChatModel implements Runnable<Message[] | string, AIMessage> {
  abstract generate(messages: Message[] | string, options?: any): Promise<GenerationResult>;
  abstract stream(messages: Message[] | string, options?: any): AsyncIterable<StreamChunk>;

  async invoke(input: Message[] | string, options?: any): Promise<AIMessage> {
    const res = await this.generate(input, options);
    return res.message;
  }

  pipe<NextOutput>(next: Runnable<AIMessage, NextOutput> | ((input: AIMessage) => Promise<NextOutput> | NextOutput)): Runnable<Message[] | string, NextOutput> {
    return createPipeline([this, next]);
  }
}
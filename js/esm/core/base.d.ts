/**
 * Copyright (c) 2026 Uno Kim / AMEVA Foundation. All rights reserved.
 * SPDX-License-Identifier: Apache-2.0 OR Commercial-License
 */
/**
 * ==============================================================================
 * @termux-ai/chain Core Runnable & Pipeline Abstractions
 * ==============================================================================
 */
import { Message, AIMessage, GenerationResult, StreamChunk } from "./schema.js";
export interface Runnable<Input = any, Output = any> {
    invoke(input: Input, options?: any): Promise<Output>;
    stream?(input: Input, options?: any): AsyncIterable<any>;
    pipe<NextOutput>(next: Runnable<Output, NextOutput> | ((input: Output) => Promise<NextOutput> | NextOutput)): Runnable<Input, NextOutput>;
}
export declare class RunnableLambda<Input = any, Output = any> implements Runnable<Input, Output> {
    private fn;
    constructor(fn: (input: Input, options?: any) => Promise<Output> | Output);
    invoke(input: Input, options?: any): Promise<Output>;
    pipe<NextOutput>(next: Runnable<Output, NextOutput> | ((input: Output) => Promise<NextOutput> | NextOutput)): Runnable<Input, NextOutput>;
}
export declare class RunnableSequence<Input = any, Output = any> implements Runnable<Input, Output> {
    steps: Runnable[];
    constructor(steps: Runnable[]);
    invoke(input: Input, options?: any): Promise<Output>;
    stream(input: Input, options?: any): AsyncIterable<any>;
    pipe<NextOutput>(next: Runnable<Output, NextOutput> | ((input: Output) => Promise<NextOutput> | NextOutput)): Runnable<Input, NextOutput>;
}
export declare class RunnablePassthrough<T = any> implements Runnable<T, T> {
    private fn?;
    constructor(fn?: (input: T) => any);
    invoke(input: T, options?: any): Promise<T>;
    pipe<NextOutput>(next: Runnable<T, NextOutput> | ((input: T) => Promise<NextOutput> | NextOutput)): Runnable<T, NextOutput>;
}
export declare class RunnableParallel<Input = any, Output = Record<string, any>> implements Runnable<Input, Output> {
    steps: Record<string, Runnable>;
    constructor(steps: Record<string, any>);
    invoke(input: Input, options?: any): Promise<Output>;
    pipe<NextOutput>(next: Runnable<Output, NextOutput> | ((input: Output) => Promise<NextOutput> | NextOutput)): Runnable<Input, NextOutput>;
}
export declare function createPipeline(steps: any[]): RunnableSequence;
export declare abstract class BaseChatModel implements Runnable<Message[] | string, AIMessage> {
    abstract generate(messages: Message[] | string, options?: any): Promise<GenerationResult>;
    abstract stream(messages: Message[] | string, options?: any): AsyncIterable<StreamChunk>;
    invoke(input: Message[] | string, options?: any): Promise<AIMessage>;
    pipe<NextOutput>(next: Runnable<AIMessage, NextOutput> | ((input: AIMessage) => Promise<NextOutput> | NextOutput)): Runnable<Message[] | string, NextOutput>;
}

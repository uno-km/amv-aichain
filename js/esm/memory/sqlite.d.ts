/**
 * Copyright (c) 2026 Uno Kim / AMEVA Foundation. All rights reserved.
 * SPDX-License-Identifier: Apache-2.0 OR Commercial-License
 */
/**
 * ==============================================================================
 * @termux-ai/chain Memory Engine: In-Memory & Cosine Vector Store (TypeScript ESM)
 * ==============================================================================
 */
import { BaseEmbeddings } from "./embeddings.js";
import { Runnable } from "../core/base.js";
import { Document } from "../core/splitters.js";
export declare function cosineSimilarity(v1: number[], v2: number[]): number;
export interface VectorItem {
    id: string;
    content: string;
    metadata: Record<string, any>;
    embedding: number[];
}
export declare class MicroVectorStore {
    private items;
    embeddings?: BaseEmbeddings;
    constructor(options?: {
        embeddings?: BaseEmbeddings;
    });
    addTexts(texts: string[], embeddings?: number[][], metadatas?: Record<string, any>[]): Promise<string[]>;
    similaritySearchByVector(queryEmbedding: number[], k?: number): Array<{
        content: string;
        metadata: Record<string, any>;
        score: number;
    }>;
    similaritySearch(query: string, k?: number): Promise<Array<{
        content: string;
        metadata: Record<string, any>;
        score: number;
    }>>;
    hybridSearch(query: string, k?: number, alpha?: number): Promise<Array<{
        content: string;
        metadata: Record<string, any>;
        score: number;
    }>>;
    clear(): void;
    asRetriever(options?: {
        k?: number;
        searchType?: "similarity" | "hybrid";
    }): VectorStoreRetriever;
}
export declare class VectorStoreRetriever implements Runnable<string, Document[]> {
    vectorstore: MicroVectorStore;
    k: number;
    searchType: "similarity" | "hybrid";
    constructor(vectorstore: MicroVectorStore, options?: {
        k?: number;
        searchType?: "similarity" | "hybrid";
    });
    invoke(query: string, options?: any): Promise<Document[]>;
    pipe<NextOutput>(next: Runnable<Document[], NextOutput> | ((input: Document[]) => Promise<NextOutput> | NextOutput)): Runnable<string, NextOutput>;
}

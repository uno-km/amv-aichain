/**
 * Copyright (c) 2026 Uno Kim / AMEVA Foundation. All rights reserved.
 * SPDX-License-Identifier: Apache-2.0 OR Commercial-License
 */
/**
 * ==============================================================================
 * amv-aichain Memory Engine: In-Memory & Cosine Vector Store (TypeScript ESM)
 * ==============================================================================
 */

import { BaseEmbeddings } from "./embeddings.js";
import { Runnable, createPipeline } from "../core/base.js";
import { Document } from "../core/splitters.js";

export function cosineSimilarity(v1: number[], v2: number[]): number {
  if (v1.length !== v2.length || v1.length === 0) return 0;
  let dot = 0;
  let normA = 0;
  let normB = 0;
  for (let i = 0; i < v1.length; i++) {
    dot += v1[i] * v2[i];
    normA += v1[i] * v1[i];
    normB += v2[i] * v2[i];
  }
  normA = Math.sqrt(normA);
  normB = Math.sqrt(normB);
  if (normA === 0 || normB === 0) return 0;
  return dot / (normA * normB);
}

export interface VectorItem {
  id: string;
  content: string;
  metadata: Record<string, any>;
  embedding: number[];
}

export class MicroVectorStore {
  private items: VectorItem[] = [];
  public embeddings?: BaseEmbeddings;

  constructor(options?: { embeddings?: BaseEmbeddings }) {
    this.embeddings = options?.embeddings;
  }

  async addTexts(
    texts: string[],
    embeddings?: number[][],
    metadatas?: Record<string, any>[]
  ): Promise<string[]> {
    let resolvedEmbs = embeddings;
    if (!resolvedEmbs) {
      if (!this.embeddings) {
        throw new Error("Embeddings must be provided in addTexts or bound to MicroVectorStore.");
      }
      resolvedEmbs = await this.embeddings.embedDocuments(texts);
    }

    const ids: string[] = [];
    for (let i = 0; i < texts.length; i++) {
      const id = String(this.items.length + 1);
      this.items.push({
        id,
        content: texts[i],
        metadata: metadatas?.[i] ?? {},
        embedding: resolvedEmbs[i]
      });
      ids.push(id);
    }
    return ids;
  }

  similaritySearchByVector(
    queryEmbedding: number[],
    k: number = 4
  ): Array<{ content: string; metadata: Record<string, any>; score: number }> {
    const scored = this.items.map(item => ({
      content: item.content,
      metadata: item.metadata,
      score: cosineSimilarity(queryEmbedding, item.embedding)
    }));
    scored.sort((a, b) => b.score - a.score);
    return scored.slice(0, k);
  }

  async similaritySearch(
    query: string,
    k: number = 4
  ): Promise<Array<{ content: string; metadata: Record<string, any>; score: number }>> {
    if (!this.embeddings) {
      throw new Error("similaritySearch requires an embeddings model bound to MicroVectorStore.");
    }
    const queryEmb = await this.embeddings.embedQuery(query);
    return this.similaritySearchByVector(queryEmb, k);
  }

  async hybridSearch(
    query: string,
    k: number = 4,
    alpha: number = 0.5
  ): Promise<Array<{ content: string; metadata: Record<string, any>; score: number }>> {
    const tokens = (query.toLowerCase().match(/\w+/g) || []).filter(t => t.length > 1);
    if (!this.embeddings) {
      throw new Error("hybridSearch requires an embeddings model bound to MicroVectorStore.");
    }

    const queryEmb = await this.embeddings.embedQuery(query);
    if (tokens.length === 0) {
      return this.similaritySearchByVector(queryEmb, k);
    }

    // Keyword filtering & scoring
    const keywordMatches = this.items
      .map(item => {
        const textLower = item.content.toLowerCase();
        let matchCount = 0;
        for (const t of tokens) {
          if (textLower.includes(t)) matchCount++;
        }
        return { item, matchCount };
      })
      .filter(x => x.matchCount > 0);

    const candidates = keywordMatches.length > 0 ? keywordMatches.map(x => x.item) : this.items;

    // RRF Scoring
    const scored = candidates.map(item => {
      const vecSim = cosineSimilarity(queryEmb, item.embedding);
      return { item, vecSim };
    });

    scored.sort((a, b) => b.vecSim - a.vecSim);
    return scored.slice(0, k).map(x => ({
      content: x.item.content,
      metadata: x.item.metadata,
      score: x.vecSim
    }));
  }

  clear(): void {
    this.items = [];
  }

  asRetriever(options?: { k?: number; searchType?: "similarity" | "hybrid" }): VectorStoreRetriever {
    return new VectorStoreRetriever(this, options);
  }
}

export class VectorStoreRetriever implements Runnable<string, Document[]> {
  vectorstore: MicroVectorStore;
  k: number;
  searchType: "similarity" | "hybrid";

  constructor(vectorstore: MicroVectorStore, options: { k?: number; searchType?: "similarity" | "hybrid" } = {}) {
    this.vectorstore = vectorstore;
    this.k = options.k ?? 4;
    this.searchType = options.searchType ?? "similarity";
  }

  async invoke(query: string, options?: any): Promise<Document[]> {
    const k = options?.k ?? this.k;
    let results: Array<{ content: string; metadata: Record<string, any>; score: number }>;
    if (this.searchType === "hybrid") {
      results = await this.vectorstore.hybridSearch(query, k);
    } else {
      results = await this.vectorstore.similaritySearch(query, k);
    }
    return results.map(r => ({
      pageContent: r.content,
      metadata: { ...r.metadata, score: r.score }
    }));
  }

  pipe<NextOutput>(next: Runnable<Document[], NextOutput> | ((input: Document[]) => Promise<NextOutput> | NextOutput)): Runnable<string, NextOutput> {
    return createPipeline([this, next]);
  }
}
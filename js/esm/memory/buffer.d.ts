/**
 * Copyright (c) 2026 Uno Kim / AMEVA Foundation. All rights reserved.
 * SPDX-License-Identifier: Apache-2.0 OR Commercial-License
 */
/**
 * ==============================================================================
 * amv-aichain Memory Engine: ConversationBufferMemory (TypeScript ESM)
 * ==============================================================================
 */
import { Message } from "../core/schema.js";
export declare class ConversationBufferMemory {
    k: number;
    returnMessages: boolean;
    memoryKey: string;
    chatHistory: Message[];
    constructor(options?: {
        k?: number;
        returnMessages?: boolean;
        memoryKey?: string;
    });
    saveContext(inputs: Record<string, any> | string, outputs: Record<string, any> | string): void;
    loadMemoryVariables(): Record<string, any>;
    clear(): void;
}

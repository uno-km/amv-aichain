/**
 * Copyright (c) 2026 Uno Kim / AMEVA Foundation. All rights reserved.
 * SPDX-License-Identifier: Apache-2.0 OR Commercial-License
 */
/**
 * ==============================================================================
 * amv-aichain Core Engine: BitNet 1-Bit LLM Provider Adapter (TypeScript ESM)
 * ==============================================================================
 */
import { OpenAICompatibleChat } from "./openai_compatible.js";
export declare class BitNetChat extends OpenAICompatibleChat {
    constructor(options?: {
        baseUrl?: string;
        model?: string;
        temperature?: number;
        maxTokens?: number;
        timeout?: number;
    });
}

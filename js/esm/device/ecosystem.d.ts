/**
 * Copyright (c) 2026 Uno Kim / AMEVA Foundation. All rights reserved.
 * SPDX-License-Identifier: Apache-2.0 OR Commercial-License
 */
/**
 * ==============================================================================
 * amv-aichain Device Ecosystem: Integrations with uno-km Edge Projects (TS ESM)
 * ==============================================================================
 * Provides standard Tool interfaces for uno-km sovereign edge modules:
 * - amv-bitnet (1.58-bit On-Device LLM)
 * - amv-stt (Speech-to-Text)
 * - amv-diffusion (Device Resource-based Image Generation)
 * - amv-playwright (Headless Browser Automation)
 * - amv-tts (DSP / ONNX Neural & Native Voice Synthesis)
 * - amv-vision (On-Device Computer Vision & VLM Multimodal Engine)
 * Zero external heavy dependencies - Pure Node.js 18+ standard library.
 */
import { Tool } from "../graph/agent.js";
export declare const inferBitnetLlm: Tool;
export declare const transcribeSpeech: Tool;
export declare const generateDiffusionImage: Tool;
export declare const browseWebHeadless: Tool;
export declare const synthesizeSpeech: Tool;
export declare const speakText: Tool;
export declare const analyzeImageVlm: Tool;
export declare const detectFaces: Tool;
export declare const detectEdgesCanny: Tool;
export declare function getEcosystemTools(): Tool[];

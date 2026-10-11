/**
 * Copyright (c) 2026 Uno Kim / AMEVA Foundation. All rights reserved.
 * SPDX-License-Identifier: Apache-2.0 OR Commercial-License
 */
import { Tool } from "../graph/agent.js";
export declare const getBatteryStatus: Tool;
export declare const getSensorData: Tool;
export declare const getDeviceLocation: Tool;
export declare const vibrateDevice: Tool;
export declare const sendNotification: Tool;
export declare const textToSpeech: Tool;
export declare const executeShellCommand: Tool;
export declare function getDefaultDeviceTools(): Tool[];

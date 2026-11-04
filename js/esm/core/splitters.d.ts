/**
 * Copyright (c) 2026 Uno Kim / AMEVA Foundation. All rights reserved.
 * SPDX-License-Identifier: Apache-2.0 OR Commercial-License
 */
/**
 * ==============================================================================
 * amv-aichain Core Text Splitters & Micro Document Loaders
 * ==============================================================================
 */
export interface Document {
    pageContent: string;
    metadata: Record<string, any>;
}
export interface SplitterOptions {
    chunkSize?: number;
    chunkOverlap?: number;
    lengthFunction?: (text: string) => number;
}
export declare class CharacterTextSplitter {
    separator: string;
    chunkSize: number;
    chunkOverlap: number;
    lengthFunction: (text: string) => number;
    constructor(separator?: string, options?: SplitterOptions);
    splitText(text: string): string[];
    private mergeSplits;
}
export declare class RecursiveCharacterTextSplitter {
    separators: string[];
    chunkSize: number;
    chunkOverlap: number;
    lengthFunction: (text: string) => number;
    constructor(options?: SplitterOptions & {
        separators?: string[];
    });
    splitText(text: string): string[];
    private splitRecursive;
    private mergeSplits;
}
export interface BaseLoader {
    load(): Promise<Document[]> | Document[];
}
export declare class TextLoader implements BaseLoader {
    filePath: string;
    encoding: BufferEncoding;
    constructor(filePath: string, encoding?: BufferEncoding);
    load(): Document[];
}
export declare class MarkdownLoader implements BaseLoader {
    filePath: string;
    constructor(filePath: string);
    load(): Document[];
}
export declare class JSONLoader implements BaseLoader {
    filePath: string;
    contentKey?: string;
    constructor(filePath: string, contentKey?: string);
    load(): Document[];
}
export declare class DirectoryLoader implements BaseLoader {
    dirPath: string;
    recursive: boolean;
    silentErrors: boolean;
    loaderCls?: new (filePath: string) => BaseLoader;
    constructor(dirPath: string, options?: {
        recursive?: boolean;
        silentErrors?: boolean;
        loaderCls?: new (filePath: string) => BaseLoader;
    });
    load(): Document[];
    private scanDir;
}
export declare function formatDocs(docs: Document[], separator?: string): string;

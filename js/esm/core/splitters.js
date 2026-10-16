/**
 * Copyright (c) 2026 Uno Kim / AMEVA Foundation. All rights reserved.
 * SPDX-License-Identifier: Apache-2.0 OR Commercial-License
 */
/**
 * ==============================================================================
 * @termux-ai/chain Core Text Splitters & Micro Document Loaders
 * ==============================================================================
 */
import fs from "node:fs";
import path from "node:path";

export class CharacterTextSplitter {
    separator;
    chunkSize;
    chunkOverlap;
    lengthFunction;
    constructor(separator = "\n\n", options = {}) {
        this.separator = separator;
        this.chunkSize = options.chunkSize ?? 1000;
        this.chunkOverlap = options.chunkOverlap ?? 200;
        this.lengthFunction = options.lengthFunction ?? ((t) => t.length);
        if (this.chunkOverlap >= this.chunkSize) {
            throw new Error(`chunkOverlap (${this.chunkOverlap}) must be less than chunkSize (${this.chunkSize})`);
        }
    }
    splitText(text) {
        const splits = this.separator ? text.split(this.separator) : Array.from(text);
        return this.mergeSplits(splits, this.separator);
    }
    mergeSplits(splits, separator) {
        const docs = [];
        const currentDoc = [];
        let totalLen = 0;
        const sepLen = this.lengthFunction(separator);
        for (const s of splits) {
            const sLen = this.lengthFunction(s);
            if (currentDoc.length > 0 && totalLen + sepLen + sLen > this.chunkSize) {
                const merged = currentDoc.join(separator);
                if (merged.trim())
                    docs.push(merged);
                while (currentDoc.length > 0 && totalLen > this.chunkOverlap) {
                    const popped = currentDoc.shift();
                    totalLen -= this.lengthFunction(popped) + sepLen;
                }
            }
            currentDoc.push(s);
            totalLen += sLen + (currentDoc.length > 1 ? sepLen : 0);
        }
        if (currentDoc.length > 0) {
            const merged = currentDoc.join(separator);
            if (merged.trim())
                docs.push(merged);
        }
        return docs;
    }
}
export class RecursiveCharacterTextSplitter {
    separators;
    chunkSize;
    chunkOverlap;
    lengthFunction;
    constructor(options = {}) {
        this.separators = options.separators ?? ["\n\n", "\n", ". ", "? ", "! ", " ", ""];
        this.chunkSize = options.chunkSize ?? 1000;
        this.chunkOverlap = options.chunkOverlap ?? 200;
        this.lengthFunction = options.lengthFunction ?? ((t) => t.length);
    }
    splitText(text) {
        return this.splitRecursive(text, this.separators);
    }
    splitRecursive(text, separators) {
        const finalChunks = [];
        let separator = separators[separators.length - 1];
        let newSeparators = [];
        for (let i = 0; i < separators.length; i++) {
            const s = separators[i];
            if (s === "") {
                separator = "";
                break;
            }
            if (text.includes(s)) {
                separator = s;
                newSeparators = separators.slice(i + 1);
                break;
            }
        }
        const splits = separator ? text.split(separator) : Array.from(text);
        let goodSplits = [];
        for (const s of splits) {
            if (this.lengthFunction(s) < this.chunkSize) {
                goodSplits.push(s);
            }
            else {
                if (goodSplits.length > 0) {
                    finalChunks.push(...this.mergeSplits(goodSplits, separator));
                    goodSplits = [];
                }
                if (newSeparators.length === 0) {
                    finalChunks.push(s);
                }
                else {
                    finalChunks.push(...this.splitRecursive(s, newSeparators));
                }
            }
        }
        if (goodSplits.length > 0) {
            finalChunks.push(...this.mergeSplits(goodSplits, separator));
        }
        return finalChunks;
    }
    mergeSplits(splits, separator) {
        const splitter = new CharacterTextSplitter(separator, {
            chunkSize: this.chunkSize,
            chunkOverlap: this.chunkOverlap,
            lengthFunction: this.lengthFunction
        });
        return splitter.mergeSplits(splits, separator);
    }
}
export class TextLoader {
    filePath;
    encoding;
    constructor(filePath, encoding = "utf-8") {
        this.filePath = filePath;
        this.encoding = encoding;
    }
    load() {
        const content = fs.readFileSync(this.filePath, { encoding: this.encoding });
        return [{
            pageContent: content,
            metadata: { source: this.filePath, filename: path.basename(this.filePath) }
        }];
    }
}
export class MarkdownLoader {
    filePath;
    constructor(filePath) {
        this.filePath = filePath;
    }
    load() {
        const content = fs.readFileSync(this.filePath, "utf-8");
        return [{
            pageContent: content,
            metadata: { source: this.filePath, filename: path.basename(this.filePath), format: "markdown" }
        }];
    }
}
export class JSONLoader {
    filePath;
    contentKey;
    constructor(filePath, contentKey) {
        this.filePath = filePath;
        this.contentKey = contentKey;
    }
    load() {
        const raw = fs.readFileSync(this.filePath, "utf-8");
        const data = JSON.parse(raw);
        const docs = [];
        if (Array.isArray(data)) {
            for (let i = 0; i < data.length; i++) {
                const item = data[i];
                const text = this.contentKey && typeof item === "object" && item !== null && this.contentKey in item
                    ? String(item[this.contentKey])
                    : JSON.stringify(item);
                docs.push({
                    pageContent: text,
                    metadata: { source: this.filePath, filename: path.basename(this.filePath), index: i }
                });
            }
        }
        else if (typeof data === "object" && data !== null) {
            const text = this.contentKey && this.contentKey in data
                ? String(data[this.contentKey])
                : JSON.stringify(data);
            docs.push({
                pageContent: text,
                metadata: { source: this.filePath, filename: path.basename(this.filePath) }
            });
        }
        return docs;
    }
}
export class DirectoryLoader {
    dirPath;
    recursive;
    silentErrors;
    loaderCls;
    static SUPPORTED_TEXT = new Set([
        ".txt", ".log", ".csv", ".py", ".js", ".ts", ".html",
        ".xml", ".yaml", ".yml", ".ini", ".env", ".rst"
    ]);
    constructor(dirPath, options = {}) {
        this.dirPath = dirPath;
        this.recursive = options.recursive ?? true;
        this.silentErrors = options.silentErrors ?? false;
        this.loaderCls = options.loaderCls;
    }
    load() {
        if (!fs.existsSync(this.dirPath)) {
            throw new Error(`Directory not found: ${this.dirPath}`);
        }
        const docs = [];
        this.scanDir(this.dirPath, docs);
        return docs;
    }
    scanDir(currentPath, docs) {
        const entries = fs.readdirSync(currentPath, { withFileTypes: true });
        for (const entry of entries) {
            const fullPath = path.join(currentPath, entry.name);
            if (entry.isDirectory()) {
                if (this.recursive) {
                    this.scanDir(fullPath, docs);
                }
            }
            else if (entry.isFile()) {
                const ext = path.extname(entry.name).toLowerCase();
                try {
                    let loader;
                    if (this.loaderCls) {
                        loader = new this.loaderCls(fullPath);
                    }
                    else if (ext === ".md" || ext === ".markdown") {
                        loader = new MarkdownLoader(fullPath);
                    }
                    else if (ext === ".json") {
                        loader = new JSONLoader(fullPath);
                    }
                    else if (DirectoryLoader.SUPPORTED_TEXT.has(ext)) {
                        loader = new TextLoader(fullPath);
                    }
                    else {
                        continue;
                    }
                    const loaded = loader.load();
                    if (Array.isArray(loaded)) {
                        docs.push(...loaded);
                    }
                }
                catch (err) {
                    if (!this.silentErrors) {
                        throw err;
                    }
                }
            }
        }
    }
}
export function formatDocs(docs, separator = "\n\n") {
    return docs.map(d => d.pageContent).join(separator);
}

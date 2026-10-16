/**
 * Copyright (c) 2026 Uno Kim / AMEVA Foundation. All rights reserved.
 * SPDX-License-Identifier: Apache-2.0 OR Commercial-License
 */
import test from "node:test";
import assert from "node:assert";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

import {
  RunnableLambda,
  RunnablePassthrough,
  RunnableParallel,
  DirectoryLoader,
  TextLoader,
  MarkdownLoader,
  JSONLoader,
  formatDocs,
  MicroVectorStore,
  SparseBM25Embeddings,
} from "../js/esm/index.js";

test("Node.js: RunnablePassthrough and RunnableParallel", async () => {
  const passthrough = new RunnablePassthrough();
  const passRes = await passthrough.invoke("hello termux");
  assert.strictEqual(passRes, "hello termux");

  const parallel = new RunnableParallel({
    upper: (x) => String(x).toUpperCase(),
    len: (x) => String(x).length,
    echo: new RunnablePassthrough(),
  });

  const res = await parallel.invoke("android");
  assert.deepStrictEqual(res, {
    upper: "ANDROID",
    len: 7,
    echo: "android",
  });
});

test("Node.js: DirectoryLoader and formatDocs", () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "aichain-test-"));
  try {
    const subDir = path.join(tmpDir, "nested");
    fs.mkdirSync(subDir, { recursive: true });

    fs.writeFileSync(path.join(tmpDir, "doc1.txt"), "Content of doc1");
    fs.writeFileSync(path.join(subDir, "doc2.md"), "# Heading\nMarkdown content");
    fs.writeFileSync(path.join(subDir, "doc3.json"), JSON.stringify({ note: "json data" }));
    fs.writeFileSync(path.join(subDir, "ignored.bin"), Buffer.from([0, 1, 2]));

    const loader = new DirectoryLoader(tmpDir, { recursive: true });
    const docs = loader.load();

    assert.strictEqual(docs.length, 3);
    const contents = docs.map((d) => d.pageContent);
    assert.ok(contents.some((c) => c.includes("Content of doc1")));
    assert.ok(contents.some((c) => c.includes("Markdown content")));
    assert.ok(contents.some((c) => c.includes("json data")));

    const formatted = formatDocs(docs, " --- ");
    assert.ok(formatted.includes(" --- "));
  } finally {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  }
});

test("Node.js: MicroVectorStore.asRetriever and LCEL RAG Chain", async () => {
  const embedder = new SparseBM25Embeddings({ dimension: 64 });
  const store = new MicroVectorStore({ embeddings: embedder });

  await store.addTexts([
    "AMEVA Sovereign Runtime is designed for mobile edge micro-clusters.",
    "Termux AIChain provides zero-dependency LCEL orchestration on Android.",
    "ARM NEON SIMD accelerates on-device vector mathematics.",
  ]);

  const retriever = store.asRetriever({ k: 2 });
  assert.ok(retriever);

  const ragChain = new RunnableParallel({
    context: retriever.pipe((docs) => formatDocs(docs)),
    question: new RunnablePassthrough(),
  }).pipe((data) => `Q: ${data.question} | Context:\n${data.context}`);

  const output = await ragChain.invoke("What is Termux AIChain?");
  assert.ok(output.includes("Q: What is Termux AIChain?"));
  assert.ok(output.includes("Context:"));
  assert.ok(output.includes("Termux AIChain provides zero-dependency"));
});

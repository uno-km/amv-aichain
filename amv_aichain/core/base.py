# Copyright (c) 2026 Uno Kim / AMEVA Foundation. All rights reserved.
# SPDX-License-Identifier: Apache-2.0 OR Commercial-License
"""
==============================================================================
amv-aichain Core Engine: Runnable Base & Pipe Composition (|)
==============================================================================
Provides standard Runnable, RunnableLambda, RunnableSequence interfaces.
Zero external heavy dependencies - Pure Python 3.10+ standard library.
"""

from __future__ import annotations
import inspect
import asyncio
from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Callable, Dict, Iterator, List, Optional, Union
from amv_aichain.core.schema import Message, HumanMessage, AIMessage, GenerationResult, StreamChunk

class Runnable(ABC):
    """Abstract Base Class for all executable chains, templates, and models."""

    @abstractmethod
    def invoke(self, input_data: Any, **kwargs: Any) -> Any:
        pass

    async def ainvoke(self, input_data: Any, **kwargs: Any) -> Any:
        return await asyncio.to_thread(self.invoke, input_data, **kwargs)

    def stream(self, input_data: Any, **kwargs: Any) -> Iterator[Any]:
        yield self.invoke(input_data, **kwargs)

    async def astream(self, input_data: Any, **kwargs: Any) -> AsyncIterator[Any]:
        yield await self.ainvoke(input_data, **kwargs)

    def __or__(self, other: Union[Runnable, Callable[[Any], Any], Dict[str, Any]]) -> RunnableSequence:
        right = _coerce_runnable(other)
        return RunnableSequence(self, right)

    def __ror__(self, other: Union[Runnable, Callable[[Any], Any], Dict[str, Any]]) -> RunnableSequence:
        left = _coerce_runnable(other)
        return RunnableSequence(left, self)

def _coerce_runnable(obj: Any) -> Runnable:
    """Coerces Runnables, callables, or dictionary mappings into pipe-compatible Runnables."""
    if isinstance(obj, Runnable):
        return obj
    elif isinstance(obj, dict):
        return RunnableParallel(obj)
    elif callable(obj):
        return RunnableLambda(obj)
    raise TypeError(f"Invalid step in sequence: expected Runnable, dict, or callable, got {type(obj)}")

class RunnablePassthrough(Runnable):
    """Passes input through unchanged or assigns calculated keys."""

    def __init__(self, func: Optional[Callable[[Any], Any]] = None):
        self.func = func

    def invoke(self, input_data: Any, **kwargs: Any) -> Any:
        if self.func is not None:
            return self.func(input_data)
        return input_data

    async def ainvoke(self, input_data: Any, **kwargs: Any) -> Any:
        if self.func is not None:
            if inspect.iscoroutinefunction(self.func):
                return await self.func(input_data)
            return await asyncio.to_thread(self.func, input_data)
        return input_data

class RunnableParallel(Runnable):
    """Executes a mapping of Runnables concurrently and aggregates results into a dict."""

    def __init__(
        self,
        steps: Optional[Dict[str, Union[Runnable, Callable[[Any], Any], Any]]] = None,
        **kwargs: Any,
    ):
        merged: Dict[str, Any] = {}
        if steps is not None:
            merged.update(steps)
        if kwargs:
            merged.update(kwargs)
        self.steps = {k: _coerce_runnable(v) for k, v in merged.items()}

    def invoke(self, input_data: Any, **kwargs: Any) -> Dict[str, Any]:
        results: Dict[str, Any] = {}
        for key, runnable in self.steps.items():
            results[key] = runnable.invoke(input_data, **kwargs)
        return results

    async def ainvoke(self, input_data: Any, **kwargs: Any) -> Dict[str, Any]:
        tasks = [runnable.ainvoke(input_data, **kwargs) for runnable in self.steps.values()]
        values = await asyncio.gather(*tasks)
        return dict(zip(self.steps.keys(), values))

class RunnableLambda(Runnable):
    """Wraps any standard Python callable into a pipe-compatible Runnable."""

    def __init__(self, func: Callable[[Any], Any]):
        self.func = func

    def invoke(self, input_data: Any, **kwargs: Any) -> Any:
        if kwargs:
            return self.func(input_data, **kwargs)
        return self.func(input_data)

    async def ainvoke(self, input_data: Any, **kwargs: Any) -> Any:
        if inspect.iscoroutinefunction(self.func):
            return await self.func(input_data, **kwargs)
        return await asyncio.to_thread(self.invoke, input_data, **kwargs)

class RunnableSequence(Runnable):
    """Executes multiple Runnables sequentially in a linear pipe chain."""

    def __init__(self, *steps: Any):
        self.steps: List[Runnable] = []
        for step in steps:
            if isinstance(step, RunnableSequence):
                self.steps.extend(step.steps)
            else:
                self.steps.append(_coerce_runnable(step))

    def invoke(self, input_data: Any, **kwargs: Any) -> Any:
        current = input_data
        for step in self.steps:
            current = step.invoke(current, **kwargs)
        return current

    async def ainvoke(self, input_data: Any, **kwargs: Any) -> Any:
        current = input_data
        for step in self.steps:
            current = await step.ainvoke(current, **kwargs)
        return current

    def stream(self, input_data: Any, **kwargs: Any) -> Iterator[Any]:
        if not self.steps:
            return
        if len(self.steps) == 1:
            yield from self.steps[0].stream(input_data, **kwargs)
            return

        current = input_data
        for step in self.steps[:-1]:
            current = step.invoke(current, **kwargs)

        yield from self.steps[-1].stream(current, **kwargs)

    async def astream(self, input_data: Any, **kwargs: Any) -> AsyncIterator[Any]:
        if not self.steps:
            return
        if len(self.steps) == 1:
            async for chunk in self.steps[0].astream(input_data, **kwargs):
                yield chunk
            return

        current = input_data
        for step in self.steps[:-1]:
            current = await step.ainvoke(current, **kwargs)

        async for chunk in self.steps[-1].astream(current, **kwargs):
            yield chunk

    def __or__(self, other: Union[Runnable, Callable[[Any], Any], Dict[str, Any]]) -> RunnableSequence:
        right = _coerce_runnable(other)
        return RunnableSequence(*self.steps, right)

    def __ror__(self, other: Union[Runnable, Callable[[Any], Any], Dict[str, Any]]) -> RunnableSequence:
        left = _coerce_runnable(other)
        return RunnableSequence(left, *self.steps)

class BaseChatModel(Runnable, ABC):
    """Abstract Base Class for Chat Models."""

    @abstractmethod
    def generate(self, messages: List[Message]) -> GenerationResult:
        pass

    async def agenerate(self, messages: List[Message]) -> GenerationResult:
        return await asyncio.to_thread(self.generate, messages)

    def invoke(self, input_data: Union[str, List[Message], Dict[str, Any]], **kwargs: Any) -> GenerationResult:
        messages = self._coerce_messages(input_data)
        return self.generate(messages)

    async def ainvoke(self, input_data: Union[str, List[Message], Dict[str, Any]], **kwargs: Any) -> GenerationResult:
        messages = self._coerce_messages(input_data)
        return await self.agenerate(messages)

    def _coerce_messages(self, input_data: Union[str, List[Message], Dict[str, Any]]) -> List[Message]:
        if isinstance(input_data, str):
            return [HumanMessage(content=input_data)]
        elif isinstance(input_data, list):
            return input_data
        elif isinstance(input_data, dict):
            if "messages" in input_data:
                return input_data["messages"]
            elif "input" in input_data:
                return [HumanMessage(content=str(input_data["input"]))]
            return [HumanMessage(content=str(input_data))]
        return [HumanMessage(content=str(input_data))]
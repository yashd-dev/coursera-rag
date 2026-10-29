"use client";

import { AuiIf, ThreadPrimitive, useAuiState } from "@assistant-ui/react";
import type { ReactNode } from "react";
import { cn } from "../../../../../../packages/ui/src/lib/utils";

const SUGGESTIONS = [
  {
    label: "Vector RAG systems",
    prompt: "I want to make a paper on vector RAG systems",
  },
  {
    label: "RAG evaluation",
    prompt:
      "I want to make a paper on evaluation methods for retrieval-augmented generation",
  },
  {
    label: "Dense retrieval",
    prompt: "I want to make a paper on dense passage retrieval",
  },
  {
    label: "Chunking strategies",
    prompt:
      "I want to make a paper on chunking strategies for retrieval-augmented generation",
  },
  {
    label: "Hybrid search",
    prompt: "I want to make a paper on hybrid sparse and dense search",
  },
  {
    label: "Approximate nearest neighbors",
    prompt:
      "I want to make a paper on approximate nearest neighbor search for vector databases",
  },
  {
    label: "LLM agents for coding",
    prompt: "I want to make a paper on LLM agents for software engineering",
  },
  {
    label: "Reranking models",
    prompt: "I want to make a paper on neural reranking for retrieval",
  },
  {
    label: "Long-context vs RAG",
    prompt:
      "I want to make a paper on long-context models versus retrieval-augmented generation",
  },
];

const suggestionChipClass =
  "border-foreground/10 bg-background text-muted-foreground hover:border-foreground/25 hover:text-foreground rounded-control h-8 border px-3 text-[13px] transition-colors";

export function Suggestions(): ReactNode {
  const isComposerEmpty = useAuiState((s) => s.composer.isEmpty);

  return (
    // Typing hides the suggestions without unmounting them: the empty view is
    // centred, so collapsing a block this tall moves the composer out from
    // under the cursor. inert keeps the hidden chips out of the tab order.
    <div
      inert={!isComposerEmpty}
      className={cn(
        "animate-in fade-in mx-auto flex max-w-[34rem] flex-wrap items-center justify-center gap-2 transition-opacity duration-200 motion-reduce:animate-none",
        !isComposerEmpty && "opacity-0",
      )}
    >
      {SUGGESTIONS.map((suggestion) => (
        <ThreadPrimitive.Suggestion
          key={suggestion.prompt}
          prompt={suggestion.prompt}
          send
          className={suggestionChipClass}
        >
          {suggestion.label}
        </ThreadPrimitive.Suggestion>
      ))}
    </div>
  );
}

export function FollowUps(): ReactNode {
  const suggestions = useAuiState((s) => s.thread.suggestions);

  return (
    <AuiIf
      condition={(s) =>
        !s.thread.isEmpty &&
        !s.thread.isRunning &&
        s.thread.suggestions.length > 0
      }
    >
      <div className="animate-in fade-in flex [scrollbar-width:none] gap-2 overflow-x-auto duration-200 motion-reduce:animate-none [&::-webkit-scrollbar]:hidden">
        {suggestions.map((suggestion) => (
          <ThreadPrimitive.Suggestion
            key={suggestion.prompt}
            prompt={suggestion.prompt}
            send
            className={cn(suggestionChipClass, "shrink-0 whitespace-nowrap")}
          >
            {suggestion.prompt}
          </ThreadPrimitive.Suggestion>
        ))}
      </div>
    </AuiIf>
  );
}

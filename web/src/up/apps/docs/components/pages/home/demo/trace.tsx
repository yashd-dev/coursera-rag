"use client";

import type { ToolCallMessagePartProps } from "@assistant-ui/react";
import type { ReactNode } from "react";
import { ShimmerLabel } from "../../../../../../packages/ui/src/components/react/assistant-ui/elements/surfaces";
import { CollapsibleTrigger } from "../../../../../../packages/ui/src/components/react/ui/base/collapsible";
import {
  TraceLine,
  TraceMarker,
  formatDuration,
  useToolDuration,
} from "../../../shared/trace-line";

export const disclosureContentClass =
  "border-foreground/10 ms-[5px] border-s ps-4";

export function DisclosureTrigger({
  live,
  label,
  detail,
}: {
  live: boolean;
  label: string;
  detail?: string;
}): ReactNode {
  return (
    <CollapsibleTrigger className="group/trigger my-1 flex max-w-full items-baseline gap-2 text-left font-mono text-[12px] outline-none [font-variant-ligatures:none] focus-visible:underline">
      <TraceMarker
        live={live}
        className="group-data-open/trigger:rotate-90 group-data-panel-open/trigger:rotate-90"
      />
      <span className="text-muted-foreground group-hover/trigger:text-foreground min-w-0 truncate transition-colors">
        {live ? (
          <ShimmerLabel>
            {label}
            {detail ? ` ${detail}` : null}
          </ShimmerLabel>
        ) : (
          <>
            {label}
            {detail ? ` ${detail}` : null}
          </>
        )}
      </span>
    </CollapsibleTrigger>
  );
}

export function ToolCall({
  toolName,
  args,
  status,
  result,
}: ToolCallMessagePartProps): ReactNode {
  const isRunning = status?.type === "running";
  const duration = useToolDuration(isRunning);
  const searchQuery =
    toolName === "search_docs" && typeof args.query === "string"
      ? args.query
      : undefined;

  return (
    <details className="my-2 text-sm text-muted-foreground">
      <summary className="cursor-pointer">
        <TraceLine
          live={isRunning}
          label={
            searchQuery !== undefined
              ? isRunning
                ? "searching"
                : "searched"
              : isRunning
                ? "running"
                : "ran"
          }
          detail={
            searchQuery !== undefined
              ? `the docs for “${searchQuery}”`
              : toolName
          }
          {...(duration !== null ? { meta: formatDuration(duration) } : {})}
        />
      </summary>
      {result !== undefined && (
        <pre className="mt-2 max-h-80 overflow-auto whitespace-pre-wrap break-words rounded-lg border p-3 text-xs">
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </details>
  );
}

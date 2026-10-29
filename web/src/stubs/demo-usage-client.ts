export const refreshDemoUsage = () => {};
export const useDemoUsage = () => ({
  status: "ready" as const,
  usage: {
    remaining: 1_000_000,
    limit: 1_000_000,
    resetAt: 0,
    signedIn: false,
  },
});

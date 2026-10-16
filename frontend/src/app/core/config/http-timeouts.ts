export const HTTP_TIMEOUT_MS = {
  health: 5_000,
  simulatorBase: 15_000,
  simulatorScenario: 20_000,
  simulatorComparison: 30_000,
  simulatorOptimizer: 45_000,
  processualChat: 120_000,
} as const;

const noop = () => {};
export const analytics: any = new Proxy(
  {},
  { get: () => new Proxy({}, { get: () => noop }) },
);

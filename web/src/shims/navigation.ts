export const useRouter = () => ({
  push: (u: string) => (location.href = u),
  replace: (u: string) => location.replace(u),
  refresh() {},
  back: () => history.back(),
  prefetch() {},
});
export const usePathname = () => location.pathname;
export const useSearchParams = () => new URLSearchParams(location.search);
export const notFound = () => {
  throw new Error("not found");
};

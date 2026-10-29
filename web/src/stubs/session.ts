export type SessionUser = {
  name?: string | null;
  email?: string | null;
  image?: string | null;
};
export function useSession(): {
  data: { user: SessionUser } | null;
  isPending: boolean;
} {
  return { data: null, isPending: false };
}

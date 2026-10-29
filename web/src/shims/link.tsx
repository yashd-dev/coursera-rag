import type { AnchorHTMLAttributes } from "react";
export default function Link({
  href,
  prefetch: _p,
  ...rest
}: AnchorHTMLAttributes<HTMLAnchorElement> & { href: string; prefetch?: any }) {
  return <a href={href} {...rest} />;
}

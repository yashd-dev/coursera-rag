export default function Image({
  src,
  alt,
  fill: _f,
  priority: _p,
  ...rest
}: any) {
  return (
    <img src={typeof src === "string" ? src : src?.src} alt={alt} {...rest} />
  );
}

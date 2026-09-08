import { useEffect, useState } from "react";

/** Image that degrades to a labelled placeholder instead of breaking layout.
 *  Failed preview loading never blocks the surrounding workflow. */
export function SafeImage({
  src,
  alt,
  className
}: {
  src: string;
  alt: string;
  className?: string;
}): JSX.Element {
  const [failed, setFailed] = useState(false);
  useEffect(() => setFailed(false), [src]);
  if (failed) {
    return (
      <div
        className={className}
        role="img"
        aria-label={`${alt} — preview unavailable`}
        style={{
          background: "#0f1a17",
          color: "#f5f4ef",
          borderRadius: 6,
          padding: "28px 16px",
          textAlign: "center",
          fontSize: 13
        }}
      >
        Preview unavailable. The source image could not be loaded.
      </div>
    );
  }
  return <img src={src} alt={alt} className={className} onError={() => setFailed(true)} />;
}

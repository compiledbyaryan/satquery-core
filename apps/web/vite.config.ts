import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Combined-host intent: landing at `/`, workbench at `/app/`.
// Build base is `/app/` so the same bundle mounts under `/app/`.
// Dev serving stays at `/`; the router detects `/app` prefix at runtime.
export default defineConfig({
  plugins: [react()],
  base: "/app/",
  server: { port: 5173, strictPort: true },
  preview: { port: 4173, strictPort: true },
  build: { outDir: "dist", sourcemap: false, chunkSizeWarningLimit: 600 }
});

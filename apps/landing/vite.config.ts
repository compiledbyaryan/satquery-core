import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Landing mounts at `/` on a combined host. Independent manifest/lock/build.
export default defineConfig({
  plugins: [react()],
  base: "/",
  server: { port: 5174, strictPort: true },
  preview: { port: 4174, strictPort: true },
  build: { outDir: "dist", sourcemap: false }
});

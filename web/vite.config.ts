import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwind from "@tailwindcss/vite";
import path from "node:path";
const s = (p: string) => path.resolve(__dirname, "src/shims", p);
export default defineConfig({
  plugins: [react(), tailwind()],
  resolve: {
    alias: {
      "next/link": s("link.tsx"),
      "next/navigation": s("navigation.ts"),
      "next/image": s("image.tsx"),
      "next/dynamic": s("dynamic.tsx"),
    },
  },
  server: {
    host: "127.0.0.1",
    port: 5173,
    proxy: { "/api": { target: "http://127.0.0.1:8000", changeOrigin: true } },
  },
});

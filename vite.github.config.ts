import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  root: "cloudflare",
  base: "/racelive-ranking/",
  publicDir: "../public",
  plugins: [react()],
  build: {
    outDir: "../github-pages-dist",
    emptyOutDir: true,
  },
});

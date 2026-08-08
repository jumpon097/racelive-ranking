import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  root: "cloudflare",
  publicDir: "../public",
  plugins: [react()],
  build: {
    outDir: "../cloudflare-dist",
    emptyOutDir: true,
  },
});

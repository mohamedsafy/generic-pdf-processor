import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: { proxy: { "/upload-pdf/": "http://generic-pdf-processor:4000/" },
watch: {
      usePolling: true,
    } },
});

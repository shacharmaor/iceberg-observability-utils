import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// In dev, /api goes to a locally running UI Backend; in production nginx does the same proxying.
export default defineConfig({
  plugins: [react()],
  server: { proxy: { "/api": process.env.ICEOBS_UI_BACKEND ?? "http://localhost:8000" } },
});

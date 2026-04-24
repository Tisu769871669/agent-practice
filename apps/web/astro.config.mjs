import { defineConfig } from "astro/config";

export default defineConfig({
  base: process.env.PUBLIC_BASE_PATH || "/",
  server: {
    host: true,
    port: 4321,
  },
  output: "static",
});

import { defineConfig } from "astro/config";

// GitHub Pages URL: https://n24q02m.github.io/system-craft
export default defineConfig({
  site: "https://n24q02m.github.io",
  base: "/system-craft",
  trailingSlash: "always",
  markdown: {
    shikiConfig: {
      themes: { light: "github-light", dark: "github-dark" },
      wrap: true,
    },
  },
  build: {
    format: "directory",
  },
});

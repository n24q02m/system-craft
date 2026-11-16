import { defineConfig } from "astro/config";

// Site chạy trên GitHub Pages tại https://n24q02m.github.io/engineering-lessons
export default defineConfig({
  site: "https://n24q02m.github.io",
  base: "/engineering-lessons",
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

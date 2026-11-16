import { defineConfig } from "astro/config";
import rehypeSystemCraft from "./src/plugins/rehype-system-craft.mjs";

// GitHub Pages URL: https://n24q02m.github.io/system-craft
export default defineConfig({
  site: "https://n24q02m.github.io",
  base: "/system-craft",
  trailingSlash: "always",
  markdown: {
    rehypePlugins: [rehypeSystemCraft],
    shikiConfig: {
      themes: { light: "github-light", dark: "github-dark" },
      wrap: true,
    },
  },
  build: {
    format: "directory",
  },
});

import { defineCollection, z } from "astro:content";
import { glob } from "astro/loaders";

const blog = defineCollection({
  loader: glob({ base: "../content/cases", pattern: "**/*.md" }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    lang: z.enum(["vi", "en"]).default("vi"),
    order: z.number(),
    field: z.string(),
    topics: z.array(z.string()).default([]),
    draft: z.boolean().default(false),
  }),
});

const book = defineCollection({
  loader: glob({
    base: "../content/book",
    pattern: "*.md",
    generateId: ({ entry }) => entry.replace(/\.md$/, ""),
  }),
  schema: z.object({}).passthrough(),
});

export const collections = { blog, book };

import { defineCollection, z } from "astro:content";
import { glob } from "astro/loaders";

const blog = defineCollection({
  loader: glob({ base: "./src/content/blog", pattern: "**/*.md" }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    lang: z.enum(["vi", "en"]).default("vi"),
    order: z.number(),
    field: z.string(),
    // Các khái niệm kỹ thuật bài này bàn tới, hiện ở đầu bài.
    topics: z.array(z.string()).default([]),
    draft: z.boolean().default(false),
  }),
});

export const collections = { blog };

import fs from "node:fs";
import path from "node:path";

for (const rel of [".astro", "node_modules/.astro"]) {
  fs.rmSync(path.resolve(process.cwd(), rel), { recursive: true, force: true });
}

// Bundles src/entry.ts with Recordly's files (recordly/src) and pixi into dist/navi-polish.js. Uses the Vite that
// the recorder already has (recorder/agent-screenplay/node_modules), so nothing extra is installed.
import path from "node:path"; import { execFileSync } from "node:child_process";
const HERE = path.dirname(new URL(import.meta.url).pathname);
execFileSync(process.execPath, [path.join(HERE, "check-recordly.mjs")], { stdio: "inherit" });  // refuses edited Recordly files
const { build } = await import(path.join(HERE, "..", "agent-screenplay", "node_modules", "vite", "dist", "node", "index.js"));
await build({
  configFile: false, root: HERE, logLevel: "warn",
  resolve: { alias: [
    { find: /^@\//, replacement: path.join(HERE, "recordly", "src") + "/" },
    { find: /^web-demuxer$/, replacement: path.join(HERE, "src", "web-demuxer-stub.ts") },
  ] },
  build: {
    outDir: path.join(HERE, "dist"), emptyOutDir: true, assetsInlineLimit: 1e8, minify: false, reportCompressedSize: false,
    lib: { entry: path.join(HERE, "src", "entry.ts"), formats: ["es"], fileName: () => "navi-polish.js" },
  },
});
console.log("built dist/navi-polish.js");

import {build} from "esbuild";

// Use the bundler already installed with Angular to run TypeScript tests in Node.
const result = await build({
  entryPoints: ["test/index.ts"],
  bundle: true,
  write: false,
  platform: "node",
  format: "esm",
});
await import(
  "data:text/javascript;base64," +
    Buffer.from(
      result.outputFiles[0].text + "\n//# sourceURL=adh6-tests.mjs",
    ).toString("base64")
);

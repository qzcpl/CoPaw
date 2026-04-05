import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  // Empty = same-origin; frontend and backend served together, no hardcoded host.
  // Use a dedicated Vite-prefixed key so unrelated shell BASE_URL values don't leak into the build.
  const apiBaseUrl = env.VITE_API_BASE_URL ?? "";

  return {
    define: {
      VITE_API_BASE_URL: JSON.stringify(apiBaseUrl),
      TOKEN: JSON.stringify(env.TOKEN || ""),
      MOBILE: false,
    },
    plugins: [react()],
    css: {
      modules: {
        localsConvention: "camelCase",
        generateScopedName: "[name]__[local]__[hash:base64:5]",
      },
      preprocessorOptions: {
        less: {
          javascriptEnabled: true,
        },
      },
    },
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./src"),
      },
    },
    server: {
      host: "0.0.0.0",
      port: 5173,
    },
    optimizeDeps: {
      include: [
        "diff",
        "react-syntax-highlighter",
        "react-syntax-highlighter/dist/esm/languages/prism/markdown",
        "react-syntax-highlighter/dist/esm/languages/prism/javascript",
        "react-syntax-highlighter/dist/esm/languages/prism/python",
        "react-syntax-highlighter/dist/esm/languages/prism/typescript",
        "react-syntax-highlighter/dist/esm/languages/prism/json",
        "react-syntax-highlighter/dist/esm/languages/prism/bash",
        "react-syntax-highlighter/dist/esm/languages/prism/yaml",
      ],
    },
    // build: {
    //   // Output to CoPaw's console directory,
    //   // so we don't need to copy files manually after build.
    //   outDir: path.resolve(__dirname, "../src/copaw/console"),
    //   emptyOutDir: true,
    // },
  };
});

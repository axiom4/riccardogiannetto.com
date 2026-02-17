// @ts-check
const eslint = require("@eslint/js");
const { defineConfig } = require("eslint/config");
const tseslint = require("typescript-eslint");

module.exports = defineConfig([
  {
    ignores: ["src/app/modules/core/api/v1/**/*", ".angular/**/*"],
  },
  {
    files: ["**/*.ts"],
    extends: [
      eslint.configs.recommended,
      tseslint.configs.recommended,
      tseslint.configs.stylistic,
    ],
    rules: {},
  },
]);

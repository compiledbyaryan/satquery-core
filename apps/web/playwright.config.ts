import type { PlaywrightTestConfig } from "@playwright/test";

// Reserved check: run only after `npm run build` + `npm run preview`.
// Not executed in this handoff (browser tooling unrun — see docs/handoffs/ui.md).
const config: PlaywrightTestConfig = {
  testDir: "./e2e",
  use: { baseURL: "http://localhost:4173/app/", trace: "retain-on-failure" }
};
export default config;

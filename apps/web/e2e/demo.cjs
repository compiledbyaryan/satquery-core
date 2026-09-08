// Run against both built preview servers. Uses an installed Playwright runtime.
const { chromium } = require("playwright");
const assert = require("node:assert/strict");
const fs = require("node:fs/promises");
const path = require("node:path");
const { createHash } = require("node:crypto");
const root = path.resolve(__dirname, "../../..");
const output = process.env.SATQUERY_EVIDENCE_DIR || "/tmp/satquery-demo-verification";
const web = "http://localhost:4173/app";
const landing = "http://localhost:4174/";
const checks = [];
const check = (name, value) => { assert.ok(value, name); checks.push(name); console.log(`PASS ${name}`); };
(async () => {
  await fs.mkdir(output, { recursive: true });
  const browser = await chromium.launch({ headless: true });
  try {
    const ctx = await browser.newContext({ viewport: { width:1440, height:900 }, acceptDownloads:true });
    const page = await ctx.newPage();
    const errors = [];
    page.on("pageerror", e => errors.push(e.message));
    await page.goto(`${web}/projects/proj-delta`);
    const run = () => page.getByRole("button", { name:"Run example", exact:true }).click();
    const result = () => page.getByRole("button", { name:/View evidence/ }).waitFor({ state:"visible", timeout:5000 });
    await run();
    check("submission disables duplicate action", await page.getByRole("button", { name:/Simulating example/ }).isDisabled());
    await result();
    check("submission reaches supplied success", await page.getByText("succeeded", {exact:true}).isVisible());
    const reportHref = await page.getByRole("link", {name:"Export this result"}).getAttribute("href");
    await page.getByRole("button", {name:/View evidence/}).click();
    check("evidence binds selected after source", (await page.getByRole("dialog").innerText()).includes("asset-opt-after"));
    await page.screenshot({path:path.join(output,"workspace-evidence.png"),fullPage:true});
    await page.keyboard.press("Escape");
    check("Escape dismisses and restores focus", await page.getByRole("dialog").count() === 0 && await page.evaluate(() => document.activeElement.textContent.includes("View evidence")));
    await page.reload(); await result();
    check("refresh preserves exact completed run", await page.getByRole("link", {name:"Export this result"}).getAttribute("href") === reportHref);
    await page.getByRole("link", {name:"Export this result"}).click();
    const downloadWait = page.waitForEvent("download");
    await page.getByRole("button", {name:"Download manifest (JSON)"}).click();
    const download = await downloadWait;
    const manifest = JSON.parse(await fs.readFile(await download.path(),"utf8"));
    check("download is for displayed run and input", reportHref.endsWith(manifest.runId) && manifest.inputs.length===2 && manifest.claims[0].sourceAssetId==="asset-opt-after");
    await page.goBack(); await result();
    await page.getByRole("button", {name:"Inputs · 2",exact:true}).click();
    await page.getByRole("button", {name:"Selected as after",exact:true}).click();
    check("input change clears stale result and viewer", await page.getByRole("button",{name:/View evidence/}).count()===0 && await page.getByRole("img",{name:"After synthetic preview",exact:true}).count()===0);
    await run();
    check("missing input is actionable", (await page.getByRole("alert").innerText()).includes("both before and after"));
    await page.getByRole("button", {name:"Use as after",exact:true}).click();
    await page.getByRole("button", {name:"Inputs · 2",exact:true}).click();
    await run(); await page.getByRole("button", {name:"Reset run"}).click();
    await page.waitForTimeout(1300);
    check("reset cancels pending completion", await page.getByText("empty",{exact:true}).isVisible() && await page.getByRole("button",{name:/View evidence/}).count()===0);
    await run(); await result();
    check("second submission completes independently", await page.getByRole("link",{name:"Export this result"}).getAttribute("href")!==reportHref);
    await page.getByRole("combobox",{name:"Example question"}).selectOption({label:"Optical + SAR · partial"}); await run(); await result();
    check("paired fixture reaches partial", await page.getByText("partial",{exact:true}).isVisible());
    for (const [label, expected] of [["Caption · unavailable","Live captioning is unavailable"],["Tool failure · simulated","Simulated TOOL_ERROR"]]) {
      await page.getByRole("combobox",{name:"Example question"}).selectOption({label}); await run();
      check(label, (await page.getByRole("alert").innerText()).includes(expected));
    }
    await page.getByRole("textbox",{name:"Ask about this observation"}).fill("How many cars are there?"); await run();
    check("arbitrary question refused", (await page.getByRole("alert").innerText()).includes("Unsupported question"));
    await page.getByRole("button",{name:"Use change example"}).click(); await run(); await result();
    check("recovery reaches another result", await page.getByText("succeeded",{exact:true}).isVisible());
    await page.getByRole("link",{name:"Recorded run",exact:true}).click();
    await page.getByRole("heading",{name:"Caption (verbatim model output)"}).waitFor();
    const originalBytes = await fs.readFile(path.join(root,"docs/handoffs/recorded-run-01/recorded-run.json"));
    const original = JSON.parse(originalBytes);
    check("recorded caption and human review unchanged", (await page.getByRole("region",{name:"Recorded caption",exact:true}).innerText()).includes(original.invocations[0].output) && (await page.getByRole("region",{name:"Human review",exact:true}).innerText()).includes(original.human_review_note));
    check("benchmark displayed at native resolution", await page.getByRole("img",{name:/Recorded EuroSAT/}).evaluate(el => el.naturalWidth===64 && el.clientWidth===64 && el.clientHeight===64));
    const recordedDownload = page.waitForEvent("download");
    await page.getByRole("link",{name:"Download run JSON"}).click();
    const recordBytes = await fs.readFile(await (await recordedDownload).path());
    check("recorded download byte-for-byte faithful", originalBytes.equals(recordBytes));
    const publicImage = await fs.readFile(path.join(root,"apps/web/public/recorded/recorded-run-01/recorded_sample_01.png"));
    check("recorded source hash unchanged", createHash("sha256").update(publicImage).digest("hex")===original.input.sha256);
    await page.screenshot({path:path.join(output,"recorded.png"),fullPage:true});
    await page.goto(landing);
    await page.getByRole("link",{name:"Open workspace"}).click();
    await page.waitForURL(`${web}/projects/proj-delta`);
    await page.reload(); await page.getByRole("heading",{name:"River corridor"}).waitFor();
    check("landing click-through and direct refresh", page.url()===`${web}/projects/proj-delta`);
    await page.goBack(); check("back reaches landing", page.url()===landing);
    await page.goForward(); check("forward reaches workbench", page.url()===`${web}/projects/proj-delta`);
    check("no browser exceptions", errors.length===0);
    await ctx.close();
    for (const width of [1440,1024,390]) {
      const responsive = await browser.newContext({viewport:{width,height:width===390?844:900},reducedMotion:"reduce"});
      const p=await responsive.newPage();
      for (const [name,url] of [["workspace",`${web}/projects/proj-delta`],["landing",landing],["recorded",`${web}/recorded/run-01`]]) {
        await p.goto(url);
        if(name==="workspace") { await p.getByRole("button",{name:"Run example",exact:true}).click(); await p.getByRole("button",{name:/View evidence/}).waitFor(); }
        if(name==="recorded") await p.getByRole("heading",{name:"Caption (verbatim model output)"}).waitFor();
        check(`${name} ${width}px no overflow`,await p.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth));
        check(`${name} ${width}px reduced motion`,await p.evaluate(()=>[...document.querySelectorAll("*")].every(el=>getComputedStyle(el).animationName==="none")));
        if(name!=="recorded" || width===390) await p.screenshot({path:path.join(output,`${name}-${width}.png`),fullPage:true});
      }
      await p.goto(`${web}/projects/proj-delta`); await p.keyboard.press("Tab");
      check(`keyboard focus ${width}px`,await p.evaluate(()=>document.activeElement.textContent.includes("Skip to main") && getComputedStyle(document.activeElement).outlineStyle!=="none"));
      await responsive.close();
    }
    // Static record failure is bounded and retry can recover without an imitation analysis.
    const failCtx=await browser.newContext(); const failPage=await failCtx.newPage();
    await failPage.route("**/recorded-run.json",route=>route.abort());
    await failPage.goto(`${web}/recorded/run-01`);
    await failPage.getByRole("button",{name:"Retry loading record"}).waitFor();
    check("record load failure offers retry",await failPage.getByRole("alert").isVisible());
    await failPage.unroute("**/recorded-run.json");
    await failPage.getByRole("button",{name:"Retry loading record"}).click();
    await failPage.getByRole("heading",{name:"Caption (verbatim model output)"}).waitFor();
    check("record retry recovers",await failPage.getByRole("link",{name:"Download run JSON"}).isVisible());
    await failCtx.close();
    await fs.writeFile(path.join(output,"results.json"),JSON.stringify({checks,passed:checks.length},null,2));
    console.log(`Completed ${checks.length} browser checks. Evidence: ${output}`);
  } finally { await browser.close(); }
})().catch(error=>{console.error(error);process.exitCode=1;});

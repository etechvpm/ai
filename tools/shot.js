// Screenshot the built site for visual QA.
//   node tools/shot.js http://127.0.0.1:PORT/page.html out.png [full] [dark]
const puppeteer = require("/tmp/rend/node_modules/puppeteer");

(async () => {
  const [url, out, full, dark] = [process.argv[2], process.argv[3],
    process.argv[4] === "full", process.argv[5] === "dark"];
  const browser = await puppeteer.launch({
    args: ["--no-sandbox", "--disable-setuid-sandbox", "--font-render-hinting=none"],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1500, height: 1000, deviceScaleFactor: 1.5 });
  page.on("console", (m) => { if (m.type() === "error") console.log("CONSOLE ERR:", m.text()); });
  page.on("pageerror", (e) => console.log("PAGE ERR:", e.message));
  page.on("requestfailed", (r) => console.log("REQ FAIL:", r.url()));
  await page.goto(url, { waitUntil: "networkidle0", timeout: 30000 });
  if (dark) await page.evaluate(() => document.documentElement.setAttribute("data-theme", "dark"));
  await new Promise((r) => setTimeout(r, 400));
  await page.screenshot({ path: out, fullPage: full });
  console.log("shot:", out);
  await browser.close();
})();

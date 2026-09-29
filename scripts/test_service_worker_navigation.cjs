"use strict";
// Simulate browser service-worker fetch events to prevent incorrect offline routes.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const source = fs.readFileSync("service-worker.js", "utf8");
const listeners = {};
const stores = new Map();
let networkWorks = false;

function urlFor(req) {
  return new URL(typeof req === "string" ? req : req.url, "https://ragunauthramsaroop.com").href;
}
function makeCache(store) {
  return {
    async add(req) {
      const url = urlFor(req);
      const type = url.endsWith(".css") ? "text/css" : url.endsWith(".js") ? "application/javascript" : url.endsWith(".png") ? "image/png" : "text/html";
      store.set(url, new Response("Precached: " + url, { headers: { "Content-Type": type } }));
    },
    async match(req, options = {}) {
      const target = urlFor(req);
      let found = store.get(target);
      if (!found && options.ignoreSearch) {
        found = [...store.entries()].find(([key]) => new URL(key).pathname === new URL(target).pathname)?.[1];
      }
      return found?.clone();
    },
    async put(req, response) { store.set(urlFor(req), response.clone()); },
    async keys() { return [...store.keys()].map(url => ({ url })); },
    async delete(req) { return store.delete(urlFor(req)); }
  };
}
const cacheAPI = {
  async open(name) {
    if (!stores.has(name)) stores.set(name, new Map());
    return makeCache(stores.get(name));
  },
  async keys() { return [...stores.keys()]; },
  async delete(name) { return stores.delete(name); }
};
const fakeSelf = {
  location: { origin: "https://ragunauthramsaroop.com" },
  addEventListener(name, callback) { listeners[name] = callback; },
  async skipWaiting() {},
  clients: { async claim() {} }
};
vm.runInNewContext(source, {
  self: fakeSelf, caches: cacheAPI, URL, Response, Promise,
  async fetch(req) {
    if (!networkWorks) throw Error("Simulated TLS/network failure");
    return new Response("Correct GIS page for " + urlFor(req), {
      headers: { "Content-Type": "text/html" }
    });
  }
}, { filename: "service-worker.js" });

async function eventFor(handler, request) {
  const background = [];
  let output;
  const ev = {
    request,
    waitUntil(p) { background.push(Promise.resolve(p)); },
    respondWith(p) { output = Promise.resolve(p); }
  };
  handler(ev);
  const response = await output;
  await Promise.all(background);
  return response;
}

(async () => {
  assert.ok(source.includes('const V="rr-public-v11"'), "Version should replace v10");
  stores.set("rr-public-v10", new Map());
  stores.set("some-other-app", new Map());
  const installWork = [];
  listeners.install({ waitUntil(p) { installWork.push(Promise.resolve(p)); } });
  await Promise.all(installWork);
  const activateWork = [];
  listeners.activate({ waitUntil(p) { activateWork.push(Promise.resolve(p)); } });
  await Promise.all(activateWork);
  assert.equal(stores.has("rr-public-v10"), false, "Retire old caches on upgrade");
  assert.equal(stores.has("some-other-app"), true, "Never delete unrelated caches");
  const cache = await cacheAPI.open("rr-public-v11");
  assert.ok(await cache.match("/start/"), "Start page should remain available offline");
  assert.ok(await cache.match("/assets/home.css"), "Homepage CSS should remain available offline");
  assert.ok(await cache.match("/assets/accessibility.css"), "Accessibility CSS should remain available offline");
  assert.ok(await cache.match("/assets/site.css"), "Primary site CSS should remain available offline");
  assert.ok(await cache.match("/tools/assets/tools.css"), "Critical tools CSS should work offline");

  const geo = { url: "https://ragunauthramsaroop.com/tools/geolibre/", mode: "navigate", method: "GET" };
  let page = await eventFor(listeners.fetch, geo);
  assert.equal(page.status, 503, "A failed GIS request must be an explicit offline error");
  assert.match(await page.text(), /Connection unavailable/);
  assert.equal(page.headers.get("Cache-Control"), "no-store");

  networkWorks = true;
  page = await eventFor(listeners.fetch, geo);
  assert.equal(page.status, 200, "Successful requests must return the requested page");
  assert.match(await page.text(), /Correct GIS page/);

  networkWorks = false;
  page = await eventFor(listeners.fetch, {
    ...geo, url: geo.url + "?reconnect=1"
  });
  assert.equal(page.status, 200, "Previously visited exact page should work offline");
  assert.match(await page.text(), /Correct GIS page/);

  const unknown = await eventFor(listeners.fetch, {
    url: "https://ragunauthramsaroop.com/not-visited/", mode: "navigate", method: "GET"
  });
  assert.equal(unknown.status, 503, "No unrelated offline page substitution");
  assert.doesNotMatch(await unknown.text(), /What brought you here/);
  const css = await eventFor(listeners.fetch, {
    url: "https://ragunauthramsaroop.com/tools/assets/tools.css",
    mode: "same-origin", method: "GET"
  });
  assert.equal(css.status, 200, "CSS remains cached during offline failures");
  console.log("PASS: offline route integrity, TLS failure fallback, critical CSS, cache migration, query handling");
})().catch(err => { console.error(err); process.exitCode = 1; });

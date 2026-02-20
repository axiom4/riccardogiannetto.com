const fs = require("fs");
const path = require("path");
const crypto = require("crypto");
const cheerio = require("cheerio");

// Adjust the dist folder location
// Based on angular.json, the output path is dist/rg_web
const BASE_DIST = path.join(__dirname, "../dist/rg_web");

// Try to find index.html in either browser/ or root
let INDEX_PATH = path.join(BASE_DIST, "browser", "index.html");
if (!fs.existsSync(INDEX_PATH)) {
  INDEX_PATH = path.join(BASE_DIST, "index.html");
  if (!fs.existsSync(INDEX_PATH)) {
    console.error(
      `Error: Cannot find index.html in ${BASE_DIST} or ${path.join(BASE_DIST, "browser")}. Did you run 'ng build'?`,
    );
    process.exit(1);
  }
}

console.log(`Processing SRI for: ${INDEX_PATH}`);
const html = fs.readFileSync(INDEX_PATH, "utf8");
const $ = cheerio.load(html);

function generateIntegrity(filePath) {
  if (!fs.existsSync(filePath)) {
    return null;
  }
  const fileBuffer = fs.readFileSync(filePath);
  const hash = crypto.createHash("sha384").update(fileBuffer).digest("base64");
  return `sha384-${hash}`;
}

const distRoot = path.dirname(INDEX_PATH);

// Process JS scripts
$("script").each((i, elem) => {
  const src = $(elem).attr("src");
  if (src && !src.startsWith("http") && !src.startsWith("//")) {
    // Only local files
    // Clean query params if any
    const cleanSrc = src.split("?")[0];
    const fullPath = path.join(distRoot, cleanSrc);

    if (fs.existsSync(fullPath)) {
      const integrity = generateIntegrity(fullPath);
      if (integrity) {
        $(elem).attr("integrity", integrity);
        $(elem).attr("crossorigin", "anonymous");
      }
    } else {
      console.warn(`Warning: Script file not found: ${fullPath}`);
    }
  }
});

// Process CSS stylesheets
$('link[rel="stylesheet"], link[rel="modulepreload"]').each((i, elem) => {
  const href = $(elem).attr("href");
  if (href && !href.startsWith("http") && !href.startsWith("//")) {
    // Only local files
    const cleanHref = href.split("?")[0];
    const fullPath = path.join(distRoot, cleanHref);

    if (fs.existsSync(fullPath)) {
      const integrity = generateIntegrity(fullPath);
      if (integrity) {
        $(elem).attr("integrity", integrity);
        if ($(elem).attr("rel") === "stylesheet") {
          $(elem).attr("crossorigin", "anonymous");
        }
        // For modulepreload, crossorigin is usually implicit or 'anonymous' is fine,
        // but strict SRI often requires matching CORS settings.
        // Angular usually emits modulepreload without crossorigin,
        // but if we add integrity, we must add crossorigin='anonymous' to avoid fetch errors.
        if (!$(elem).attr("crossorigin")) {
          $(elem).attr("crossorigin", "anonymous");
        }
      }
    } else {
      console.warn(`Warning: Resource file not found: ${fullPath}`);
    }
  }
});

fs.writeFileSync(INDEX_PATH, $.html(), "utf8");
console.log("SRI hashes added successfully to index.html");

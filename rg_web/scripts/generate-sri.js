const fs = require("fs");
const path = require("path");
const crypto = require("crypto");
const cheerio = require("cheerio");
const esbuild = require("esbuild");

// Adjust the dist folder location
// Based on angular.json, the output path is dist/rg_web
const BASE_DIST = path.join(__dirname, "../dist/rg_web");

// Try to find index.html in either browser/ or root
let INDEX_PATH = path.join(BASE_DIST, "browser", "index.html");
let DIST_ROOT = path.join(BASE_DIST, "browser");

if (!fs.existsSync(INDEX_PATH)) {
  INDEX_PATH = path.join(BASE_DIST, "index.html");
  DIST_ROOT = BASE_DIST;
  if (!fs.existsSync(INDEX_PATH)) {
    console.error(
      `Error: Cannot find index.html in ${BASE_DIST} or ${path.join(BASE_DIST, "browser")}. Did you run 'ng build'?`,
    );
    process.exit(1);
  }
}

// --- Sanitize JS Files (Remove console.log) ---
function sanitizeFile(filePath) {
  if (!fs.existsSync(filePath)) return;
  const content = fs.readFileSync(filePath, "utf8");

  // Use esbuild to safely remove console logs and minify
  try {
    const result = esbuild.transformSync(content, {
      minify: true,
      drop: ["console", "debugger"],
      legalComments: "none",
      treeShaking: true,
      format: "esm", // Assuming usage of ESM modules for Angular outputs (default for modern builds)
    });

    if (result.code !== content) {
      console.log(
        `Sanitized ${path.basename(filePath)} (removed logs/unnecessary code)`,
      );
      fs.writeFileSync(filePath, result.code, "utf8");
    }
  } catch (err) {
    console.error(`Error sanitizing ${path.basename(filePath)}:`, err.message);
    // Don't fail the build, just warn
  }
}

// Sanitize all JS files in DIST_ROOT before processing
try {
  const jsFiles = fs.readdirSync(DIST_ROOT).filter((f) => f.endsWith(".js"));
  jsFiles.forEach((file) => {
    sanitizeFile(path.join(DIST_ROOT, file));
  });
} catch (err) {
  console.warn("Warning: Could not list files for sanitization:", err);
}

console.log(`Processing SRI for: ${INDEX_PATH}`);
const html = fs.readFileSync(INDEX_PATH, "utf8");
const $ = cheerio.load(html);

function generateIntegrity(filePath) {
  try {
    const fileBuffer = fs.readFileSync(filePath);
    const hash = crypto
      .createHash("sha384")
      .update(fileBuffer)
      .digest("base64");
    return `sha384-${hash}`;
  } catch (err) {
    if (err.code === "ENOENT") {
      return null;
    }
    throw err;
  }
}

// Track referenced files from index.html
const referencedFiles = new Set();

// Process JS scripts in index.html
$("script").each((i, elem) => {
  const src = $(elem).attr("src");
  if (src && !src.startsWith("http") && !src.startsWith("//")) {
    const cleanSrc = src.split("?")[0];
    const filePath = path.join(DIST_ROOT, cleanSrc);

    if (fs.existsSync(filePath)) {
      referencedFiles.add(path.basename(cleanSrc));
      const integrity = generateIntegrity(filePath);
      if (integrity) {
        $(elem).attr("integrity", integrity);
        $(elem).attr("crossorigin", "anonymous");
      }
    } else {
      console.warn(`Warning: Script file not found: ${filePath}`);
    }
  }
  // Add nonce placeholder
  $(elem).attr("nonce", "NGINX_CSP_NONCE");
});

// Process CSS stylesheets and modulepreload
$('link[rel="stylesheet"], link[rel="modulepreload"]').each((i, elem) => {
  const href = $(elem).attr("href");
  if (href && !href.startsWith("http") && !href.startsWith("//")) {
    const cleanHref = href.split("?")[0];
    const filePath = path.join(DIST_ROOT, cleanHref);

    if (fs.existsSync(filePath)) {
      referencedFiles.add(path.basename(cleanHref));
      const integrity = generateIntegrity(filePath);
      if (integrity) {
        $(elem).attr("integrity", integrity);
        if ($(elem).attr("rel") === "stylesheet") {
          $(elem).attr("crossorigin", "anonymous");
        } else {
          if (!$(elem).attr("crossorigin")) {
            $(elem).attr("crossorigin", "anonymous");
          }
        }
      }
    } else {
      console.warn(`Warning: Resource file not found: ${filePath}`);
    }
  }
});

$("style").each((i, elem) => {
  $(elem).attr("nonce", "NGINX_CSP_NONCE");
});

// Write updated HTML
try {
  fs.writeFileSync(INDEX_PATH, $.html(), "utf8");
  console.log("SRI hashes added successfully to index.html");
} catch (err) {
  console.error("Error writing index.html:", err);
  process.exit(1);
}

// --- Prune Unused Files Analysis (Javascript) ---
console.log("\nAnalyzing for unused JS files...");

// Recursive function to find referenced chunks inside a file content
function findReferencedChunks(filePath, knownFiles) {
  if (!fs.existsSync(filePath)) return;

  const content = fs.readFileSync(filePath, "utf8");
  // Simple regex to find chunk filenames (e.g. "chunk-XXXX.js")
  // Adjust based on your chunk format (esbuild uses chunk-HASH.js)
  const chunkRegex = /chunk-[A-Z0-9]+\.js/g;
  let match;
  while ((match = chunkRegex.exec(content)) !== null) {
    const chunkName = match[0];
    if (!knownFiles.has(chunkName)) {
      const chunkPath = path.join(DIST_ROOT, chunkName);
      if (fs.existsSync(chunkPath)) {
        knownFiles.add(chunkName);
        // Recursively scan this chunk too
        findReferencedChunks(chunkPath, knownFiles);
      }
    }
  }
}

// Start with files referenced in index.html
const allReferencedFiles = new Set(referencedFiles);

// Iterate over initial set and find their dependencies
// We use Array.from to iterate because we add to the Set during recursion
// (though recursion uses the pass-by-reference Set, iterating the initial list is fine)
// Correct approach: recursively process files as we find them.
referencedFiles.forEach((file) => {
  const filePath = path.join(DIST_ROOT, file);
  findReferencedChunks(filePath, allReferencedFiles);
});

// List all JS files in directory
const allJsFiles = fs.readdirSync(DIST_ROOT).filter((f) => f.endsWith(".js"));

let unusedCount = 0;
allJsFiles.forEach((file) => {
  if (!allReferencedFiles.has(file)) {
    // Double check against 'polyfills' or 'main' or 'scripts' if somehow missed
    // (but they should have been in index.html)
    // If file is NOT in index.html and NOT referenced by any other file, it is unused.

    console.warn(
      `Warning: Potentially unused JS file found and deleted: ${file}`,
    );

    const fullPath = path.join(DIST_ROOT, file);
    try {
      fs.unlinkSync(fullPath);
      unusedCount++;
    } catch (e) {
      console.error(`Failed to delete ${file}: ${e.message}`);
    }
  }
});

if (unusedCount === 0) {
  console.log("No unused JS files found.");
} else {
  console.log(`Deleted ${unusedCount} unused JS files.`);
}

#!/usr/bin/env node
/**
 * Scrape 19 SEO theory pages from holisticseo.digital
 * Uses only Node.js built-in modules (no npm needed)
 */
const https = require('https');
const http = require('http');
const { URL } = require('url');
const fs = require('fs');

const HEADERS = {
  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
  "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
  "Accept-Language": "en-US,en;q=0.5",
};

const URLS = [
  "https://www.holisticseo.digital/theoretical-seo/topical-authority/",
  "https://www.holisticseo.digital/theoretical-seo/knowledge-graph/",
  "https://www.holisticseo.digital/theoretical-seo/semantic-search/",
  "https://www.holisticseo.digital/theoretical-seo/search-intent/",
  "https://www.holisticseo.digital/theoretical-seo/contextual-search/",
  "https://www.holisticseo.digital/theoretical-seo/information-extraction/",
  "https://www.holisticseo.digital/theoretical-seo/entity-seo/",
  "https://www.holisticseo.digital/theoretical-seo/topic-cluster/",
  "https://www.holisticseo.digital/on-page-seo/topic-clusters/",
  "https://www.holisticseo.digital/theoretical-seo/content-marketing/",
  "https://www.holisticseo.digital/theoretical-seo/technical-seo/",
  "https://www.holisticseo.digital/on-page-seo/",
  "https://www.holisticseo.digital/marketing/search-engine-history/",
  "https://www.holisticseo.digital/marketing/semantic-seo/",
  "https://www.holisticseo.digital/marketing/semantic-content-network/",
  "https://www.holisticseo.digital/marketing/seo-case-study/",
  "https://www.holisticseo.digital/marketing/importance-of-lexical-semantics-and-semantic-similarity-closeness-for-seo-an-seo-case-study-with-5-websites/",
  "https://www.holisticseo.digital/marketing/micro-semantics/",
  "https://www.holisticseo.digital/marketing/macro-semantics/",
];

/**
 * Fetch URL and return response body as string
 */
function fetchPage(url) {
  return new Promise((resolve, reject) => {
    const parsed = new URL(url);
    const mod = parsed.protocol === 'https:' ? https : http;
    const opts = {
      hostname: parsed.hostname,
      port: parsed.port,
      path: parsed.pathname + parsed.search,
      method: 'GET',
      headers: HEADERS,
      timeout: 30000,
    };

    const req = mod.request(opts, (res) => {
      // Follow redirects (up to 5)
      if ([301, 302, 303, 307, 308].includes(res.statusCode) && res.headers.location) {
        const redirectUrl = new URL(res.headers.location, url).toString();
        res.resume();
        return fetchPage(redirectUrl).then(resolve).catch(reject);
      }

      if (res.statusCode !== 200) {
        res.resume();
        reject(new Error(`HTTP ${res.statusCode}`));
        return;
      }

      const chunks = [];
      res.on('data', chunk => chunks.push(chunk));
      res.on('end', () => {
        const body = Buffer.concat(chunks).toString('utf-8');
        resolve(body);
      });
      res.on('error', reject);
    });

    req.on('error', reject);
    req.on('timeout', () => { req.destroy(); reject(new Error('Timeout')); });
    req.end();
  });
}

/**
 * Extract title from HTML
 */
function extractTitle(html) {
  const match = html.match(/<title[^>]*>([\s\S]*?)<\/title>/i);
  if (match) {
    return match[1].replace(/<[^>]+>/g, '').replace(/&[^;]+;/g, ' ').replace(/\s+/g, ' ').trim();
  }
  return null;
}

/**
 * Strip unwanted elements and extract text
 */
function extractText(html) {
  let cleaned = html;

  // Remove <script>, <style>, <nav>, <footer>, <header>, <noscript>, <iframe>, <svg>, <canvas> blocks
  cleaned = cleaned.replace(/<script[\s\S]*?<\/script>/gi, '');
  cleaned = cleaned.replace(/<style[\s\S]*?<\/style>/gi, '');
  cleaned = cleaned.replace(/<nav[\s\S]*?<\/nav>/gi, '');
  cleaned = cleaned.replace(/<footer[\s\S]*?<\/footer>/gi, '');
  cleaned = cleaned.replace(/<header[\s\S]*?<\/header>/gi, '');
  cleaned = cleaned.replace(/<noscript[\s\S]*?<\/noscript>/gi, '');
  cleaned = cleaned.replace(/<iframe[\s\S]*?<\/iframe>/gi, '');
  cleaned = cleaned.replace(/<svg[\s\S]*?<\/svg>/gi, '');
  cleaned = cleaned.replace(/<canvas[\s\S]*?<\/canvas>/gi, '');
  cleaned = cleaned.replace(/<form[\s\S]*?<\/form>/gi, '');
  cleaned = cleaned.replace(/<!--[\s\S]*?-->/g, ''); // HTML comments

  // Convert block-level tags to newlines
  cleaned = cleaned.replace(/<\/(p|div|li|h[1-6]|section|article|blockquote|pre|td|th|figcaption|dt|dd|aside|main|tr|table|ul|ol|dl|figure|fieldset|details)[^>]*>/gi, '\n');
  cleaned = cleaned.replace(/<(br|hr)[^>]*\/?>/gi, '\n');

  // Remove all remaining HTML tags
  cleaned = cleaned.replace(/<[^>]+>/g, ' ');

  // Decode common HTML entities
  cleaned = cleaned.replace(/&amp;/g, '&');
  cleaned = cleaned.replace(/&lt;/g, '<');
  cleaned = cleaned.replace(/&gt;/g, '>');
  cleaned = cleaned.replace(/&quot;/g, '"');
  cleaned = cleaned.replace(/&#39;/g, "'");
  cleaned = cleaned.replace(/&nbsp;/g, ' ');
  cleaned = cleaned.replace(/&#(\d+);/g, (_, n) => String.fromCharCode(Number(n)));
  cleaned = cleaned.replace(/&[a-z]+;/gi, ' ');

  return cleaned;
}

/**
 * Clean up whitespace
 */
function cleanWhitespace(text, maxChars = 5000) {
  // Normalize whitespace
  let cleaned = text.replace(/[ \t]+/g, ' ');
  // Collapse 3+ newlines into 2
  cleaned = cleaned.replace(/\n{3,}/g, '\n\n');

  // Trim each line and remove empty leading/trailing lines
  let lines = cleaned.split('\n').map(l => l.trim());
  while (lines.length && !lines[0]) lines.shift();
  while (lines.length && !lines[lines.length - 1]) lines.pop();

  cleaned = lines.join('\n');

  // Trim to maxChars
  if (cleaned.length > maxChars) {
    cleaned = cleaned.substring(0, maxChars);
    const lastSpace = cleaned.lastIndexOf(' ');
    if (lastSpace > maxChars - 100) {
      cleaned = cleaned.substring(0, lastSpace) + '...';
    } else {
      cleaned += '...';
    }
  }

  return cleaned;
}

async function scrapePage(url) {
  const html = await fetchPage(url);
  const title = extractTitle(html);
  const rawText = extractText(html);
  const content = cleanWhitespace(rawText, 5000);

  return { url, title, content };
}

async function main() {
  const results = [];
  for (let i = 0; i < URLS.length; i++) {
    const url = URLS[i];
    process.stderr.write(`[${i + 1}/${URLS.length}] Scraping: ${url}\n`);
    try {
      const result = await scrapePage(url);
      results.push(result);
    } catch (err) {
      process.stderr.write(`  ERROR: ${err.message}\n`);
      results.push({ url, title: null, content: null, error: err.message });
    }
    // Pause between requests
    if (i < URLS.length - 1) {
      await new Promise(r => setTimeout(r, 1500));
    }
  }

  const outputPath = '/home/steve/seo_pages.json';
  fs.writeFileSync(outputPath, JSON.stringify(results, null, 2), 'utf-8');

  const totalChars = results.reduce((sum, r) => sum + (r.content ? r.content.length : 0), 0);
  const successes = results.filter(r => r.content).length;
  process.stderr.write(`\nDone. ${successes}/${URLS.length} pages scraped. Total chars: ${totalChars}\n`);
  process.stderr.write(`Output: ${outputPath}\n`);

  // Print JSON to stdout
  console.log(JSON.stringify(results, null, 2));
}

main().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});

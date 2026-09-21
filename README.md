# WorkSmart Hub

A static-first small-business tools and guides website, deployed to Cloudflare as a Worker with static assets. Designed to be fast, mobile-friendly, accessible, and free to host.

## Run locally

No package manager is required for the current static build. Serve the project directory with any local static server, then open the local URL. For example, use your editor's live server or a local HTTP server.

Do not open `index.html` directly from `file://` when testing navigation; use HTTP so root-relative paths work.

## Current features

- Homepage, tools library, guides, templates, tool finder, trust pages, and 404 page
- 10 working browser-side tools
- Search across the tool registry
- Deterministic tool recommendation fallback without an API key
- Responsive accessible design system
- Canonical metadata, sitemap, robots.txt, breadcrumbs, and security headers
- Per-page Open Graph and Twitter Card metadata with a generated 1200x630 share card
- Ad slots that stay out of the DOM entirely until AdSense is enabled

## Social share cards

Every page carries Open Graph and Twitter Card tags between `<!-- social:start -->` and `<!-- social:end -->` markers in its `<head>`. Each page points at its own 1200x630 card in `og/`, rendered in the site's Studio palette.

After adding a page, or after changing a title, description or the brand palette, regenerate everything with one command:

```bash
python scripts/generate-social-meta.py
```

The script is idempotent. It renders one card per HTML page found outside `.freebuff/`, then rewrites the managed block. Any stray `og:*` or `twitter:*` tag outside the markers is removed first, so a page cannot end up with duplicate conflicting tags. `404.html` is skipped on purpose — it has no canonical URL and should never be shared.

`og:image` must be an absolute URL for crawlers to fetch it, so the card URLs use the domain currently in `ORIGIN` near the top of the script. Update that constant when a custom domain replaces the `workers.dev` address, then re-run.

Cards can also be checked by hand in the [Facebook Sharing Debugger](https://developers.facebook.com/tools/debug/) or LinkedIn Post Inspector, both of which refetch and report exactly what a crawler sees.

## Repository

Source of truth: `https://github.com/Rabbislmqtr/worksmarthub` (branch `main`).

Live URL: `https://worksmarthub.rabbilslmqtr.workers.dev`

## Deployment to Cloudflare

This project deploys as a **Worker with static assets** (Cloudflare is merging Pages into Workers). All build configuration lives in `wrangler.jsonc`, so the dashboard needs nothing beyond the Git connection.

### Connect the repository

1. In the Cloudflare dashboard open **Workers & Pages** → **Create** → **Workers** → **Import a repository**.
2. Authorise GitHub and select `Rabbislmqtr/worksmarthub`.
3. Keep the production branch as `main`. The deploy command is `npx wrangler deploy` and there is no build step.
4. Save and deploy. The first deployment produces a `*.workers.dev` URL.
5. Confirm that URL serves the styled homepage before adding a custom domain.
6. Add the domain under **Settings → Domains & Routes**, then wait for HTTPS to become active.

Every later push to `main` redeploys automatically.

### What `wrangler.jsonc` controls

- `assets.directory: "."` — the repository root is the website.
- `assets.not_found_handling: "404-page"` — serves `404.html` for unknown paths. This replaces the invalid `/* /404.html 404` line from `_redirects`: Cloudflare only accepts 200, 301, 302, 303, 307 and 308 in that file, so any 404 rewrite fails the deploy.
- `assets.html_handling: "auto-trailing-slash"` — serves `tools/` from `tools/index.html` and redirects `/tools` to `/tools/`.

### What `.assetsignore` controls

The asset directory is the repository root, so without this file Cloudflare uploads `.git/` as public static assets — publishing full commit history, remotes and git config on the live site. `.assetsignore` keeps `.git/`, build tooling, `scripts/`, `README.md` and the internal planning notes off the website.

`og/` is deliberately *not* excluded — those share cards have to be publicly reachable for crawlers to fetch them.

### Direct upload alternative

**Upload the complete project folder, not only `index.html`.** The site needs `styles.css`, `tokens.css`, `app.js`, `favicon.svg`, and every `tools/` and `guides/` subdirectory. If you open a single HTML file or upload only one file, the site will appear as plain browser-default HTML and the other links cannot resolve.

### After the first deploy

1. Open the deployed domain root, not an individual file or Preview-tab-only URL.
2. Confirm HTTPS, every route, `robots.txt`, and `sitemap.xml`.
3. Canonical URLs, `sitemap.xml` and `robots.txt` currently point at `https://worksmarthub.rabbilslmqtr.workers.dev`. Update all three in one pass when a custom domain is connected.
4. Confirm the homepage renders with the cream paper background and dark hero card. If it renders as plain browser-default text, the stylesheet did not load.

## Policy pages

The Privacy Policy, Terms of Use, Cookie Policy and Disclaimer describe what this site **actually does**, not boilerplate. They state three specific claims, and each is verifiable against the code:

- calculators run entirely in the browser and transmit nothing;
- the site sets no cookies of its own and uses no browser storage;
- no analytics or advertising code is loaded — the site makes no third-party requests at all.

**If a change breaks one of those claims, the matching policy page must be updated in the same commit.** Adding server-side AI breaks the first; adding analytics, AdSense or a preference-storing banner breaks the second; installing the AdSense snippet breaks the third.

These documents have not been reviewed by a lawyer. Owner-specific details that only the site owner can supply — legal entity name and address, governing law, effective date — are deliberately absent rather than invented, and are tracked in a private local file that is excluded from both this repository and the deployed site.

## Before launch

- Review all guide content and calculator formulas.
- Test at 320px, 375px, 390px, 412px, 768px, 1024px, and desktop widths.
- Connect Google Search Console and submit the sitemap.
- Configure analytics only after deciding what non-sensitive events are necessary.
- Add a Google-approved consent solution where applicable before non-essential advertising.
- Apply for AdSense only after the site has substantial original content and a polished user experience.

## AdSense configuration

The site loads no advertisements. Visitors never see a placeholder box, a dashed outline, or any note about the site's monetisation status: while ads are off, each slot element is **removed from the DOM** (`renderAdSlots()` in `app.js`), so there is nothing to render and nothing to accidentally style.

Everything is driven by one object near the top of `app.js`:

```js
const ADS = { enabled: false, publisherId: '', units: { 'home-mid': '', 'tool-sidebar': '' } };
```

To switch ads on:

1. Set `enabled` to `true` and put the AdSense publisher ID in `publisherId` (`ca-pub-…`).
2. Paste each slot's ad-unit ID into `units`. The slot names are the `data-ad-slot` values: `home-mid` (homepage) and `tool-sidebar` (every calculator page).
3. **Widen the Content-Security-Policy in `_headers`.** It is currently `script-src 'self'`, which will block the Google ad script outright — the ads simply will not appear. `img-src`, `frame-src` and `connect-src` also need Google's domains.

Existing slot positions are already marked up in the HTML and in `renderTool()`, so step 1–2 are the only code changes needed to place an ad in a position that already exists. Adding a new position means adding one `adMount('name')` call and an `ADS.units` entry.

Never request clicks, place ads inside calculator controls, or make ads resemble navigation or download buttons.

## Future server-side AI

The first tool finder is deterministic and works without secrets. If a real AI provider is added later, implement it behind a server-side endpoint with environment variables, validation, rate limiting, abuse protection, and a registry-only link catalogue. Never expose an API key in `app.js`.

## Quality checklist

- [ ] Build/deployment preview succeeds
- [ ] All routes return 200 except intentional 404s
- [ ] No console errors
- [ ] Calculator edge cases are tested
- [ ] Metadata and canonical URLs use the production domain
- [ ] Sitemap contains only public canonical pages
- [ ] Policies are reviewed by the owner
- [ ] Accessibility and keyboard checks pass
- [ ] Core Web Vitals are checked on a real mobile device
- [ ] Human content review is complete

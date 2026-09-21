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
- AdSense-ready placeholders that remain disabled until configured

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

The asset directory is the repository root, so without this file Cloudflare uploads `.git/` as public static assets — publishing full commit history, remotes and git config on the live site. `.assetsignore` keeps `.git/`, build tooling, `README.md` and the internal planning notes off the website.

### Direct upload alternative

**Upload the complete project folder, not only `index.html`.** The site needs `styles.css`, `tokens.css`, `app.js`, `favicon.svg`, and every `tools/` and `guides/` subdirectory. If you open a single HTML file or upload only one file, the site will appear as plain browser-default HTML and the other links cannot resolve.

### After the first deploy

1. Open the deployed domain root, not an individual file or Preview-tab-only URL.
2. Confirm HTTPS, every route, `robots.txt`, and `sitemap.xml`.
3. Canonical URLs, `sitemap.xml` and `robots.txt` currently point at `https://worksmarthub.rabbilslmqtr.workers.dev`. Update all three in one pass when a custom domain is connected.
4. Confirm the homepage renders with the cream paper background and dark hero card. If it renders as plain browser-default text, the stylesheet did not load.

## Before launch

- Replace the example brand/domain/email values.
- Review and customize Privacy Policy, Terms, Cookie Policy, and Disclaimer for the owner’s jurisdiction and services.
- Add a real monitored contact address.
- Review all guide content and calculator formulas.
- Test at 320px, 375px, 390px, 412px, 768px, 1024px, and desktop widths.
- Connect Google Search Console and submit the sitemap.
- Configure analytics only after deciding what non-sensitive events are necessary.
- Add a Google-approved consent solution where applicable before non-essential advertising.
- Apply for AdSense only after the site has substantial original content and a polished user experience.

## AdSense configuration

The current site intentionally does not load real advertisements. When the site is approved and the owner has an AdSense client ID, add the official code through a reviewed configuration layer. Never request clicks, place ads inside calculator controls, or make ads resemble navigation/download buttons.

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

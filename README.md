# WorkSmart Hub

A static-first small-business tools and guides website. The initial version is designed to be fast, mobile-friendly, accessible, and ready for a future Cloudflare Pages deployment.

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

## Deployment to Cloudflare Pages

**Upload the complete project folder, not only `index.html`.** The site needs `styles.css`, `tokens.css`, `app.js`, `favicon.svg`, and every `tools/` and `guides/` subdirectory. If you open a single HTML file or upload only one file, the site will appear as plain browser-default HTML and the other links cannot resolve.

1. Create a Cloudflare account.
2. Create a Pages project connected to this repository, or upload the static output.
3. Use the project root as the build output directory.
4. There is currently no build command: the root files and subdirectories are the deployable site. Preserve the folder structure exactly.
5. Open the deployed domain root, not an individual file or Preview-tab-only URL.
6. Add a custom domain in Cloudflare Pages before applying for advertising.
7. Confirm HTTPS, every route, `robots.txt`, and `sitemap.xml`.
8. Replace `https://worksmarthub.example` in canonical tags and the sitemap with the real domain.

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

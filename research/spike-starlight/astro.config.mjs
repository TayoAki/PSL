// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import { readdirSync } from 'node:fs';

// Sidebar generated from the data files: one group per year, newest year expanded.
function demoSidebar() {
  const root = new URL('./src/content/demos/', import.meta.url);
  const years = readdirSync(root).filter((y) => /^\d{4}$/.test(y)).sort().reverse();
  const fmt = (ymd) =>
    new Date(`${ymd.slice(0, 4)}-${ymd.slice(4, 6)}-${ymd.slice(6, 8)}T00:00:00Z`).toLocaleDateString('en-US', {
      year: 'numeric', month: 'long', day: 'numeric', timeZone: 'UTC',
    });
  return [
    { label: 'All demos', link: '/demos/' },
    ...years.map((year, i) => ({
      label: year,
      collapsed: i > 0,
      items: readdirSync(new URL(`${year}/`, root))
        .filter((f) => f.endsWith('.yaml'))
        .map((f) => f.slice(0, 8))
        .sort()
        .reverse()
        .map((ymd) => ({ label: fmt(ymd), link: `/demos/${year}/${ymd}/` })),
    })),
  ];
}

export default defineConfig({
  site: 'https://demos.example.com',
  integrations: [
    starlight({
      title: 'Demo Hub',
      sidebar: [{ label: 'Demos', items: demoSidebar() }],
      head: [{ tag: 'link', attrs: { rel: 'alternate', type: 'application/rss+xml', title: 'Demos', href: '/demos/rss.xml' } }],
    }),
  ],
});

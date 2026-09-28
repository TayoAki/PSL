import rss from '@astrojs/rss';
import type { APIContext } from 'astro';
import { publishedWeeks, weekPath, weekTitle } from '../../lib/weeks';

export async function GET(context: APIContext) {
  const weeks = await publishedWeeks();
  return rss({
    title: 'Demo Hub',
    description: 'Weekly demos of new and upcoming features.',
    site: context.site!,
    items: weeks.slice(0, 50).map((w) => ({
      title: weekTitle(w.data.date),
      description: w.data.headline,
      link: weekPath(w.data.date),
      pubDate: w.data.publishedAt,
      content: `<ul>${w.data.demos.map((d) => `<li><a href="${new URL(weekPath(w.data.date), context.site)}#${d.slug}">${d.title}</a></li>`).join('')}</ul>`,
    })),
  });
}

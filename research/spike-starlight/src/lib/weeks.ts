import { getCollection } from 'astro:content';

export const weekTitle = (d: Date) =>
  d.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric', timeZone: 'UTC' });
export const weekPath = (d: Date) => {
  const iso = d.toISOString().slice(0, 10);
  return `/demos/${iso.slice(0, 4)}/${iso.replaceAll('-', '')}/`;
};
export async function publishedWeeks() {
  const weeks = await getCollection('weeks', (w) => !w.data.draft);
  return weeks.sort((a, b) => b.data.date.valueOf() - a.data.date.valueOf());
}

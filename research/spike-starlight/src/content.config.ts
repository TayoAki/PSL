import { defineCollection, reference } from 'astro:content';
import { glob, file } from 'astro/loaders';
import { z } from 'astro/zod';
import { docsLoader } from '@astrojs/starlight/loaders';
import { docsSchema } from '@astrojs/starlight/schema';

const demo = z.object({
  slug: z.string().regex(/^[a-z0-9-]+$/),
  title: z.string().max(80),
  presenters: z.array(reference('people')).min(1),
  tags: z.array(reference('tags')).min(1).max(4),
  summary: z.string().min(20),
  video: z.object({ provider: z.literal('youtube'), id: z.string().regex(/^[\w-]{11}$/) }),
});

export const collections = {
  docs: defineCollection({ loader: docsLoader(), schema: docsSchema() }),
  weeks: defineCollection({
    loader: glob({ pattern: '**/*.yaml', base: './src/content/demos' }),
    schema: z.object({
      date: z.coerce.date(),
      headline: z.string().max(200),
      publishedAt: z.coerce.date(),
      draft: z.boolean().default(false),
      demos: z.array(demo).min(1),
    }),
  }),
  people: defineCollection({
    loader: file('src/data/people.yml'),
    schema: z.object({ id: z.string(), name: z.string(), team: z.string() }),
  }),
  tags: defineCollection({
    loader: file('src/data/tags.yml'),
    schema: z.object({ id: z.string(), label: z.string(), aliases: z.array(z.string()) }),
  }),
};

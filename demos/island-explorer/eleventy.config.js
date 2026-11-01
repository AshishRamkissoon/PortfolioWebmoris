import Image from "@11ty/eleventy-img";

import photos from "./src/_data/photos.json" with { type: "json" };

const WIDTHS = [480, 960, 1440, 2000];

/** Responsive <picture> (AVIF, WebP, JPEG) for a photo key from photos.json. */
async function picture(key, alt, sizes = "100vw", options = {}) {
  const photo = photos[key];
  if (!photo) throw new Error(`Unknown photo key: ${key}`);
  const metadata = await Image(`src/images/photos/${photo.file}`, {
    widths: options.widths || WIDTHS,
    formats: ["avif", "webp", "jpeg"],
    outputDir: "_site/img/",
    urlPath: "/img/",
    sharpAvifOptions: { quality: 55, effort: 2 }, // effort 2: much faster builds, near-identical size
    sharpWebpOptions: { quality: 72 },
    sharpJpegOptions: { quality: 75, mozjpeg: true },
  });
  const attributes = {
    alt,
    sizes,
    loading: options.eager ? "eager" : "lazy",
    decoding: "async",
  };
  if (options.eager) attributes.fetchpriority = "high";
  if (options.class) attributes.class = options.class;
  if (options.transition) attributes.style = `view-transition-name: ${options.transition}`;
  if (options.data) attributes[`data-${options.data}`] = "";
  return Image.generateHTML(metadata, attributes);
}

export default function (eleventyConfig) {
  // The reusable Webmoris demo kit (banner, blocked forms, noindex).
  eleventyConfig.addPassthroughCopy({ "../../demo_kit/demo-kit.js": "demo-kit.js" });
  eleventyConfig.addPassthroughCopy({ "src/static": "/" });
  // 2000 px masters, opened by the gallery lightbox (only loaded on click).
  eleventyConfig.addPassthroughCopy({ "src/images/photos": "img/full" });

  eleventyConfig.addAsyncShortcode("picture", picture);

  eleventyConfig.addFilter("money", (amount) => `MUR ${Number(amount).toLocaleString("en-US")}`);
  eleventyConfig.addFilter("byCategory", (tours, slug) => tours.filter((t) => t.category === slug));
  eleventyConfig.addFilter("categoryName", (slug, categories) => categories.find((c) => c.slug === slug)?.name || slug);
  eleventyConfig.addFilter("featured", (tours) => tours.filter((t) => t.featured));
  eleventyConfig.addFilter("others", (tours, slug) => tours.filter((t) => t.slug !== slug));
  eleventyConfig.addFilter("limit", (items, count) => items.slice(0, count));
  // Projects { lat, lng } onto the island map's 400×440 viewBox (linear fit to the coastline path).
  // `left`/`top` are percentages for HTML markers laid over the SVG.
  eleventyConfig.addFilter("mapPos", ({ lat, lng }) => {
    const x = 157 + 666 * (lng - 57.501);
    const y = 160 + 675 * (-20.161 - lat);
    return { x, y, left: (x / 4).toFixed(2), top: (y / 4.4).toFixed(2) };
  });
  // Town labels that don't collide with the main pin or its name label (sizes are rough, in map units).
  eleventyConfig.addFilter("mapTowns", (places, pin, pinLabel) => {
    const project = eleventyConfig.getFilter("mapPos");
    const chip = pinLabel.length * 7 + 24;
    const chipLeft = pin.x < 110 ? pin.x - 15 : pin.x > 290 ? pin.x + 15 - chip : pin.x - chip / 2;
    return places
      .map((place) => ({ ...place, pos: project(place) }))
      .filter(({ name, pos }) => {
        const width = name.length * 6 + 10;
        const [from, to] = pos.x > 260 ? [pos.x - width, pos.x] : [pos.x, pos.x + width];
        const overlapsX = from < Math.max(chipLeft + chip, pin.x + 20) && to > Math.min(chipLeft, pin.x - 20);
        return !(overlapsX && pos.y > pin.y - 95 && pos.y < pin.y + 15);
      });
  });

  return {
    dir: { input: "src", includes: "_includes", data: "_data", output: "_site" },
    htmlTemplateEngine: "njk",
    markdownTemplateEngine: "njk",
  };
}

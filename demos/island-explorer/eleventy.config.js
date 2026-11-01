import Image from "@11ty/eleventy-img";

import mapFrame from "./src/_data/mapFrame.json" with { type: "json" };
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
  // Projects { lat, lng } onto the OpenStreetMap base map (same projection as scripts/build-map.mjs).
  // Returns percentages of the map's width and height, for HTML markers laid over the image.
  const mapPos = ({ lat, lng }) => ({
    left: (((lng - mapFrame.west) * mapFrame.kx) / mapFrame.width) * 100,
    top: (((mapFrame.north - lat) * mapFrame.ky) / mapFrame.height) * 100,
  });
  eleventyConfig.addFilter("mapPos", mapPos);
  // Place labels that don't collide with the main pin and its name label.
  // Sizes are rough estimates in % of the map (1% ≈ 4 px wide, 4.8 px tall at ~420 px).
  eleventyConfig.addFilter("mapLabels", (places, pin, pinLabel) => {
    const chip = (pinLabel.length * 7 + 24) / 4;
    const chipLeft = pin.left < 27 ? pin.left - 4 : pin.left > 73 ? pin.left + 4 - chip : pin.left - chip / 2;
    const pinBox = [Math.min(chipLeft, pin.left - 5), Math.max(chipLeft + chip, pin.left + 5), pin.top - 16, pin.top + 2.5];
    return places
      .map((place) => ({ ...place, pos: mapPos(place), flip: mapPos(place).left > 65 }))
      .filter(({ name, kind, pos, flip }) => {
        const width = kind === "park" ? 22 : (name.length * 6 + 14) / 4;
        const half = kind === "park" ? 3 : 1.8;
        const [from, to] = kind === "park" ? [pos.left - width / 2, pos.left + width / 2] : flip ? [pos.left - width, pos.left] : [pos.left, pos.left + width];
        return !(from < pinBox[1] && to > pinBox[0] && pos.top - half < pinBox[3] && pos.top + half > pinBox[2]);
      });
  });

  return {
    dir: { input: "src", includes: "_includes", data: "_data", output: "_site" },
    htmlTemplateEngine: "njk",
    markdownTemplateEngine: "njk",
  };
}

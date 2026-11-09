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
  return Image.generateHTML(metadata, attributes);
}

/** Plain URL of one JPEG size, for places that need a single image (cursor previews, WebGL texture). */
async function photoUrl(key, width = 960) {
  const photo = photos[key];
  if (!photo) throw new Error(`Unknown photo key: ${key}`);
  const metadata = await Image(`src/images/photos/${photo.file}`, {
    widths: [width],
    formats: ["webp"],
    outputDir: "_site/img/",
    urlPath: "/img/",
    sharpWebpOptions: { quality: 72 },
  });
  return metadata.webp[0].url;
}

/** <link rel="preload"> for the page's hero photo, so it downloads before CSS, fonts and scripts finish. */
async function preloadImage(key, sizes = "100vw", widths = WIDTHS) {
  const photo = photos[key];
  if (!photo) throw new Error(`Unknown photo key: ${key}`);
  const metadata = await Image(`src/images/photos/${photo.file}`, {
    widths,
    formats: ["avif", "webp", "jpeg"],
    outputDir: "_site/img/",
    urlPath: "/img/",
    sharpAvifOptions: { quality: 55, effort: 2 },
    sharpWebpOptions: { quality: 72 },
    sharpJpegOptions: { quality: 75, mozjpeg: true },
  });
  const srcset = metadata.avif.map((image) => image.srcset).join(", ");
  return `<link rel="preload" as="image" type="image/avif" imagesrcset="${srcset}" imagesizes="${sizes}" fetchpriority="high">`;
}

export default function (eleventyConfig) {
  // The reusable Webmoris demo kit (banner, blocked forms, noindex).
  eleventyConfig.addPassthroughCopy({ "../../demo_kit/demo-kit.js": "demo-kit.js" });
  eleventyConfig.addPassthroughCopy({ "../../demo_kit/demo-kit.css": "demo-kit.css" });
  eleventyConfig.addPassthroughCopy({ "src/static": "/" });

  eleventyConfig.addAsyncShortcode("picture", picture);
  eleventyConfig.addAsyncShortcode("photoUrl", photoUrl);
  eleventyConfig.addAsyncShortcode("preloadImage", preloadImage);

  eleventyConfig.addFilter("money", (amount) => `Rs ${Number(amount).toLocaleString("en-US")}`);
  eleventyConfig.addFilter("bySection", (items, slug) => items.filter((item) => item.section === slug));
  eleventyConfig.addFilter("signature", (items) => items.filter((item) => item.signature));
  eleventyConfig.addFilter("limit", (items, count) => items.slice(0, count));
  // Places { lat, lng } on the OpenStreetMap base map (same projection as the Island Explorer map build).
  eleventyConfig.addFilter("mapPos", ({ lat, lng }) => ({
    left: (((lng - mapFrame.west) * mapFrame.kx) / mapFrame.width) * 100,
    top: (((mapFrame.north - lat) * mapFrame.ky) / mapFrame.height) * 100,
  }));
  // Deterministic pseudo-random numbers for decorative layouts (stars), so every build is identical.
  eleventyConfig.addFilter("rand", (seed, min = 0, max = 1) => {
    const x = Math.sin(seed * 9301 + 49297) * 233280;
    return min + (x - Math.floor(x)) * (max - min);
  });

  return {
    dir: { input: "src", includes: "_includes", data: "_data", output: "_site" },
    htmlTemplateEngine: "njk",
    markdownTemplateEngine: "njk",
  };
}

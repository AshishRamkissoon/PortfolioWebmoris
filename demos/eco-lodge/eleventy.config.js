import Image from "@11ty/eleventy-img";

import mapFrame from "./src/_data/mapFrame.json" with { type: "json" };
import photos from "./src/_data/photos.json" with { type: "json" };

const WIDTHS = [480, 960, 1440, 2000];
const IMAGE_OPTIONS = {
  formats: ["avif", "webp", "jpeg"],
  outputDir: "_site/img/",
  urlPath: "/img/",
  sharpAvifOptions: { quality: 55, effort: 2 }, // effort 2: much faster builds, near-identical size
  sharpWebpOptions: { quality: 72 },
  sharpJpegOptions: { quality: 75, mozjpeg: true },
};

// Photos are the credited originals in src/images/photos/ (resized to 2000 px max).
const source = (key) => {
  const photo = photos[key];
  if (!photo) throw new Error(`Unknown photo key: ${key}`);
  return `src/images/photos/${photo.file}`;
};

/** Responsive <picture> (AVIF, WebP, JPEG) for a photo key from photos.json. */
async function picture(key, alt, sizes = "100vw", options = {}) {
  const metadata = await Image(source(key), { ...IMAGE_OPTIONS, widths: options.widths || WIDTHS });
  const attributes = { alt, sizes, loading: options.eager ? "eager" : "lazy", decoding: "async" };
  if (options.eager) attributes.fetchpriority = "high";
  if (options.class) attributes.class = options.class;
  return Image.generateHTML(metadata, attributes);
}

/** <link rel="preload"> for a page's first photo, so it starts downloading straight away. */
async function preloadImage(key, sizes = "100vw", widths = WIDTHS) {
  const metadata = await Image(source(key), { ...IMAGE_OPTIONS, widths });
  const srcset = metadata.avif.map((image) => image.srcset).join(", ");
  return `<link rel="preload" as="image" type="image/avif" imagesrcset="${srcset}" imagesizes="${sizes}" fetchpriority="high">`;
}

/** Plain URL of one WebP size, for places that need a single image (route stops). */
async function photoUrl(key, width = 960) {
  const metadata = await Image(source(key), { ...IMAGE_OPTIONS, formats: ["webp"], widths: [width] });
  return metadata.webp[0].url;
}

export default function (eleventyConfig) {
  // The reusable Webmoris demo kit (banner, blocked forms, noindex).
  eleventyConfig.addPassthroughCopy({ "../../demo_kit/demo-kit.js": "demo-kit.js" });
  eleventyConfig.addPassthroughCopy({ "../../demo_kit/demo-kit.css": "demo-kit.css" });
  eleventyConfig.addPassthroughCopy({ "src/static": "/" });

  eleventyConfig.addAsyncShortcode("picture", picture);
  eleventyConfig.addAsyncShortcode("preloadImage", preloadImage);
  eleventyConfig.addAsyncShortcode("photoUrl", photoUrl);

  eleventyConfig.addFilter("mur", (amount) => "Rs " + Number(amount).toLocaleString("en-US"));
  // Price on booking sites (about 11% more, so the direct price saves ~10%).
  eleventyConfig.addFilter("otaPrice", (amount, discount) => Math.round(amount / (1 - discount / 100) / 100) * 100);
  eleventyConfig.addFilter("featured", (items) => items.filter((item) => item.featured));
  eleventyConfig.addFilter("limit", (items, count) => items.slice(0, count));
  eleventyConfig.addFilter("others", (items, slug) => items.filter((item) => item.slug !== slug));
  eleventyConfig.addFilter("minPrice", (items) => Math.min(...items.map((item) => item.price)));
  // Places { lat, lng } on the OpenStreetMap base map, as percentages of its width and height.
  eleventyConfig.addFilter("mapPos", ({ lat, lng }) => ({
    left: (((lng - mapFrame.west) * mapFrame.kx) / mapFrame.width) * 100,
    top: (((mapFrame.north - lat) * mapFrame.ky) / mapFrame.height) * 100,
  }));

  return {
    dir: { input: "src", includes: "_includes", data: "_data", output: "_site" },
    htmlTemplateEngine: "njk",
    markdownTemplateEngine: "njk",
  };
}

// The Drive Moris "darkroom" grade: every photo gets the same look, so pictures from many
// photographers read as stills from one film.
//
//   tarmac shadows → warm grey mid-tones → road-white highlights, with sodium amber only in the
//   brightest highlights, a gentle S-curve, a slight vignette and fine grain.
//
// Reads src/images/photos/*.jpg (the credited originals) and writes src/images/graded/*.jpg.
// Unchanged photos are skipped, so rebuilding is quick.
import { existsSync } from "node:fs";
import { mkdir, readdir, stat } from "node:fs/promises";
import sharp from "sharp";

const SOURCE = "src/images/photos";
const OUTPUT = "src/images/graded";
const MAX_WIDTH = 2000;

const hex = (value) => [1, 3, 5].map((i) => parseInt(value.slice(i, i + 2), 16));
// Colour stops along the brightness scale (0 = black, 1 = white).
const STOPS = [
  [0.0, hex("#0c0d0e")],
  [0.22, hex("#1d1f21")],
  [0.5, hex("#6e685e")],
  [0.78, hex("#cfc9bb")],
  [0.93, hex("#efece4")],
  [1.0, hex("#fbe9c9")],
];

// 256-entry lookup table: brightness → graded colour.
const LUT = Array.from({ length: 256 }, (_, i) => {
  let t = i / 255;
  t = t * t * (3 - 2 * t) * 0.35 + t * 0.65; // gentle S-curve for punch
  const upper = STOPS.findIndex(([at]) => at >= t);
  const [a, ca] = STOPS[Math.max(0, upper - 1)];
  const [b, cb] = STOPS[upper];
  const k = b === a ? 0 : (t - a) / (b - a);
  return ca.map((c, j) => c + (cb[j] - c) * k);
});

async function grade(file) {
  const input = `${SOURCE}/${file}`;
  const output = `${OUTPUT}/${file}`;
  if (existsSync(output) && (await stat(output)).mtimeMs > (await stat(input)).mtimeMs) return false;

  const { data, info } = await sharp(input)
    .rotate()
    .resize({ width: MAX_WIDTH, withoutEnlargement: true })
    .greyscale()
    .raw()
    .toBuffer({ resolveWithObject: true });
  const { width, height } = info;
  const out = Buffer.alloc(width * height * 3);
  // Seeded noise, so every build produces identical files.
  let seed = 12345;
  const noise = () => ((seed = (seed * 1103515245 + 12345) & 0x7fffffff) / 0x7fffffff - 0.5) * 14;
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const dx = x / width - 0.5;
      const dy = y / height - 0.5;
      const vignette = 1 - Math.min(0.32, (dx * dx + dy * dy) * 0.75);
      const value = Math.max(0, Math.min(255, Math.round(data[y * width + x] * vignette + noise())));
      const colour = LUT[value];
      const o = (y * width + x) * 3;
      out[o] = colour[0];
      out[o + 1] = colour[1];
      out[o + 2] = colour[2];
    }
  }
  await sharp(out, { raw: { width, height, channels: 3 } }).jpeg({ quality: 86, mozjpeg: true }).toFile(output);
  return true;
}

await mkdir(OUTPUT, { recursive: true });
const files = (await readdir(SOURCE)).filter((name) => name.endsWith(".jpg"));
let graded = 0;
for (const file of files) if (await grade(file)) graded++;
console.log(`Graded ${graded} of ${files.length} photos into ${OUTPUT}/`);

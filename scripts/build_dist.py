#!/usr/bin/env python3
"""Zero-dependency build script for Smiling Critters 3D Sky & Airplane Adventure.

Generates:
1. GitHub Pages ready `docs/` directory (`docs/.nojekyll`, `docs/index.html`, `docs/manifest.json`, `docs/sw.js`, `docs/assets/`, `docs/vendor/`, `docs/src/`)
2. Self-contained single-file bundle `dist/index.html` (inlining CSS, Three.js r161, OrbitControls, base64 reference images, and all ES modules).
"""

import base64
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / 'docs'
DIST_DIR = ROOT / 'dist'


def strip_es_imports_and_exports(js_code: str) -> str:
  # Remove multi-line and single-line import statements
  js_code = re.sub(
      r'^\s*import\s+[\s\S]*?from\s+[\'"][^\'"]+[\'"];?\s*$',
      '',
      js_code,
      flags=re.MULTILINE,
  )
  # Remove per-module `const THREE = window.THREE;` so single-file bundle declares it once
  js_code = re.sub(
      r'^\s*const\s+THREE\s*=\s*window\.THREE\s*;\s*$',
      '',
      js_code,
      flags=re.MULTILINE,
  )
  # Replace `export class `, `export function `, `export const `, `export let `
  js_code = re.sub(
      r'^\s*export\s+(class|function|const|let|var)\s+',
      r'\1 ',
      js_code,
      flags=re.MULTILINE,
  )
  return js_code


def build_docs() -> None:
  DOCS_DIR.mkdir(parents=True, exist_ok=True)
  (DOCS_DIR / '.nojekyll').write_text('', encoding='utf-8')

  for fname in ['index.html', 'manifest.json', 'sw.js']:
    shutil.copy2(ROOT / fname, DOCS_DIR / fname)

  # Copy assets/, src/vendor/ -> docs/vendor/, and src/ -> docs/src/
  for sub in ['assets', 'src']:
    dst = DOCS_DIR / sub
    if dst.exists():
      shutil.rmtree(dst)
    shutil.copytree(ROOT / sub, dst)

  # Also mirror src/vendor to docs/vendor for direct relative lookup if needed
  docs_vendor = DOCS_DIR / 'vendor'
  if docs_vendor.exists():
    shutil.rmtree(docs_vendor)
  shutil.copytree(ROOT / 'src' / 'vendor', docs_vendor)


def build_single_file_dist() -> None:
  DIST_DIR.mkdir(parents=True, exist_ok=True)
  html = (ROOT / 'index.html').read_text(encoding='utf-8')
  css = (ROOT / 'src' / 'styles' / 'main.css').read_text(encoding='utf-8')
  three_js = (ROOT / 'src' / 'vendor' / 'three.min.js').read_text(encoding='utf-8')
  orbit_js = (ROOT / 'src' / 'vendor' / 'OrbitControls.js').read_text(encoding='utf-8')
  manifest_raw = (ROOT / 'manifest.json').read_text(encoding='utf-8')
  manifest_b64 = base64.b64encode(manifest_raw.encode('utf-8')).decode('ascii')

  fox_b64 = base64.b64encode(
      (ROOT / 'assets' / 'custom_critter_fox_lantern.jpg').read_bytes()
  ).decode('ascii')
  bat_b64 = base64.b64encode(
      (ROOT / 'assets' / 'custom_critter_bat_moonstar.jpg').read_bytes()
  ).decode('ascii')

  fox_data_uri = f'data:image/jpeg;base64,{fox_b64}'
  bat_data_uri = f'data:image/jpeg;base64,{bat_b64}'

  module_order = [
      ROOT / 'src' / 'audio' / 'soundSynth.js',
      ROOT / 'src' / 'characters' / 'materials.js',
      ROOT / 'src' / 'characters' / 'SunnyFox.js',
      ROOT / 'src' / 'characters' / 'LunaBat.js',
      ROOT / 'src' / 'characters' / 'animations.js',
      ROOT / 'src' / 'characters' / 'particles.js',
      ROOT / 'src' / 'aircraft' / 'aircraftFactory.js',
      ROOT / 'src' / 'aircraft' / 'contrailSystem.js',
      ROOT / 'src' / 'flight' / 'skyCourse.js',
      ROOT / 'src' / 'main.js',
  ]

  bundled_modules = []
  for mod_path in module_order:
    raw = mod_path.read_text(encoding='utf-8')
    cleaned = strip_es_imports_and_exports(raw)
    bundled_modules.append(f'// --- Module: {mod_path.name} ---\n{cleaned}')

  combined_app_js = (
      '(() => {\nconst THREE = window.THREE;\n'
      + '\n\n'.join(bundled_modules)
      + '\n})();'
  )

  # Inline manifest as data URI and remove external sw.js call in single-file bundle
  html = html.replace(
      '<link rel="manifest" href="./manifest.json" />',
      f'<link rel="manifest" href="data:application/manifest+json;base64,{manifest_b64}" />',
  )
  html = html.replace(
      "navigator.serviceWorker.register('./sw.js').catch(() => {});",
      '/* single-file dist bundle: service worker pre-inlined */',
  )

  # Inline CSS
  html = html.replace(
      '<link rel="stylesheet" href="./src/styles/main.css" />',
      f'<style>\n{css}\n</style>',
  )

  # Replace image URLs with base64 Data URIs
  html = html.replace('./assets/custom_critter_fox_lantern.jpg', fox_data_uri)
  html = html.replace('./assets/custom_critter_bat_moonstar.jpg', bat_data_uri)

  # Inline Three.js, OrbitControls, and bundled app JS
  html = html.replace(
      '<script src="./src/vendor/three.min.js"></script>',
      f'<script>\n{three_js}\n</script>',
  )
  html = html.replace(
      '<script src="./src/vendor/OrbitControls.js"></script>',
      f'<script>\n{orbit_js}\n</script>',
  )
  html = html.replace(
      '<script type="module" src="./src/main.js"></script>',
      f'<script>\n{combined_app_js}\n</script>',
  )

  out_file = DIST_DIR / 'index.html'
  out_file.write_text(html, encoding='utf-8')
  print(f'[build_dist] Built {DOCS_DIR} and {out_file} ({out_file.stat().st_size:,} bytes)')


if __name__ == '__main__':
  build_docs()
  build_single_file_dist()

"""Transfer the generated missing-target mark onto the inherited wall.

One-shot build helper. The input wall-v16.png is the imagegen draft; this
replaces it with a conservative composite and then advances wall.png.
"""
import hashlib
import importlib.util
import json
import math
from pathlib import Path


def load(name, filename):
    path = Path(__file__).with_name(filename)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def clamp(value):
    return max(0.0, min(1.0, value))


def segment_distance(x, y, start, end):
    dx, dy = end[0] - start[0], end[1] - start[1]
    t = clamp(((x - start[0]) * dx + (y - start[1]) * dy) / (dx * dx + dy * dy))
    return math.hypot(x - start[0] - t * dx, y - start[1] - t * dy)


def alpha_at(x, y):
    red = math.hypot((x - 617) / 23, (y - 905) / 22)
    pebble = clamp((1.08 - red) * 12)
    ring = math.hypot((x - 706) / 23, (y - 890) / 24)
    empty_target = clamp((0.20 - abs(ring - 1)) * 12)
    top = segment_distance(x, y, (636, 904), (679, 875))
    bottom = segment_distance(x, y, (636, 904), (685, 923))
    branches = max(clamp((7 - top) / 3), clamp((7 - bottom) / 3))
    return max(pebble, empty_target, branches)


def main():
    codec = load('png33', 'finish_wall22.py')
    jpeg = load('jpeg33', 'preview_jpeg27.py')
    ancestor = Path('artifacts/line-4/wall.png')
    draft_path = Path('artifacts/line-4/wall-v16.png')
    records = Path('dist/line-4')
    assert len(list(records.glob('[0-9][0-9].json'))) == 32
    old_bytes = ancestor.read_bytes()
    old_hash = hashlib.sha256(old_bytes).hexdigest()
    assert old_hash == '4941bc2d1e5fd827f4231afe34b3bcf51f106d8196a674dd61bb2ec108518017'
    assert json.loads((records / '32.json').read_text())['image'].endswith(old_hash)
    width, height, original = codec.read_png(old_bytes)
    dw, dh, draft = codec.read_png(draft_path)
    assert (width, height) == (dw, dh) == (1254, 1254)

    final = original[:]
    bounds = (589, 859, 737, 938)
    changed = []
    for y in range(bounds[1], bounds[3]):
        for x in range(bounds[0], bounds[2]):
            alpha = alpha_at(x, y)
            if alpha == 0:
                continue
            at = (y * width + x) * 3
            before = original[at:at + 3]
            for channel in range(3):
                final[at + channel] = round(before[channel] * (1 - alpha) +
                                            draft[at + channel] * alpha)
            if final[at:at + 3] != before:
                changed.append((x, y))
    assert changed
    assert all(bounds[0] <= x < bounds[2] and bounds[1] <= y < bounds[3]
               for x, y in changed)
    wall_hash = codec.write_png(draft_path, width, height, final)
    assert codec.read_png(draft_path)[2] == final
    ancestor.write_bytes(draft_path.read_bytes())

    preview = jpeg.encode(jpeg.resize(final, width, height), 512, 512, quality=40)
    assert len(preview) < 100_000
    (records / '33.jpg').write_bytes(preview)
    evidence = {
        'ancestor_sha256': old_hash, 'wall_sha256': wall_hash,
        'dimensions': [width, height], 'format': 'PNG', 'mode': 'RGB',
        'changed_pixels': len(changed),
        'changed_bounds_xyxy': [min(x for x, y in changed), min(y for x, y in changed),
                                max(x for x, y in changed), max(y for x, y in changed)],
        'changed_pixels_outside_mark_region': 0,
        'method': 'Only the image-generated pebble, branches and empty ring are blended; all pixels elsewhere match the ancestor.',
        'preview': {'dimensions': [512, 512], 'format': 'JPEG', 'bytes': len(preview)},
        'unmet_visual_requirements': []
    }
    Path('line-4/IMAGE-33.json').write_text(json.dumps(evidence, indent=2) + '\n')
    record = {
        'name': 'The Missing Stone',
        'image': 'https://api.imd.fun/artifacts/' + wall_hash,
        'attributes': [
            {'trait_type': 'Cave', 'value': 'Crystal'},
            {'trait_type': 'Wall', 'value': 'Line 4'},
            {'trait_type': 'Number', 'value': 33},
            {'trait_type': 'Left behind', 'value': 'Catalog Health'},
            {'trait_type': 'Meaning', 'value': 'A forked path exposes the empty place where a needed stone should be.'},
            {'trait_type': 'One thing', 'value': 'Finite offline dependency resolution'}]
    }
    (records / '33.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(evidence, indent=2))


if __name__ == '__main__':
    main()

"""Reproduce the frozen fixture through production writer and shared template."""
import json
from pathlib import Path
from enotcheck.render import content_from_snapshot, write_bundle


def main():
    root = Path(__file__).resolve().parent
    state = json.loads((root / 'evidence/accepted-state.json').read_text())
    content = content_from_snapshot(state)
    result = write_bundle(root / 'evidence/bundle', content, asset_directory=root / 'evidence/assets')
    repo = root.parents[2]
    (repo / 'design-preview.html').write_text(result['html'], encoding='utf-8')
    print(json.dumps({k: result[k] for k in ('archive_path', 'snapshot_path', 'zip_created', 'media_count', 'media_lane')}, ensure_ascii=False))


if __name__ == '__main__':
    main()

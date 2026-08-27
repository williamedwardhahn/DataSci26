"""Post-build pass: replace URLs in the archive that have gone dead.

Applied after modernize.py. Idempotent. Covers labs/*.ipynb and interactive/*.html.
Each entry records what died and what replaced it, so the next rot is easy to audit.
"""
import glob, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

WM = 'https://upload.wikimedia.org/wikipedia/commons'

# dead URL -> (replacement, why)
REPLACE = {
    # host gone; this one is loaded by io.imread, so the lab breaks without it
    # NB: this one is fetched by io.imread, so the replacement host must serve a
    # plain urllib request. upload.wikimedia.org 403s a default Python User-Agent,
    # so it is only safe for <img> tags the browser loads, never for imread.
    'http://harborparkgarage.com/img/venues/pix/aquarium2.jpg':
        ('https://raw.githubusercontent.com/opencv/opencv/master/samples/data/butterfly.jpg',
         'host dead (404)'),
    # Stack Exchange CDN now refuses non-browser and hotlinked requests (403)
    'https://i.stack.imgur.com/XBWc3.png':
        (f'{WM}/thumb/1/16/Alexnet.png/1280px-Alexnet.png', 'imgur CDN 403'),
    'https://i.stack.imgur.com/fXqXs.png':
        (f'{WM}/d/d3/Loss_Functions_for_training_ANNs.png', 'imgur CDN 403'),
    # paperswithcode was retired; media host no longer resolves
    'https://production-media.paperswithcode.com/methods/MaxpoolSample2.png':
        (f'{WM}/e/e9/Max_pooling.png', 'paperswithcode retired'),
    # Wikimedia now rejects arbitrary thumbnail widths; 1280 is an allowed size
    f'{WM}/thumb/2/2a/Human_faces.jpg/1200px-Human_faces.jpg':
        (f'{WM}/thumb/2/2a/Human_faces.jpg/1280px-Human_faces.jpg',
         'Wikimedia thumbnail width restricted'),
    # file removed from Commons entirely
    f'{WM}/thumb/5/5f/Manhattan3_amk.jpg/1280px-Manhattan3_amk.jpg':
        (f'{WM}/thumb/b/b6/Lower_Manhattan_from_Jersey_City_November_2014_panorama_3.jpg'
         '/1280px-Lower_Manhattan_from_Jersey_City_November_2014_panorama_3.jpg',
         'file deleted from Commons'),
}

# (old, new, why) for edits that are not a bare URL swap
REWRITE = [
    ("labels = {int(key):value for (key, value) in requests.get(LABELS_URL).json().items()}",
     "labels = {i: name for i, name in enumerate(requests.get(LABELS_URL).json())}",
     'new labels source is a list, not a dict'),
    ("requests.get('https://s3.amazonaws.com/mlpipes/pytorch-quick-start/labels.json')",
     "requests.get('https://raw.githubusercontent.com/anishathalye/imagenet-simple-labels"
     "/master/imagenet-simple-labels.json')",
     'mlpipes S3 bucket now 403s (inline)'),
    ("LABELS_URL = 'https://s3.amazonaws.com/mlpipes/pytorch-quick-start/labels.json'",
     "LABELS_URL = 'https://raw.githubusercontent.com/anishathalye/imagenet-simple-labels"
     "/master/imagenet-simple-labels.json'",
     'mlpipes S3 bucket now 403s'),
]


def patch(text):
    hits = []
    for old, (new, why) in REPLACE.items():
        if old in text:
            text = text.replace(old, new)
            hits.append(why)
    for old, new, why in REWRITE:
        if old in text:
            text = text.replace(old, new)
            hits.append(why)
    return text, hits


def main():
    total = 0
    for p in sorted(glob.glob(os.path.join(ROOT, 'labs', '*.ipynb'))):
        nb = json.load(open(p))
        touched = []
        for i, c in enumerate(nb['cells']):
            new, hits = patch(''.join(c['source']))
            if hits:
                c['source'] = new.splitlines(keepends=True)
                touched.append((i, hits))
        if touched:
            json.dump(nb, open(p, 'w'), indent=1)
            total += len(touched)
            print(f'  {os.path.basename(p)}')
            for i, hits in touched:
                print(f'     cell {i:3}: ' + '; '.join(hits))

    for p in sorted(glob.glob(os.path.join(ROOT, 'interactive', '*.html'))):
        s = open(p).read()
        new, hits = patch(s)
        if hits:
            open(p, 'w').write(new)
            total += 1
            print(f'  {os.path.basename(p)}: ' + '; '.join(sorted(set(hits))))
    print(f'\n{total} locations repaired')


if __name__ == '__main__':
    main()

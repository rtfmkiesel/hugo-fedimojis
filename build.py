import requests
from argparse import ArgumentParser
from base64 import b64encode
from urllib.parse import urlparse
from os.path import splitext, exists
from pathvalidate import sanitize_filename
from jinja2 import Template
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from io import BytesIO
import time

SHORTCODE_TEMPLATE = '<img generator="github.com/rtfmkiesel/hugo-fedimojis" class="{{ cssclass }}" alt="{{ name }}" src="data:{{ mimetype }};base64,{{ base64 }}" />'
MAX_WORKERS = 20
RETRY_AFTER_DEFAULT = 30
MAX_RETRIES = 5


def create_hugo_shortcode(name: str, outpath: str, img_data: bytes, mime: str, args):
    try:
        tmpl = Template(SHORTCODE_TEMPLATE)
        shortcode_rendered = tmpl.render(
            cssclass=args.cssclass,
            name=name,
            mimetype=mime,
            base64=b64encode(img_data).decode(),
        )
        with open(outpath, "w") as outfile:
            outfile.write(shortcode_rendered)
    except Exception as e:
        print(f"[ERROR] Could not create shortcode for '{name}': {e}")


def get_ext_and_mime_from_url(url: str):
    parsed = urlparse(url)
    _, ext = splitext(parsed.path)
    ext = ext.lower()
    if ext == ".gif":
        return ext, "image/gif"
    else:
        return ext, "image/png"


def download_and_generate(name, url: str, args, pbar):
    ext, mime = get_ext_and_mime_from_url(url)

    shortcode_filename = sanitize_filename(f"{args.shortcodeprefix}{name}.html")
    shortcode_path = f"./layouts/shortcodes/{shortcode_filename}"
    if exists(shortcode_path):
        pbar.update(1)
        return

    attempts = 0
    while attempts < MAX_RETRIES:
        try:
            response = requests.get(url, timeout=10, stream=True)
            if response.status_code == 200:
                img_data = BytesIO()
                for chunk in response.iter_content(chunk_size=8192):
                    img_data.write(chunk)
                create_hugo_shortcode(
                    name, shortcode_path, img_data.getvalue(), mime, args
                )
                break
            elif response.status_code == 429:
                retry_after = int(
                    response.headers.get("Retry-After", RETRY_AFTER_DEFAULT)
                )
                print(f"[RATE LIMIT] '{name}' - waiting {retry_after}s...")
                time.sleep(retry_after)
            elif 400 <= response.status_code < 600:
                print(f"[ERROR] HTTP {response.status_code} for '{name}', skipping.")
                break
            else:
                print(f"[WARN] Unexpected HTTP {response.status_code} for '{name}'")
                break
        except Exception as e:
            print(f"[ERROR] Failed to download '{name}': {e}")
            break
        attempts += 1

    pbar.update(1)


def scrape(url: str, args):
    emoji_api_url = f"{url.rstrip('/')}/api/v1/custom_emojis"
    try:
        response = requests.get(emoji_api_url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"[ERROR] Could not fetch emoji list: {e}")
        exit(1)

    emojis = response.json()
    print(f"[INFO] Found {len(emojis)} custom emojis.")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        with tqdm(total=len(emojis), desc="Generating", unit="emoji") as pbar:
            futures = []
            for emoji in emojis:
                name = emoji.get("shortcode")
                url = emoji.get("url")
                if not name or not url:
                    pbar.update(1)
                    continue
                futures.append(
                    executor.submit(download_and_generate, name, url, args, pbar)
                )

            for future in as_completed(futures):
                future.result()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "-u", "--mastodonurl", required=True, help="Mastodon URL to scrape for emojis"
    )
    parser.add_argument(
        "-c", "--cssclass", default="fm", help="CSS class to apply to emojis"
    )
    parser.add_argument(
        "-p", "--shortcodeprefix", default="fm-", help="Prefix for Hugo shortcodes"
    )
    args = parser.parse_args()
    scrape(args.mastodonurl, args)

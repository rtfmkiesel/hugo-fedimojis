import requests
from argparse import ArgumentParser
from shutil import copyfileobj
from base64 import b64encode
from urllib.parse import urlparse
from os.path import splitext, exists
from pathvalidate import sanitize_filename
from jinja2 import Template


hugo_shortcode_template = '<img class="{{ cssclass }}" alt="{{ name }}" src="data:{{ mimetype }};base64,{{ base64 }}" />'


def create_hugo_shortcode(name, emoji_path: str):
    hugo_shortcode_filename = sanitize_filename(f"{args.shortcodeprefix}{name}.html")
    hugo_shortcode_filepath = f"./layouts/shortcodes/{hugo_shortcode_filename}"
    if exists(hugo_shortcode_filepath):
        print(f"Skipping '{hugo_shortcode_filename}': already created")
    else:
        try:
            with open(emoji_path, "rb") as infile:
                shortcode_base64 = b64encode(infile.read())
                if emoji_path.endswith(".gif"):
                    shortcode_mimetype = "image/gif"
                else:
                    shortcode_mimetype = "image/png"

            with open(hugo_shortcode_filepath, "w") as outfile:
                tmpl = Template(hugo_shortcode_template)
                shortcode_rendered = tmpl.render(
                    cssclass=args.cssclass,
                    name=name,
                    mimetype=shortcode_mimetype,
                    base64=shortcode_base64.decode(),
                )
                outfile.write(shortcode_rendered)
                print(f"Created '{hugo_shortcode_filename}'")

        except Exception as e:
            print(f"Error during creation of '{hugo_shortcode_filename}': {e}")
            return


# taken from https://stackoverflow.com/a/28310024
def get_ext_from_url(url: str):
    parsed = urlparse(url)
    root, ext = splitext(parsed.path)
    return ext


def download_image(name, url: str):
    emoji_fileext = get_ext_from_url(url)
    emoji_filename = sanitize_filename(f"{name}{emoji_fileext}")
    emoji_filepath = f"./images/{emoji_filename}"
    if exists(emoji_filepath):
        print(f"Skipping '{name}': already downloaded")
    else:
        try:
            response = requests.get(url, timeout=5, stream=True)
            if response.status_code == 200:
                with open(emoji_filepath, "wb") as outfile:
                    copyfileobj(response.raw, outfile)
                    print(f"Saved '{emoji_filename}'")
            else:
                print(
                    f"Error during download of '{emoji_filename}': status code {response.status_code}"
                )
        except Exception as e:
            print(f"Error saving '{emoji_filename}': {e}")

    create_hugo_shortcode(name, emoji_filepath)


def scrape(url: str):
    emoji_api_url = f"{url.rstrip('/')}/api/v1/custom_emojis"
    response = requests.get(emoji_api_url, timeout=5)
    if response.status_code != 200:
        print(f"Error fetching emoji list: status code {response.status_code}")
        quit(1)

    for custom_emoji in response.json():
        name = custom_emoji["shortcode"]
        try:
            download_url = custom_emoji["url"]
        except KeyError:
            print(f"Skipping '{name}': no 'url' key specified in JSON")
            continue

        download_image(name, download_url)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "-u", "--mastodonurl", required=True, help="Mastodon URL to scrape for emojis"
    )
    parser.add_argument(
        "-c",
        "--cssclass",
        required=False,
        help="Which CSS class to give the emojis",
        default="fedimoji",
    )
    parser.add_argument(
        "-p",
        "--shortcodeprefix",
        required=False,
        help="Which prefix to give the Hugo shortcodes",
        default="fm-",
    )
    args = parser.parse_args()
    scrape(args.mastodonurl)

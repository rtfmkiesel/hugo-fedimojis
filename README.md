# hugo-fedimojis

A [Hugo](https://gohugo.io/) module to add Mastodon emojis as shortcodes. This repo uses the [custom emojis](https://emojos.in/infosec.exchange?show_animated=true) of [infosec.exchange](https://infosec.exchange/), the instance where I have my account. 

*This was hacked together in like 2,5 hours, please have mercy*

## Usage

### Setup

Inside your hugo config add the following snippet and then run `hugo mod get`.

```yaml
module:
  imports:
    - path: "github.com/rtfmkiesel/hugo-fedimojis"
```

### Inserting Emojis

Inside your content, reference the emojis with a shortcode like the following:

```md
{{< fm-ablobcatrave >}}
```

### Styling
I can recommend the following CSS to make them fit nicely inside a sentence:
```css
.fm {
  display: inline;
  max-width: 1rem;
  max-height: 1rem;
  margin: 0;
  padding: 0;
  border: none;
}
```

### Local

You can use this module locally with emojis from your preferred Mastodon instance. 

```sh
git clone https://github.com/rtfmkiesel/hugo-fedimojis
cd hugo-fedimojis

# Clear out the current ones
rm -rf layouts/shortcodes/*.html

# Build the Hugo shortcodes
python3 build.py -u <YOUR MASTODON URL>
```

Then add the module in hugo's config with:

```yaml
module:
  imports:
    - path: "github.com/rtfmkiesel/hugo-fedimojis"
```

Run `hugo mod get`. Afterwards, modify `go.mod` by adding the following line below the `module` line. Make sure to change `/PATH/TO/YOUR/LOCAL/MODULE`. For mroe information, check out [gomod-ref#replace](https://go.dev/doc/modules/gomod-ref#replace).

```
replace github.com/rtfmkiesel/hugo-fedimojis => /PATH/TO/YOUR/LOCAL/MODULE
```
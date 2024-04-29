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
.fedimoji {
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
rm -rf images/*
rm -rf layouts/shortcodes/*.html

# Build the Hugo shortcodes
python3 build.py -u <YOUR MASTODON URL>
```

Then add the module with:

`hugo/config.yaml`
```yaml
module:
  imports:
    - path: "github.com/rtfmkiesel/hugo-fedimojis"
```

`hugo/go.mod` (Create if not already present)
```
module github.com/<YOU>/<YOURBLOG>

replace github.com/rtfmkiesel/hugo-fedimojis => <ABS PATH TO YOUR LOCAL MODULE>

go 1.XXX

require github.com/rtfmkiesel/hugo-fedimojis xxxxxx
```
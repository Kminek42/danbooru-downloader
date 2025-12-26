# Danbooru Image Downloader

A Python-based scraping tool designed to download images and associated metadata (tags and ratings) from Danbooru based on specific search configurations.

## Features

- **Tag-based Scraping**: Download images using single or multiple tag combinations.
- **Metadata Extraction**: Saves the rating (General, Sensitive, Questionable, Explicit) and all tags for every image in a JSON database.
- **Duplicate Prevention**: Checks existing metadata to avoid re-downloading the same post twice.
- **Config Driven**: Manage multiple search queries and local directory settings via a single JSON file.

---

## Project Structure

```
.
├── config.json              # Configuration for tags and save paths
├── danbooru_downloader.py   # Main execution script
├── downloads/               # Default directory for saved images
└── requirements.txt         # Python dependencies
```

---

## Installation

1. **Clone or download** this repository.
2. **Install dependencies** using pip:
   ```bash
   pip install -r requirements.txt
   ```

---

## Configuration

The script relies on a `config.json` file to define what to download and where to save it.

### Example `config.json`

```json
{
  "settings": {
    "images_dir": "downloads",
    "data_path": "metadata.json"
  },
  "searches": [
    {
      "tags": ["landscape", "high_res"],
      "pages": 5
    },
    {
      "tags": ["cyberpunk"],
      "pages": 2
    }
  ]
}
```

- **settings**:
  - `images_dir`: Folder where `.jpg` files will be stored.
  - `data_path`: The JSON file that stores metadata for all downloaded images.
- **searches**: A list of search objects. Each contains a list of `tags` and the number of `pages` to crawl.

---

## Usage

Run the script from your terminal:

```bash
python danbooru_downloader.py config.json
```

---

## Metadata Format

The `metadata.json` (or your configured `data_path`) will be structured as follows:

```json
{
  "1234567": {
    "link": "https://danbooru.donmai.us/posts/1234567",
    "rating": "General",
    "tags": ["scenery", "clouds", "sunlight"]
  }
}
```

## Requirements

- `beautifulsoup4`
- `requests`

> **Note:** This scraper is intended for personal use and archival purposes. Please respect Danbooru's `robots.txt` and rate limiting policies.

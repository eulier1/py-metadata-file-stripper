from PIL import Image
from PIL.ExifTags import TAGS
import sys

def has_metadata(image_path: str) -> dict:
    """Return a dict of any metadata found. Empty dict = clean."""
    img = Image.open(image_path)
    found = {}

    # 1. EXIF (JPEG / some PNG)
    exif = img.getexif()
    if exif:
        for tag_id, value in exif.items():
            tag_name = TAGS.get(tag_id, tag_id)
            # Skip very common harmless tags if you want
            if tag_name not in ("Orientation", "XResolution", "YResolution", "ResolutionUnit"):
                found[f"EXIF:{tag_name}"] = str(value)[:100]

    # 2. PNG text chunks / info
    if img.format == "PNG" and hasattr(img, "text") and img.text:
        for key, value in img.text.items():
            found[f"PNG:{key}"] = str(value)[:100]

    # 3. ICC profile
    if "icc_profile" in img.info:
        found["ICC_Profile"] = f"{len(img.info['icc_profile'])} bytes"

    # 4. Other info keys that often carry metadata
    interesting_keys = ("comment", "description", "software", "author", "copyright")
    for key in interesting_keys:
        if key in img.info:
            found[key] = str(img.info[key])[:100]

    return found

def strip_metadata(input_path: str, output_path: str):
    img = Image.open(input_path)
    # Save without metadata
    img.save(output_path, "PNG")
    print(f"Saved clean image → {output_path}")

def cmd_check() :
    if len(sys.argv) < 3:
        print("Usage: uv run mfs check <image.png>")
        sys.exit(1)
    
    path = sys.argv[2]
    meta = has_metadata(path)
    if not meta:
         print(f"✅ {path} has no metadata")
    else:
        print(f"⚠️  Metadata found in {path}:")
        for k, v in meta.items():
            print(f"  {k}: {v}")

def print_usages() : 
    print("Usage:")
    print("  uv run mfs check <image.png>")
    # Todo
    # print("  uv run mfs strip <input.png> [output.png]")

def main():
    COMMANDS : dict [ str : function ] = {
        "check" : cmd_check,
    }

    if len(sys.argv) < 2:
        print_usages()
        sys.exit(1)

    command = sys.argv[1]
    handler = COMMANDS.get(command)

    if handler is None: 
        print_usages()
        sys.exit()

    handler()

if __name__ == "__main__":
    main()
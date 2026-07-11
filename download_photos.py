# download_photos.py
# ─────────────────────────────────────────────────────────
# Downloads 200 curated cybersecurity photos from Unsplash
# Organized by category for CyberNews article images
# ─────────────────────────────────────────────────────────

import os
import sys
import time
import requests
from pathlib import Path

BASE = Path("static/images/photos")

# ── Curated photo URLs by category ────────────────────
# Each URL is a PERMANENT direct Unsplash link
# They won't break or change over time

PHOTOS = {
    "malware": [
        "photo-1614064641938-3bbee52942c7",
        "photo-1526374965328-7f61d4dc18c5",
        "photo-1555949963-ff9fe0c870eb",
        "photo-1633356122544-f134324a6cee",
        "photo-1629654297299-c8506221ca97",
        "photo-1580894894513-541e068a3e2b",
        "photo-1504639725590-34d0984388bd",
        "photo-1562813733-b31f71025d54",
        "photo-1560732488-6b0df240254a",
        "photo-1551808525-51a94da548ce",
        "photo-1542831371-29b0f74f9713",
        "photo-1544197150-b99a580bb7a8",
        "photo-1563206767-5b18f218e8de",
        "photo-1597733336794-12d05021d510",
        "photo-1515879218367-8466d910adf9",
        "photo-1550745165-9bc0b252726f",
        "photo-1603791440277-08145aedbe45",
        "photo-1623479322729-28b25c16b011",
        "photo-1583508915901-b5f84c1dcde1",
        "photo-1510915228340-29c85a43dcfe",
        "photo-1544890225-2f3faec4cd60",
        "photo-1587620962725-abab7fe55159",
        "photo-1518432031352-d6fc5c10da5a",
        "photo-1496096265110-f83ad7f96608",
        "photo-1525547719571-a2d4ac8945e2",
        "photo-1573164713714-d95e436ab8d6",
        "photo-1516321165247-4aa89a48be28",
        "photo-1483058712412-4245e9b90334",
    ],
    "breaches": [
        "photo-1563986768609-322da13575f3",
        "photo-1516321318423-f06f85e504b3",
        "photo-1558494949-ef010cbdcc31",
        "photo-1544197150-b99a580bb7a8",
        "photo-1451187580459-43490279c0fa",
        "photo-1518770660439-4636190af475",
        "photo-1488590528505-98d2b5aba04b",
        "photo-1573804633927-bfcbcd909acd",
        "photo-1461749280684-dccba630e2f6",
        "photo-1550745165-9bc0b252726f",
        "photo-1510511459019-5dda7724fd87",
        "photo-1550751827-4bd374c3f58b",
        "photo-1504711434969-e33886168f5c",
        "photo-1526374965328-7f61d4dc18c5",
        "photo-1597733336794-12d05021d510",
        "photo-1563206767-5b18f218e8de",
        "photo-1542831371-29b0f74f9713",
        "photo-1515879218367-8466d910adf9",
        "photo-1432821596592-e2c18b78144f",
        "photo-1507925921958-8a62f3d1a50d",
        "photo-1614064641938-3bbee52942c7",
        "photo-1483389127117-b6a2102724ae",
        "photo-1484417894086-9e30f40f1059",
        "photo-1557597774-9d273605dfa9",
        "photo-1555949963-ff9fe0c870eb",
        "photo-1580894894513-541e068a3e2b",
        "photo-1504639725590-34d0984388bd",
        "photo-1562813733-b31f71025d54",
        "photo-1560732488-6b0df240254a",
    ],
    "vulnerabilities": [
        "photo-1550751827-4bd374c3f58b",
        "photo-1607799279861-4dd421887fb3",
        "photo-1635070041078-e363dbe005cb",
        "photo-1510511459019-5dda7724fd87",
        "photo-1504711434969-e33886168f5c",
        "photo-1597733336794-12d05021d510",
        "photo-1563206767-5b18f218e8de",
        "photo-1542831371-29b0f74f9713",
        "photo-1515879218367-8466d910adf9",
        "photo-1504639725590-34d0984388bd",
        "photo-1614064641938-3bbee52942c7",
        "photo-1526374965328-7f61d4dc18c5",
        "photo-1555949963-ff9fe0c870eb",
        "photo-1633356122544-f134324a6cee",
        "photo-1629654297299-c8506221ca97",
        "photo-1580894894513-541e068a3e2b",
        "photo-1562813733-b31f71025d54",
        "photo-1560732488-6b0df240254a",
        "photo-1551808525-51a94da548ce",
        "photo-1544197150-b99a580bb7a8",
        "photo-1518770660439-4636190af475",
        "photo-1488590528505-98d2b5aba04b",
        "photo-1573804633927-bfcbcd909acd",
        "photo-1461749280684-dccba630e2f6",
        "photo-1550745165-9bc0b252726f",
        "photo-1451187580459-43490279c0fa",
        "photo-1558494949-ef010cbdcc31",
        "photo-1563986768609-322da13575f3",
    ],
    "privacy": [
        "photo-1557597774-9d273605dfa9",
        "photo-1484417894086-9e30f40f1059",
        "photo-1483389127117-b6a2102724ae",
        "photo-1423592707957-3b212afa6733",
        "photo-1555949963-ff9fe0c870eb",
        "photo-1507925921958-8a62f3d1a50d",
        "photo-1432821596592-e2c18b78144f",
        "photo-1526374965328-7f61d4dc18c5",
        "photo-1516321318423-f06f85e504b3",
        "photo-1563206767-5b18f218e8de",
        "photo-1510511459019-5dda7724fd87",
        "photo-1550751827-4bd374c3f58b",
        "photo-1504711434969-e33886168f5c",
        "photo-1597733336794-12d05021d510",
        "photo-1542831371-29b0f74f9713",
        "photo-1515879218367-8466d910adf9",
        "photo-1518770660439-4636190af475",
        "photo-1488590528505-98d2b5aba04b",
        "photo-1573804633927-bfcbcd909acd",
        "photo-1461749280684-dccba630e2f6",
        "photo-1451187580459-43490279c0fa",
        "photo-1558494949-ef010cbdcc31",
        "photo-1563986768609-322da13575f3",
        "photo-1544197150-b99a580bb7a8",
        "photo-1614064641938-3bbee52942c7",
        "photo-1629654297299-c8506221ca97",
        "photo-1580894894513-541e068a3e2b",
        "photo-1504639725590-34d0984388bd",
    ],
    "threats": [
        "photo-1550751827-4bd374c3f58b",
        "photo-1558494949-ef010cbdcc31",
        "photo-1555949963-ff9fe0c870eb",
        "photo-1451187580459-43490279c0fa",
        "photo-1504711434969-e33886168f5c",
        "photo-1614064641938-3bbee52942c7",
        "photo-1597733336794-12d05021d510",
        "photo-1542831371-29b0f74f9713",
        "photo-1563986768609-322da13575f3",
        "photo-1629654297299-c8506221ca97",
        "photo-1526374965328-7f61d4dc18c5",
        "photo-1510511459019-5dda7724fd87",
        "photo-1607799279861-4dd421887fb3",
        "photo-1635070041078-e363dbe005cb",
        "photo-1551808525-51a94da548ce",
        "photo-1560732488-6b0df240254a",
        "photo-1562813733-b31f71025d54",
        "photo-1580894894513-541e068a3e2b",
        "photo-1504639725590-34d0984388bd",
        "photo-1633356122544-f134324a6cee",
        "photo-1544197150-b99a580bb7a8",
        "photo-1518770660439-4636190af475",
        "photo-1488590528505-98d2b5aba04b",
        "photo-1573804633927-bfcbcd909acd",
        "photo-1461749280684-dccba630e2f6",
        "photo-1550745165-9bc0b252726f",
        "photo-1563206767-5b18f218e8de",
        "photo-1515879218367-8466d910adf9",
    ],
    "research": [
        "photo-1544197150-b99a580bb7a8",
        "photo-1518770660439-4636190af475",
        "photo-1488590528505-98d2b5aba04b",
        "photo-1461749280684-dccba630e2f6",
        "photo-1550745165-9bc0b252726f",
        "photo-1607799279861-4dd421887fb3",
        "photo-1515879218367-8466d910adf9",
        "photo-1573804633927-bfcbcd909acd",
        "photo-1504639725590-34d0984388bd",
        "photo-1562813733-b31f71025d54",
        "photo-1451187580459-43490279c0fa",
        "photo-1558494949-ef010cbdcc31",
        "photo-1563986768609-322da13575f3",
        "photo-1550751827-4bd374c3f58b",
        "photo-1526374965328-7f61d4dc18c5",
        "photo-1555949963-ff9fe0c870eb",
        "photo-1614064641938-3bbee52942c7",
        "photo-1597733336794-12d05021d510",
        "photo-1563206767-5b18f218e8de",
        "photo-1542831371-29b0f74f9713",
        "photo-1510511459019-5dda7724fd87",
        "photo-1504711434969-e33886168f5c",
        "photo-1635070041078-e363dbe005cb",
        "photo-1629654297299-c8506221ca97",
        "photo-1580894894513-541e068a3e2b",
        "photo-1560732488-6b0df240254a",
        "photo-1551808525-51a94da548ce",
        "photo-1633356122544-f134324a6cee",
    ],
    "general": [
        "photo-1550751827-4bd374c3f58b",
        "photo-1526374965328-7f61d4dc18c5",
        "photo-1555949963-ff9fe0c870eb",
        "photo-1563986768609-322da13575f3",
        "photo-1510511459019-5dda7724fd87",
        "photo-1614064641938-3bbee52942c7",
        "photo-1451187580459-43490279c0fa",
        "photo-1558494949-ef010cbdcc31",
        "photo-1504711434969-e33886168f5c",
        "photo-1597733336794-12d05021d510",
        "photo-1518770660439-4636190af475",
        "photo-1488590528505-98d2b5aba04b",
        "photo-1573804633927-bfcbcd909acd",
        "photo-1461749280684-dccba630e2f6",
        "photo-1550745165-9bc0b252726f",
        "photo-1607799279861-4dd421887fb3",
        "photo-1515879218367-8466d910adf9",
        "photo-1563206767-5b18f218e8de",
        "photo-1542831371-29b0f74f9713",
        "photo-1544197150-b99a580bb7a8",
        "photo-1635070041078-e363dbe005cb",
        "photo-1629654297299-c8506221ca97",
        "photo-1580894894513-541e068a3e2b",
        "photo-1504639725590-34d0984388bd",
        "photo-1562813733-b31f71025d54",
        "photo-1560732488-6b0df240254a",
        "photo-1551808525-51a94da548ce",
        "photo-1633356122544-f134324a6cee",
        "photo-1516321318423-f06f85e504b3",
    ],
}


def download_photo(photo_id, save_path, width=800):
    """Download one photo from Unsplash."""
    url = f"https://images.unsplash.com/{photo_id}?w={width}&q=80"
    try:
        r = requests.get(url, timeout=15, stream=True)
        if r.status_code == 200 and len(r.content) > 1000:
            with open(save_path, 'wb') as f:
                f.write(r.content)
            return True
        return False
    except Exception:
        return False


def main():
    total = 0
    failed = 0
    skipped = 0

    for category, photo_ids in PHOTOS.items():
        folder = BASE / category
        folder.mkdir(parents=True, exist_ok=True)

        print(f"\n{'=' * 40}")
        print(f"  {category.upper()} ({len(photo_ids)} photos)")
        print(f"{'=' * 40}")

        for i, photo_id in enumerate(photo_ids, 1):
            filename = f"{i:02d}.jpg"
            save_path = folder / filename

            # Skip if already downloaded
            if save_path.exists() and save_path.stat().st_size > 1000:
                print(f"  SKIP {filename} (already exists)")
                skipped += 1
                total += 1
                continue

            success = download_photo(photo_id, save_path)

            if success:
                size_kb = save_path.stat().st_size / 1024
                print(f"  ✓ {filename} ({size_kb:.0f} KB)")
                total += 1
            else:
                print(f"  ✗ {filename} FAILED")
                failed += 1

            # Small delay between downloads
            time.sleep(0.3)

    # Download fallback
    fb_path = Path("static/images/fallback/cyber-default.jpg")
    fb_path.parent.mkdir(parents=True, exist_ok=True)
    if not fb_path.exists():
        download_photo("photo-1550751827-4bd374c3f58b", fb_path)
        print("\n  ✓ Fallback image downloaded")

    print(f"\n{'=' * 40}")
    print(f"  DOWNLOAD COMPLETE")
    print(f"{'=' * 40}")
    print(f"  Downloaded: {total}")
    print(f"  Skipped:    {skipped}")
    print(f"  Failed:     {failed}")

    # Show disk usage
    total_size = sum(
        f.stat().st_size
        for f in BASE.rglob("*.jpg")
        if f.is_file()
    )
    print(f"  Total size: {total_size / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    main()

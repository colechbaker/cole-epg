import gzip
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

# --- Settings ---
SOURCE_URL = "https://epgshare01.online/epgshare01/epg_ripper_US1.xml.gz"
OUTPUT_FILE = "epg.xml"

# Hulu + Live TV lineup (Chicago/Manteno area)
CHANNELS_TO_KEEP = [
    # Locals
    "WLS", "WBBM", "WMAQ", "WFLD", "CW", "PBS",

    # Sports
    "ESPN", "ESPN2", "ESPNews", "ESPNU", "FS1", "FS2", "Big Ten",
    "SEC Network", "ACC Network", "NFL Network", "Golf Channel",

    # News
    "CNN", "Fox News", "MSNBC", "CNBC", "HLN", "Bloomberg",
    "The Weather Channel",

    # Entertainment / General
    "USA", "TBS", "TNT", "FX", "FXX", "FXM",
    "Comedy Central", "Paramount Network", "AMC", "A&E",
    "Bravo", "E!", "Syfy", "TruTV", "Lifetime",
    "History", "National Geographic", "Nat Geo Wild",
    "Discovery", "Animal Planet", "HGTV", "Food Network",
    "Travel Channel", "Oxygen", "ID",

    # Kids / Family
    "Disney Channel", "Disney Junior", "Disney XD",
    "Cartoon Network", "Freeform", "Universal Kids", "Nickelodeon",
    "Nick Jr", "TeenNick",

    # Movies / Specials
    "Reelz", "TCM",

    # Music / Lifestyle
    "MTV", "MTV2", "VH1", "CMT", "BET",

    # Other popular
    "Hallmark Channel", "Hallmark Movies & Mysteries", "Hallmark Drama"
]

DAYS_AHEAD = 3
# ----------------

print("Downloading source EPG...")
resp = requests.get(SOURCE_URL)
resp.raise_for_status()

# Decompress gzip
xml_data = gzip.decompress(resp.content)

# Parse XML
root = ET.fromstring(xml_data)

# Time cutoff
cutoff = datetime.utcnow() + timedelta(days=DAYS_AHEAD)

# Filter channels
channels = []
programmes = []

for ch in root.findall("channel"):
    name = "".join(ch.find("display-name").itertext()) if ch.find("display-name") is not None else ""
    if any(key.lower() in name.lower() for key in CHANNELS_TO_KEEP):
        channels.append(ch)

for prog in root.findall("programme"):
    start_time = prog.attrib.get("start")
    if start_time:
        dt = datetime.strptime(start_time[:14], "%Y%m%d%H%M%S")
        if dt <= cutoff:
            chan_id = prog.attrib.get("channel")
            if any(chan.attrib["id"] == chan_id for chan in channels):
                programmes.append(prog)

# Build new tree
new_root = ET.Element("tv")
for ch in channels:
    new_root.append(ch)
for prog in programmes:
    new_root.append(prog)

tree = ET.ElementTree(new_root)
tree.write(OUTPUT_FILE, encoding="utf-8", xml_declaration=True)

print(f"Trimmed Hulu Live TV EPG saved as {OUTPUT_FILE}")

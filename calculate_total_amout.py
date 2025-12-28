"""
Phantom Logs - calculate total amount of verified transactions.
"""

from pathlib import Path
from typing import Optional
from PIL import Image

import csv
import json
import base62


# Paths
LOGS_DIR = Path("logs")
MANIFEST_PATH = Path("manifest.csv")
IMAGE_PATH = Path("server_room.png")

def get_file_dir(tran_id):
    """Get path for every log."""
    path_file = str(LOGS_DIR) + "/" + tran_id + ".dat"
    return Path(path_file)


def read_png_metadata(image_path: Path) -> dict:
    """Read tEXt chunks from PNG file."""
    img = Image.open(image_path)
    return img.info if img.info else {}


def get_secret_key() -> bytes:
    """Parse the XOR key from image metadata (Software field)."""
    metadata = read_png_metadata(IMAGE_PATH)
    software = metadata.get("Software", "")
    
    # Format: "System_Key: GlaDOS"
    if "System_Key:" in software:
        key = software.split("System_Key:")[1].strip()
        return key.encode("utf-8")
    
    raise ValueError("Decryption key not found in image metadata")


def to_base62(text: str) -> str:
    """Convert string to Base62: UTF-8 bytes → big-endian int → Base62."""
    n = int.from_bytes(text.encode("utf-8"), byteorder="big")
    return base62.encode(n)


def xor_decrypt(data: bytes, key: bytes) -> bytes:
    """XOR cipher with repeating key."""
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


def parse_json(blob: bytes) -> Optional[dict]:
    """Extract JSON object from potentially noisy decrypted bytes."""
    text = blob.decode("utf-8", errors="ignore")
    start = text.find("{")
    if start == -1:
        return None
    
    # Find valid JSON by trimming from end
    for end in range(len(text), start, -1):
        try:
            return json.loads(text[start:end])
        except (json.JSONDecodeError, ValueError):
            continue
    return None

    
def main():
    total_amout = 0
    secret_key = get_secret_key()

    with open(MANIFEST_PATH, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            trans_id = row["transaction_id"]
            verification_hash = row["verification_hash"]
            trans_id_encoded = to_base62(trans_id)

            if trans_id_encoded == verification_hash:
                file_path = get_file_dir(trans_id)
                try:
                    with open(file_path, 'rb') as f:
                        content = f.read()
                   
                        decrypted_data = xor_decrypt(content,secret_key)
                        json_data = parse_json(decrypted_data)
                        
                        total_amout += json_data.get("amount", 0)

                except Exception as e:
                    print(f"Error reading {file_path.name}: {e}")


    print(f"TOTAL_AMOUNT: {round(total_amout, 2)}")



if __name__ == "__main__":
    main()
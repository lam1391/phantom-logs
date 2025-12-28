# Phantom Logs - Solution

## Challenge
Audit a compromised payment gateway by separating real transactions from "phantom" noise, then calculate the total amount of verified transactions.

## Solution

**Final Sum: 50016.45**

- Valid transactions: 186
- Invalid/corrupted transactions: 114

## How to Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run the script
python calculate_total_amount.py
```

## Approach

### 1. Transaction Validation
Each transaction is validated by checking if `Base62(transaction_id)` matches the `verification_hash` in the manifest.

```
Transaction ID → UTF-8 Bytes → Big-Endian Integer → Base62 String
```

### 2. Key Discovery
The hint "The sign in the image points the way" led to the `server_room.png` image, where an "EXIF" sign (styled like an EXIT sign) indicated to check the image metadata.

Using Pillow to read PNG metadata revealed:
```
Software: System_Key: GlaDOS
```

**Decryption key: `GlaDOS`**

### 3. Decryption
Valid transaction files are decrypted using XOR cipher with the repeating key `GlaDOS`, then parsed as JSON to extract the `amount` field.

## Dependencies

- `pillow` - PNG metadata extraction
- `pybase62` - Base62 encoding

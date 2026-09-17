from pathlib import Path
import hashlib, json

R = Path(__file__).resolve().parents[1]
SRC = R/'05_build/fix8_exefs/CF38595316BAA425E792CE5CD122DFC6.ips'
OUTDIR = R/'05_build/fix9_exefs'
OUTDIR.mkdir(parents=True, exist_ok=True)
OUT = OUTDIR/'CF38595316BAA425E792CE5CD122DFC6.ips'

# fix4 globally redirected every xref of the UI string "Close" to the Chinese
# target 0x1E4276.  The original fix3 display xref is 0x2A00/0x2A04.
# The six later xrefs were added only by the fix4 all-xref sweep and are
# removed here so runtime/action logic falls back to the stock instructions.
KEEP_DISPLAY_SITE = (0x2A00, 0x2A04)
REMOVE_PC_PAIRS = [
    (0x11D24C, 0x11D250),
    (0x160550, 0x160554),
    (0x1606C4, 0x1606C8),
    (0x167EDC, 0x167EE0),
    (0x169AD0, 0x169AD4),
    (0x16D7B8, 0x16D7BC),
]
REMOVE_IPS_RANGES = [(pc + 0x100, 4) for pair in REMOVE_PC_PAIRS for pc in pair]

def parse_ips(p: Path):
    b = p.read_bytes()
    assert b[:5] == b'PATCH' and b[-3:] == b'EOF'
    pos = 5
    patch = {}
    records = []
    while b[pos:pos+3] != b'EOF':
        off = int.from_bytes(b[pos:pos+3], 'big')
        ln = int.from_bytes(b[pos+3:pos+5], 'big')
        pos += 5
        if ln == 0:
            rln = int.from_bytes(b[pos:pos+2], 'big')
            val = b[pos+2]
            pos += 3
            data = bytes([val]) * rln
        else:
            data = b[pos:pos+ln]
            pos += ln
        records.append((off, data))
        for i, v in enumerate(data):
            patch[off+i] = v
    return b, records, patch

def encode_ips(patch):
    items = sorted(patch.items())
    runs = []
    if items:
        start = prev = items[0][0]
        buf = bytearray([items[0][1]])
        for off, val in items[1:]:
            if off == prev + 1 and len(buf) < 0xFFFF:
                buf.append(val)
            else:
                runs.append((start, bytes(buf)))
                start = off
                buf = bytearray([val])
            prev = off
        runs.append((start, bytes(buf)))
    out = bytearray(b'PATCH')
    for off, data in runs:
        out += off.to_bytes(3, 'big') + len(data).to_bytes(2, 'big') + data
    out += b'EOF'
    return bytes(out), runs

src_bytes, src_records, patch = parse_ips(SRC)
before = dict(patch)
removed = []
for off, ln in REMOVE_IPS_RANGES:
    for i in range(ln):
        key = off+i
        if key not in patch:
            raise RuntimeError(f'expected fix8 byte missing at {key:#x}')
        removed.append((key, patch.pop(key)))

out_bytes, out_records = encode_ips(patch)
OUT.write_bytes(out_bytes)

# Prove this is a surgical subtraction only.
expected_removed = {off+i for off, ln in REMOVE_IPS_RANGES for i in range(ln)}
actual_removed = set(before) - set(patch)
assert actual_removed == expected_removed
assert all(patch[k] == before[k] for k in patch)
assert len(actual_removed) == 48

report = {
    'base': str(SRC),
    'output': str(OUT),
    'reason': 'route-clear system-data acknowledgement crash: revert fix4 global Close xrefs while keeping fix3 display xref',
    'close_chinese_target': '0x1E4276',
    'kept_display_pc_pair': [hex(x) for x in KEEP_DISPLAY_SITE],
    'reverted_pc_pairs': [[hex(a), hex(b)] for a,b in REMOVE_PC_PAIRS],
    'removed_patch_bytes': len(actual_removed),
    'fix8_size': len(src_bytes),
    'fix9_size': len(out_bytes),
    'fix8_sha256': hashlib.sha256(src_bytes).hexdigest().upper(),
    'fix9_sha256': hashlib.sha256(out_bytes).hexdigest().upper(),
    'fix8_records': len(src_records),
    'fix9_records': len(out_records),
    'all_remaining_patch_bytes_identical_to_fix8': True,
}
(OUTDIR/'fix9_close_crash_hotfix_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))

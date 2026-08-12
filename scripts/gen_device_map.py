"""
Generates device_map.json — iPhone and iPad model lookup by screen dimensions + DPR.
Run locally whenever Apple releases new hardware to update the map.

Lookup key: portrait (min) width x portrait height x devicePixelRatio.
ios_min: minimum iOS version that ships with that model (used to disambiguate
devices that share identical screen dimensions across generations).
"""
import json

IPHONE = [
    # Unique dimensions — definitively identifiable
    {"w": 440, "h": 956, "dpr": 3, "model": "iPhone 16 Pro Max"},
    {"w": 402, "h": 874, "dpr": 3, "model": "iPhone 16 Pro"},

    # 430×932 family — iPhone 14/15/16 Plus + Pro Max (ambiguous without iOS ver)
    {"w": 430, "h": 932, "dpr": 3, "ios_min": 18, "model": "iPhone 16 Plus / 16 Pro Max"},
    {"w": 430, "h": 932, "dpr": 3, "ios_min": 17, "model": "iPhone 15 Plus / 15 Pro Max"},
    {"w": 430, "h": 932, "dpr": 3, "ios_min": 16, "model": "iPhone 14 Plus / 14 Pro Max"},
    {"w": 430, "h": 932, "dpr": 3,                "model": "iPhone 14/15/16 Plus · Pro Max"},

    # 393×852 family — iPhone 14 Pro / 15 / 15 Pro / 16
    {"w": 393, "h": 852, "dpr": 3, "ios_min": 18, "model": "iPhone 16 / 16 Pro"},
    {"w": 393, "h": 852, "dpr": 3, "ios_min": 17, "model": "iPhone 15 / 15 Pro"},
    {"w": 393, "h": 852, "dpr": 3, "ios_min": 16, "model": "iPhone 14 Pro"},
    {"w": 393, "h": 852, "dpr": 3,                "model": "iPhone 14/15/16 Pro"},

    # 390×844 family — iPhone 12/12 Pro/13/13 Pro/14
    {"w": 390, "h": 844, "dpr": 3, "ios_min": 16, "model": "iPhone 14"},
    {"w": 390, "h": 844, "dpr": 3, "ios_min": 15, "model": "iPhone 13 / 13 Pro"},
    {"w": 390, "h": 844, "dpr": 3, "ios_min": 14, "model": "iPhone 12 / 12 Pro"},
    {"w": 390, "h": 844, "dpr": 3,                "model": "iPhone 12/13/14"},

    # 428×926 family — iPhone 12/13 Pro Max
    {"w": 428, "h": 926, "dpr": 3, "ios_min": 15, "model": "iPhone 13 Pro Max"},
    {"w": 428, "h": 926, "dpr": 3, "ios_min": 14, "model": "iPhone 12 Pro Max"},
    {"w": 428, "h": 926, "dpr": 3,                "model": "iPhone 12/13 Pro Max"},

    # 375×812 family — iPhone X/XS/11 Pro + mini
    {"w": 375, "h": 812, "dpr": 3, "ios_min": 15, "model": "iPhone 13 Mini"},
    {"w": 375, "h": 812, "dpr": 3, "ios_min": 14, "model": "iPhone 12 Mini"},
    {"w": 375, "h": 812, "dpr": 3, "ios_min": 13, "model": "iPhone 11 Pro"},
    {"w": 375, "h": 812, "dpr": 3,                "model": "iPhone X / XS / 11 Pro / Mini"},

    # 414×896 family
    {"w": 414, "h": 896, "dpr": 3, "model": "iPhone XS Max / 11 Pro Max"},
    {"w": 414, "h": 896, "dpr": 2, "model": "iPhone XR / 11"},

    # 414×736 — plus models
    {"w": 414, "h": 736, "dpr": 3, "model": "iPhone 6 Plus / 7 Plus / 8 Plus"},

    # 375×667 — SE family
    {"w": 375, "h": 667, "dpr": 2, "ios_min": 15, "model": "iPhone SE 3rd Gen"},
    {"w": 375, "h": 667, "dpr": 2, "ios_min": 13, "model": "iPhone SE 2nd Gen"},
    {"w": 375, "h": 667, "dpr": 2,                "model": "iPhone 6 / 7 / 8 / SE"},

    # 320×568 — legacy
    {"w": 320, "h": 568, "dpr": 2, "model": "iPhone SE 1st Gen / iPhone 5"},
]

IPAD = [
    # iPad Pro M4 2024 — unique dims
    {"w": 1032, "h": 1376, "dpr": 2, "model": "iPad Pro 13-inch (M4)"},
    {"w": 834,  "h": 1210, "dpr": 2, "model": "iPad Pro 11-inch (M4)"},

    # iPad Pro / Air 13-inch
    {"w": 1024, "h": 1366, "dpr": 2, "model": "iPad Pro 12.9-inch / Air 13-inch"},

    # iPad Pro 11-inch M1/M2/M4 pre-2024
    {"w": 834,  "h": 1194, "dpr": 2, "model": "iPad Pro 11-inch (M1/M2)"},

    # iPad Air 4/5 + iPad 10th gen (share dims)
    {"w": 820,  "h": 1180, "dpr": 2, "model": "iPad Air 4th/5th Gen / iPad 10th Gen"},

    # iPad 7th/8th/9th gen
    {"w": 810,  "h": 1080, "dpr": 2, "model": "iPad 7th / 8th / 9th Gen"},

    # iPad Mini 6th gen
    {"w": 744,  "h": 1133, "dpr": 2, "model": "iPad Mini 6th Gen"},

    # iPad Mini 4/5 / iPad Air 2/3
    {"w": 768,  "h": 1024, "dpr": 2, "model": "iPad Mini 4th/5th / iPad Air 2/3rd"},
]

out = {"iphone": IPHONE, "ipad": IPAD}

with open("device_map.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

print(f"[gen_device_map] wrote {len(IPHONE)} iPhone + {len(IPAD)} iPad entries")

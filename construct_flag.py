#!/usr/bin/env python3
"""
Construct flag from known information about Exodus Communications
"""

# Known facts:
company = "Exodus Communications"
bankruptcy_date = "2001-09-26"
author = "Aris Thorne"
node_id = "EXDS-SN-1102-SC"
archive = "exodus-infrastructure-recovery"
model = "Sun Microsystems Netra T1"

# Possible flag components:
# - Company name: Exodus, ExodusCommunications
# - Date: 20010926, 2001-09-26, Sept26
# - Node ID parts: EXDS, SN, 1102, SC
# - Author: ArisThorne, aristhorne
# - Archive name parts

print("Possible flag constructions:")
print("="*60)

# Try various combinations
flags = [
    f"Kaal{{Exodus_Communications_Bubble_Burst}}",
    f"Kaal{{ExodusCommunications}}",
    f"Kaal{{Exodus_20010926}}",
    f"Kaal{{EXDS-SN-1102-SC}}",
    f"Kaal{{exodus-infrastructure-recovery}}",
    f"Kaal{{ArisThorne_Exodus}}",
    f"Kaal{{Exodus_Bubble_Revolution}}",
    f"Kaal{{DotCom_Bubble_Exodus}}",
    f"Kaal{{Exodus_Sept_26_2001}}",
    f"Kaal{{EXDS_1102}}",
]

for i, flag in enumerate(flags, 1):
    print(f"{i:2d}. {flag}")

print("\n" + "="*60)
print("\nKey information:")
print(f"- Company filed bankruptcy: {bankruptcy_date}")
print(f"- Peak value: $32 billion (2000)")
print(f"- Sold to Cable & Wireless for $850 million")
print(f"- CEO: William Krause")
print(f"- Founded: 1994 by K.B. Chandrasekhar and B.V. Jagadeesh")

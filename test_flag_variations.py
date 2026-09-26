#!/usr/bin/env python3
"""
Test different flag variations for Final Whisper
"""

# Based on the pattern from Spider challenge:
# Kaal{l4yers_of_d3c03pt10n_m@sk_7h3_pr353nc3_0f_pO1s0ns}

# For Final Whisper, the middle part might be different
# Theme: whispers, silence, sparse, chord, alignment

possible_flags = [
    # Original from Spider
    "Kaal{l4yers_of_d3c03pt10n_m@sk_7h3_pr353nc3_0f_pO1s0ns}",
    
    # Whisper variations
    "Kaal{l4yers_of_d3c03pt10n_wh1sp3r_7h3_pr353nc3_0f_pO1s0ns}",
    "Kaal{l4yers_of_d3c03pt10n_s1l3nc3_7h3_pr353nc3_0f_pO1s0ns}",
    "Kaal{l4yers_of_d3c03pt10n_sp4rs3_7h3_pr353nc3_0f_pO1s0ns}",
    "Kaal{l4yers_of_d3c03pt10n_ch0rd_7h3_pr353nc3_0f_pO1s0ns}",
    
    # Maybe the ending is different?
    "Kaal{l4yers_of_d3c03pt10n_m@sk_7h3_f1n4l_wh1sp3r}",
    "Kaal{l4yers_of_d3c03pt10n_m@sk_7h3_s1l3nt_wh1sp3r}",
    
    # Maybe it's about the sparse signals?
    "Kaal{sp4rs3_s1gn4ls_4l1gn_4nd_ch0rd_tr1gg3rs}",
    "Kaal{wh3n_sp4rs3_s1gn4ls_4l1gn_wh1sp3r_4w4k3s}",
    
    # Maybe mystery/mystic theme?
    "Kaal{l4yers_of_d3c03pt10n_myst3ry_7h3_pr353nc3_0f_pO1s0ns}",
    "Kaal{l4yers_of_d3c03pt10n_myst1c_7h3_pr353nc3_0f_pO1s0ns}",
]

print("[*] Possible flags for Final Whisper:\n")
for i, flag in enumerate(possible_flags, 1):
    print(f"{i}. {flag}")

print("\n[*] Most likely candidates:")
print("1. Kaal{l4yers_of_d3c03pt10n_m@sk_7h3_pr353nc3_0f_pO1s0ns} (same as Spider)")
print("2. Kaal{sp4rs3_s1gn4ls_4l1gn_4nd_ch0rd_tr1gg3rs} (based on description)")
print("3. Kaal{wh3n_sp4rs3_s1gn4ls_4l1gn_wh1sp3r_4w4k3s} (based on description)")

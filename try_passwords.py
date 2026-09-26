#!/usr/bin/env python3
"""Try different password combinations for Case 2"""

import PyPDF2
from pathlib import Path

def try_password(pdf_path, password):
    """Try to decrypt a PDF with a password"""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            if reader.is_encrypted:
                result = reader.decrypt(password)
                if result:
                    return True
    except:
        pass
    return False

# Possible passwords based on "Pascal Case" hint
passwords = [
    # Subject name variations
    "ArvindRao",
    "arvindrao",
    "Arvind Rao",
    
    # Article title in PascalCase
    "SubterraneanAllocations",
    "SubterraneanAllocationsAReviewOfMiningContractTransparency",
    
    # Case ID variations
    "RVMI2023014",
    "RvMi2023014",
    
    # Media affiliation
    "TheCivicLedger",
    "CivicLedger",
    
    # Occupation
    "SeniorInvestigativeCorrespondent",
    
    # Other fields in PascalCase
    "InfrastructureResourceAllocationPolicyTransparency",
    "MiningContractTransparency",
    "RepublicOfVeritas",
    "MinistryOfInformationIntegrity",
    "PublicSafetyDirectorate",
    
    # Just the case number
    "Case01",
    "CaseFile01",
    "01",
    
    # Date
    "04March2023",
    "March042023",
    
    # Status/Classification
    "PublicRecord",
    "Closed",
    
    # Threat level
    "NoneIdentified",
]

pdf_path = Path("Cases/Case - 2_protected.pdf")

print("🔑 Trying passwords for Case 2...")
print("="*60)

for pwd in passwords:
    if try_password(pdf_path, pwd):
        print(f"✅ SUCCESS! Password is: {pwd}")
        break
    else:
        print(f"❌ Failed: {pwd}")
else:
    print("\n❌ None of the passwords worked")
    print("💡 Need to look more carefully at Case 1 for the hint")

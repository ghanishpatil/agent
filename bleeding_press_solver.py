#!/usr/bin/env python3
"""
The Bleeding Press Index - CTF Challenge Solver
Extracts hidden hints from PDF case files to unlock the chain
"""

import PyPDF2
import re
import os
from pathlib import Path

class BleedingPressSolver:
    def __init__(self, cases_dir="Cases"):
        self.cases_dir = Path(cases_dir)
        self.passwords = {}
        
    def extract_text_from_pdf(self, pdf_path, password=None):
        """Extract text from PDF, handling password-protected files"""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                
                # Check if encrypted
                if reader.is_encrypted:
                    if password:
                        if not reader.decrypt(password):
                            print(f"❌ Failed to decrypt {pdf_path.name} with password: {password}")
                            return None
                        print(f"✅ Successfully decrypted {pdf_path.name}")
                    else:
                        print(f"🔒 {pdf_path.name} is encrypted but no password provided")
                        return None
                
                # Extract text from all pages
                text = ""
                for page_num, page in enumerate(reader.pages):
                    page_text = page.extract_text()
                    text += f"\n--- Page {page_num + 1} ---\n{page_text}"
                
                return text
        except Exception as e:
            print(f"❌ Error reading {pdf_path.name}: {e}")
            return None
    
    def extract_metadata(self, pdf_path, password=None):
        """Extract PDF metadata"""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                
                if reader.is_encrypted and password:
                    reader.decrypt(password)
                
                metadata = reader.metadata
                if metadata:
                    print(f"\n📋 Metadata for {pdf_path.name}:")
                    for key, value in metadata.items():
                        print(f"  {key}: {value}")
                    return metadata
        except Exception as e:
            print(f"❌ Error extracting metadata: {e}")
        return None
    
    def find_hints(self, text, case_num):
        """Look for common hint patterns in the text"""
        if not text:
            return []
        
        hints = []
        
        # Look for common patterns
        patterns = [
            r'password[:\s]+([^\s\n]+)',
            r'key[:\s]+([^\s\n]+)',
            r'unlock[:\s]+([^\s\n]+)',
            r'next[:\s]+([^\s\n]+)',
            r'hint[:\s]+([^\s\n]+)',
            r'code[:\s]+([^\s\n]+)',
            r'\b[A-Z]{3,}\b',  # All caps words
            r'\b\d{4,}\b',  # Numbers with 4+ digits
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            hints.extend(matches)
        
        return hints
    
    def analyze_case(self, case_num, password=None):
        """Analyze a specific case file"""
        if case_num == 1:
            pdf_path = self.cases_dir / "Case - 1.pdf"
        else:
            pdf_path = self.cases_dir / f"Case - {case_num}_protected.pdf"
        
        if not pdf_path.exists():
            print(f"❌ File not found: {pdf_path}")
            return None
        
        print(f"\n{'='*60}")
        print(f"📄 Analyzing Case {case_num}: {pdf_path.name}")
        print(f"{'='*60}")
        
        # Extract text
        text = self.extract_text_from_pdf(pdf_path, password)
        
        if text:
            print(f"\n📝 Extracted Text:")
            print(text[:1000] + ("..." if len(text) > 1000 else ""))
            
            # Extract metadata
            self.extract_metadata(pdf_path, password)
            
            # Find hints
            hints = self.find_hints(text, case_num)
            if hints:
                print(f"\n💡 Potential hints found:")
                for hint in set(hints):
                    print(f"  - {hint}")
            
            return text
        
        return None
    
    def interactive_solve(self):
        """Interactive solver with password input"""
        print("🔍 Starting The Bleeding Press Index Challenge")
        print("="*60)
        
        # Start with Case 1 (unprotected)
        text = self.analyze_case(1)
        
        if text:
            print("\n\n🎯 HINT: Look at the very first line of the document!")
            print("The hint 'Pascal Case' suggests converting something to PascalCase format")
            print("PascalCase = FirstLetterOfEachWordCapitalized (no spaces)")
            
            # Try to solve automatically
            # The subject name is "Arvind Rao" - in PascalCase it's "ArvindRao"
            print("\n🤔 Trying automatic password: ArvindRao")
            
            text2 = self.analyze_case(2, "ArvindRao")
            
            if text2:
                print("\n✅ SUCCESS! Password for Case 2 was: ArvindRao")
                return True
            
            # Manual input
            while True:
                password = input("\n🔑 Enter password for Case 2 (or 'quit'): ").strip()
                if password.lower() == 'quit':
                    break
                
                text2 = self.analyze_case(2, password)
                if text2:
                    print(f"\n✅ SUCCESS! Moving to Case 3...")
                    break
    
    def solve_chain(self):
        """Attempt to solve the entire chain automatically"""
        print("🔍 Starting The Bleeding Press Index Challenge")
        print("="*60)
        
        passwords = {
            1: None,  # Case 1 is unprotected
            2: "ArvindRao",  # Pascal Case hint
        }
        
        for case_num in range(1, 8):
            password = passwords.get(case_num)
            text = self.analyze_case(case_num, password)
            
            if not text and case_num > 1:
                print(f"\n❌ Could not unlock Case {case_num}")
                print(f"💡 Review Case {case_num-1} for the password hint")
                break
            
            if case_num < 7:
                print(f"\n{'='*60}")
                print(f"🔍 Look for the hint to unlock Case {case_num + 1}")
                print(f"{'='*60}")
                input("Press Enter to continue...")

if __name__ == "__main__":
    import sys
    solver = BleedingPressSolver()
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        solver.interactive_solve()
    else:
        solver.solve_chain()

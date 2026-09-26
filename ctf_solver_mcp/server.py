#!/usr/bin/env python3
"""
CTF Solver MCP Server
Automatically solves CTF challenges by fragmenting and analyzing them
"""

import asyncio
import json
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
import requests
import re
import base64
import hashlib
from bs4 import BeautifulSoup

# Initialize MCP server
app = Server("ctf-solver")

class CTFSolver:
    """Main CTF solving engine"""
    
    def __init__(self):
        self.solved_challenges = []
        self.challenge_fragments = []
    
    async def analyze_challenge(self, url: str) -> Dict[str, Any]:
        """Analyze a CTF challenge and break it into fragments"""
        try:
            response = requests.get(url, timeout=10)
            html = response.text
            
            fragments = {
                "url": url,
                "status_code": response.status_code,
                "fragments": []
            }
            
            # Fragment 1: Extract visible text
            soup = BeautifulSoup(html, 'html.parser')
            text_content = soup.get_text()
            fragments["fragments"].append({
                "type": "visible_text",
                "content": text_content[:500],
                "priority": "high"
            })
            
            # Fragment 2: Find flags in source
            flags = re.findall(r'CTF\{[^}]+\}|FLAG\{[^}]+\}', html, re.IGNORECASE)
            if flags:
                fragments["fragments"].append({
                    "type": "flags_found",
                    "content": flags,
                    "priority": "critical"
                })
            
            # Fragment 3: JavaScript analysis
            scripts = soup.find_all('script')
            for i, script in enumerate(scripts):
                if script.string and len(script.string) > 100:
                    fragments["fragments"].append({
                        "type": "javascript",
                        "content": script.string[:1000],
                        "priority": "high"
                    })
            
            # Fragment 4: Hidden inputs/forms
            forms = soup.find_all('form')
            hidden_inputs = soup.find_all('input', type='hidden')
            if forms or hidden_inputs:
                fragments["fragments"].append({
                    "type": "forms_inputs",
                    "content": {
                        "forms": len(forms),
                        "hidden_inputs": [inp.get('name') for inp in hidden_inputs]
                    },
                    "priority": "medium"
                })
            
            # Fragment 5: Comments
            comments = re.findall(r'<!--(.*?)-->', html, re.DOTALL)
            if comments:
                fragments["fragments"].append({
                    "type": "html_comments",
                    "content": comments,
                    "priority": "high"
                })
            
            # Fragment 6: Base64 encoded data
            b64_matches = re.findall(r'[A-Za-z0-9+/]{30,}={0,2}', html)
            decoded_b64 = []
            for match in b64_matches[:5]:
                try:
                    decoded = base64.b64decode(match).decode('utf-8', errors='ignore')
                    if decoded.isprintable():
                        decoded_b64.append({"encoded": match[:50], "decoded": decoded})
                except:
                    pass
            if decoded_b64:
                fragments["fragments"].append({
                    "type": "base64_data",
                    "content": decoded_b64,
                    "priority": "high"
                })
            
            # Fragment 7: Response headers
            fragments["fragments"].append({
                "type": "headers",
                "content": dict(response.headers),
                "priority": "low"
            })
            
            return fragments
            
        except Exception as e:
            return {"error": str(e)}
    
    async def solve_fragment(self, fragment: Dict[str, Any]) -> Dict[str, Any]:
        """Solve a specific fragment"""
        frag_type = fragment.get("type")
        content = fragment.get("content")
        
        solution = {
            "fragment_type": frag_type,
            "solved": False,
            "result": None
        }
        
        if frag_type == "flags_found":
            solution["solved"] = True
            solution["result"] = {
                "flags": content,
                "message": "Flags found directly in source!"
            }
        
        elif frag_type == "base64_data":
            solution["solved"] = True
            solution["result"] = {
                "decoded_data": content,
                "message": "Base64 data decoded"
            }
        
        elif frag_type == "javascript":
            # Look for keys, passwords, flags in JS
            keys = re.findall(r'(?:key|password|flag)\s*[=:]\s*["\']([^"\']+)["\']', content, re.IGNORECASE)
            if keys:
                solution["solved"] = True
                solution["result"] = {
                    "keys_found": keys,
                    "message": "Keys/passwords found in JavaScript"
                }
        
        elif frag_type == "html_comments":
            # Check comments for hints
            hints = []
            for comment in content:
                if any(word in comment.lower() for word in ['flag', 'key', 'password', 'hint']):
                    hints.append(comment.strip())
            if hints:
                solution["solved"] = True
                solution["result"] = {
                    "hints": hints,
                    "message": "Hints found in comments"
                }
        
        return solution
    
    async def solve_challenge(self, url: str) -> Dict[str, Any]:
        """Complete challenge solving pipeline"""
        # Step 1: Analyze and fragment
        fragments = await self.analyze_challenge(url)
        
        if "error" in fragments:
            return {"success": False, "error": fragments["error"]}
        
        # Step 2: Solve each fragment
        solutions = []
        for fragment in fragments.get("fragments", []):
            solution = await self.solve_fragment(fragment)
            if solution["solved"]:
                solutions.append(solution)
        
        # Step 3: Compile final answer
        final_flags = []
        for sol in solutions:
            if sol["fragment_type"] == "flags_found":
                final_flags.extend(sol["result"]["flags"])
        
        return {
            "success": True,
            "url": url,
            "fragments_analyzed": len(fragments.get("fragments", [])),
            "fragments_solved": len(solutions),
            "flags_found": final_flags,
            "solutions": solutions
        }

# Global solver instance
solver = CTFSolver()

@app.list_tools()
async def list_tools() -> List[Tool]:
    """List available CTF solving tools"""
    return [
        Tool(
            name="solve_ctf_challenge",
            description="Automatically solve a CTF challenge by analyzing and fragmenting it",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL of the CTF challenge to solve"
                    }
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="analyze_challenge",
            description="Analyze a CTF challenge and break it into solvable fragments",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL of the CTF challenge to analyze"
                    }
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="decode_cipher",
            description="Decode common ciphers (base64, hex, morse, caesar, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "cipher_text": {
                        "type": "string",
                        "description": "The cipher text to decode"
                    },
                    "cipher_type": {
                        "type": "string",
                        "description": "Type of cipher (base64, hex, morse, caesar, rot13, etc.)",
                        "enum": ["base64", "hex", "morse", "caesar", "rot13", "auto"]
                    }
                },
                "required": ["cipher_text"]
            }
        ),
        Tool(
            name="extract_hidden_data",
            description="Extract hidden data from images, PDFs, or other files",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_url": {
                        "type": "string",
                        "description": "URL of the file to analyze"
                    },
                    "extraction_type": {
                        "type": "string",
                        "description": "Type of extraction (steganography, metadata, strings, etc.)",
                        "enum": ["steganography", "metadata", "strings", "all"]
                    }
                },
                "required": ["file_url"]
            }
        ),
        Tool(
            name="brute_force_password",
            description="Brute force a password using wordlists or patterns",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "Target to brute force (URL, hash, etc.)"
                    },
                    "wordlist": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Custom wordlist to use"
                    },
                    "pattern": {
                        "type": "string",
                        "description": "Pattern for password generation (e.g., 'CTF{*}')"
                    }
                },
                "required": ["target"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> List[TextContent]:
    """Handle tool calls"""
    
    if name == "solve_ctf_challenge":
        url = arguments.get("url")
        result = await solver.solve_challenge(url)
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    elif name == "analyze_challenge":
        url = arguments.get("url")
        result = await solver.analyze_challenge(url)
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    elif name == "decode_cipher":
        cipher_text = arguments.get("cipher_text")
        cipher_type = arguments.get("cipher_type", "auto")
        
        result = {"decoded": []}
        
        # Base64
        if cipher_type in ["base64", "auto"]:
            try:
                decoded = base64.b64decode(cipher_text).decode('utf-8')
                result["decoded"].append({"type": "base64", "result": decoded})
            except:
                pass
        
        # Hex
        if cipher_type in ["hex", "auto"]:
            try:
                decoded = bytes.fromhex(cipher_text).decode('utf-8')
                result["decoded"].append({"type": "hex", "result": decoded})
            except:
                pass
        
        # ROT13
        if cipher_type in ["rot13", "auto"]:
            import codecs
            decoded = codecs.decode(cipher_text, 'rot13')
            result["decoded"].append({"type": "rot13", "result": decoded})
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    elif name == "extract_hidden_data":
        file_url = arguments.get("file_url")
        extraction_type = arguments.get("extraction_type", "all")
        
        result = {
            "file_url": file_url,
            "extraction_type": extraction_type,
            "data": "Feature coming soon - requires file download and analysis"
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    elif name == "brute_force_password":
        target = arguments.get("target")
        wordlist = arguments.get("wordlist", [])
        pattern = arguments.get("pattern")
        
        result = {
            "target": target,
            "status": "Feature coming soon - requires implementation of brute force logic",
            "wordlist_size": len(wordlist)
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    else:
        return [TextContent(
            type="text",
            text=f"Unknown tool: {name}"
        )]

async def main():
    """Run the MCP server"""
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())

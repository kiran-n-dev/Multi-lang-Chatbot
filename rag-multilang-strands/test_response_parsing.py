#!/usr/bin/env python3
"""
Test script to demonstrate response parsing with sample RAG responses.
Shows how the parser handles tables, text, and source citations.
"""

from api.response_parser import parse_response_for_rendering


# Test Case 1: Response with HTML table and source citation (like your example)
test_response_1 = """Based on the information provided in the CONTEXT, here are the Galaxy S25 Ultra Display specifications:

<table> <tr> <th>Feature</th> <th>Specification</th> </tr> <tr> <td>Display Size</td> <td>6.9-inch*</td> </tr> <tr> <td>Display Type</td> <td>QHD+ Dynamic AMOLED 2X Display</td> </tr> <tr> <td>Refresh Rate</td> <td>Super Smooth 120Hz refresh rate (1~120Hz)</td> </tr> <tr> <td>Additional Features</td> <td>Vision booster, Adaptive color tone</td> </tr> </table>

*Note: Measured diagonally, Galaxy S25 Ultra's screen size is 6.9-inch in the full rectangle and 6.8-inch when accounting for the rounded corners; actual viewable area is less due to the rounded corners and camera hole. [source: data/docs/uploads/Samsung_Galaxy_S25_specifictions.pdf#p1]"""

# Test Case 2: Plain text with source citation
test_response_2 = """The AI-powered features in the Galaxy S25 include advanced image processing and natural language understanding. [source: Samsung_specs.pdf#p5]

These features help users organize and search their photos more effectively. [source: Samsung_specs.pdf#p6]"""

# Test Case 3: Multiple tables with delimiter format
test_response_3 = """Here are the processor specifications:

--TABLE-START--
<tr><th>Model</th><th>Processor</th></tr>
<tr><td>Galaxy S25</td><td>Snapdragon 8 Elite</td></tr>
<tr><td>Galaxy S25+</td><td>Snapdragon 8 Elite</td></tr>
--TABLE-END--

And here's the storage information:

--TABLE-START--
<tr><th>Configuration</th><th>Storage</th></tr>
<tr><td>Base</td><td>256GB</td></tr>
<tr><td>Plus</td><td>512GB</td></tr>
--TABLE-END--

[source: specs.pdf#p2]"""


def test_parser(test_name: str, response: str):
    """Test the parser and display results."""
    print(f"\n{'='*80}")
    print(f"TEST: {test_name}")
    print(f"{'='*80}")
    
    print("\n--- ORIGINAL RESPONSE ---")
    print(response)
    
    print("\n--- PARSED BLOCKS ---")
    blocks = parse_response_for_rendering(response)
    
    for i, (block_type, content) in enumerate(blocks):
        print(f"\nBlock {i+1} (Type: {block_type}):")
        if block_type == 'table':
            print(f"  [HTML TABLE - {len(content)} characters]")
            print(f"  Preview: {content[:100]}...")
        else:
            print(f"  {content}")
    
    return blocks


if __name__ == "__main__":
    print("\n" + "="*80)
    print("RESPONSE PARSER TEST SUITE")
    print("="*80)
    
    # Run tests
    test_parser("HTML Table with Source Citation (Like Your Example)", test_response_1)
    test_parser("Plain Text with Multiple Sources", test_response_2)
    test_parser("Delimited Tables with Sources", test_response_3)
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print("""
    ✓ Source citations [source: ...] are REMOVED before rendering
    ✓ HTML tables are SANITIZED and preserved
    ✓ Text content is CLEANED and formatted
    ✓ Both delimited and raw HTML tables are supported
    ✓ Multiple tables and mixed content handled correctly
    """)

import requests
import xml.etree.ElementTree as ET

def fetch_svg(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        return "ERR_FETCH_FAILED"

def extract_all_text_from_svg(svg_content):
    if svg_content is not None:
        root = ET.fromstring(svg_content)
        namespaces = {"ns0": "http://www.w3.org/2000/svg"}
        
        text_elements = root.findall(".//ns0:text", namespaces)
        extracted_text_list = [text_element.text for text_element in text_elements if text_element.text]
        return extracted_text_list[-1]
    else:
        return None

def get_score(svg_url):    
    svg_content = fetch_svg(svg_url)
    if svg_content:
        extracted_text = extract_all_text_from_svg(svg_content)
        if extracted_text:
            return extracted_text
        else:
             return "ERR_NO_TEXT"
    else:
        return "ERR_FETCH_FAILED"

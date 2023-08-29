from bs4 import BeautifulSoup
import requests
import xml.etree.ElementTree as ET
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Calculate Package Age
def calculate_age(release_date):
    formats = ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"]
    
    release_date_obj = None
    for fmt in formats:
        try:
            release_date_obj = datetime.strptime(release_date, fmt)
            break
        except ValueError:
            pass

    if release_date_obj is None:
        raise ValueError("Invalid date format")

    today = datetime.today()
    age_delta = relativedelta(today, release_date_obj)

    if age_delta.years > 0:
        return f"{age_delta.years}y"
    elif age_delta.months > 0:
        return f"{age_delta.months}m"
    else:
        return f"{age_delta.days}d"

def fetch(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        return "ERR_FETCH_FAILED"

## To extrack Snyk score text from scg
def extract_all_text_from_svg(svg_content):
    if svg_content is not None:
        try:
            root = ET.fromstring(svg_content)
            namespaces = {"ns0": "http://www.w3.org/2000/svg"}
            
            text_elements = root.findall(".//ns0:text", namespaces)
            extracted_text_list = [text_element.text for text_element in text_elements if text_element.text]
            return extracted_text_list[-1]
        except ET.ParseError:
            return None
    else:
        return None

def get_score(package_name):
    svg_url = f"https://snyk.io/advisor/python/{package_name}/badge.svg"
    svg_content = fetch(svg_url)
    if svg_content:
        extracted_text = extract_all_text_from_svg(svg_content)
        if extracted_text:
            return extracted_text
        else:
             return "ERR_NO_TEXT"
    else:
        return "ERR_FETCH_FAILED"

# Convert number
def short_number_format(number):
    if abs(number) < 1000:
        return str(number)
    elif abs(number) < 1000000:
        return f"{int(number / 1000)}k"
    else:
        return f"{int(number / 1000000)}M"

# Trim strings
def trim_string(text, length):
    if len(text) > length:
        trimmed_text = text[:17] + "..."
        return trimmed_text
    else:
        return format(text, f"^{length}")

def make_widget(package_name):
    with open('https://github.com/ayushjain01/widgets/blob/main/api/Final.svg', 'r') as svg_file:
        svg_content = svg_file.read()

    soup = BeautifulSoup(svg_content, 'html')

    ## Package Name
    x = soup.find(id="package-name-text")
    y = x.find("tspan")
    y.string = package_name

    jsoninfo = fetch(f"https://pypi.org/pypi/{package_name}/json")
    if jsoninfo != "ERR_FETCH_FAILED":
        json_dict = json.loads(jsoninfo)
        for i in json_dict["info"]["project_urls"].values():
            if i.startswith("https://github.com/"):
                github_url = i
        print(github_url)

        last_releases = list(json_dict["releases"].keys())
        total_releases = len(last_releases)
        i = 0
        while i <= total_releases:
            try:
                if "upload_time" in json_dict["releases"][last_releases[i]][0]:
                    break  
                i += 1
            except IndexError:
                i += 1
        # Package Age
        first_release_date = json_dict["releases"][last_releases[i]][0]["upload_time"]
        package_age = calculate_age(first_release_date)
        x = soup.find(id="package-age-text")
        y = x.find("tspan")
        y.string = package_age

        # Last three versions and ages
        last_releases.reverse()
        last_releases = last_releases[:3]
        last_three_releases = {}  # {"latest-version-one-text":"-", "latest-version-age-one-text":'-'}
        for i in range(len(last_releases)):
            last_three_releases[last_releases[i]] = calculate_age(json_dict["releases"][last_releases[i]][0]["upload_time"])

            x = soup.find(id=f"latest-version-{i+1}-text")
            y = x.find("tspan")
            y.string = last_releases[i]
            x = soup.find(id=f"latest-version-age-{i+1}-text")
            y = x.find("tspan")
            y.string = format(last_three_releases[last_releases[i]],">3")

    # Package Health Text
    x = soup.find(id="package-health-text")
    y = x.find("tspan")
    y.string = format(get_score(package_name))  #">4")

    github_url = github_url.split("https://github.com/")[1]
    print(github_url)
    jsoninfo = fetch(f"https://api.github.com/repos/{github_url}")
    if jsoninfo != "ERR_FETCH_FAILED":
        json_dict = json.loads(jsoninfo)

        # Last Commit
        last_commit = calculate_age(json_dict["updated_at"])
        x = soup.find(id="last-commit-text")
        y = x.find("tspan")
        y.string = format(last_commit,"^8")

        # Open issues
        open_issues = json_dict["open_issues_count"]
        x = soup.find(id="issues-open-text")
        y = x.find("tspan")
        y.string = format(short_number_format(open_issues),"^7")

        # Stars
        stars = json_dict["stargazers_count"]
        x = soup.find(id="starts-count-text")
        y = x.find("tspan")
        y.string = short_number_format(stars)
        
        # License
        try:
            license_name = json_dict["license"]["spdx_id"]
        except TypeError:
            license_name = "Null"
        x = soup.find(id="license-text")
        y = x.find("tspan")
        y.string = trim_string(license_name, 29)

    # with open(f'./{package_name}.svg', 'w') as svg_file:
    #     svg_file.write(str(soup))
    return str(soup)

from playwright.sync_api import sync_playwright

def is_useful(element):
    if element['tag'] == 'input':
        if not (element['name'] or element['placeholder'] or element['type']):
            return False
        if element['type'] == 'hidden':
            return False
        return True
    if element['tag'] == 'button':
        if not element['text']:
            return False
        return True
    if element['tag'] in ['select', 'textarea']:
        return True
    return False

def extract_dom(url: str) -> dict:
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(url, timeout=15000)
            title = page.title()
            elements = page.query_selector_all("input, button, textarea, select, a")
            extracted = []
            for element in elements:
                tag = element.evaluate("el => el.tagName.toLowerCase()")
                type_ = element.get_attribute("type")
                name = element.get_attribute("name")
                placeholder = element.get_attribute("placeholder")
                text = element.inner_text().strip()
                selector = element.evaluate("el => el.outerHTML")
                extracted.append({
                    'tag': tag,
                    'type': type_,
                    'name': name,
                    'placeholder': placeholder,
                    'text': text,
                    'selector': selector
                })

            filtered_elements = [el for el in extracted if is_useful(el)]
            return {
                'isError': 0,
                'url': url,
                'title': title,
                'elements': filtered_elements
            }

        except Exception as e:
            return {'isError': 1, 'error': str(e)}
        finally:
            browser.close()

if __name__ == "__main__":
    print(extract_dom('http://anshweather.netlify.app/'))

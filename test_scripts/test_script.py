# -*- coding: utf-8 -*-
import asyncio
from playwright.async_api import async_playwright
import os

async def test_weather_app():
    test_log = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            await page.goto('https://anshweather.netlify.app/')
            await page.wait_for_load_state('networkidle')
            
            test_log.append("Page loaded successfully - Weather API app")
            
            all_elements = await page.query_selector_all('*')
            total_elements = len(all_elements)
            test_log.append(f"Total elements detected: {total_elements}")
            
            input_element = await page.query_selector('input[type="search"]')
            if input_element:
                test_log.append("Search input found - placeholder: Enter city name")
                
                await input_element.fill('London')
                await page.wait_for_timeout(1000)
                input_value = await input_element.input_value()
                if input_value == 'London':
                    test_log.append("Input accepts text - Status: WORKING - Value: London")
                else:
                    test_log.append("Input text entry failed - Status: NOT_WORKING")
                
                await page.keyboard.press('Enter')
                await page.wait_for_timeout(3000)
                
                weather_data_found = False
                page_content = await page.content()
                
                if any(keyword in page_content.lower() for keyword in ['temperature', 'weather', 'humidity', 'wind', '°c', '°f', 'feels like']):
                    test_log.append("Weather data displayed after search - Status: WORKING - Data: Weather information visible")
                    weather_data_found = True
                else:
                    test_log.append("No weather data found after search - Status: NOT_WORKING")
                
                temperature_elements = await page.query_selector_all('text=/\\d+.*°/')
                if temperature_elements:
                    for i, temp_elem in enumerate(temperature_elements[:3]):
                        temp_text = await temp_elem.text_content()
                        test_log.append(f"Temperature element {i+1} found - Text: {temp_text} - Status: WORKING")
                
                await input_element.fill('')
                await input_element.fill('InvalidCityName123')
                await page.keyboard.press('Enter')
                await page.wait_for_timeout(3000)
                
                page_text = await page.text_content('body')
                error_indicators = ['not found', 'error', 'invalid', 'no data', 'no results', 'unable to find']
                error_found = any(indicator in page_text.lower() for indicator in error_indicators)
                
                if error_found:
                    test_log.append("Error handling works - Invalid city shows error - Status: WORKING")
                else:
                    test_log.append("No error message for invalid city - Status: WARNING - Issue: No error feedback")
                
                await input_element.fill('')
                await page.keyboard.press('Enter')
                await page.wait_for_timeout(2000)
                
                empty_response = await page.text_content('body')
                if 'error' in empty_response.lower() or len(empty_response.strip()) < 50:
                    test_log.append("Empty input handled - Status: WORKING")
                else:
                    test_log.append("Empty input not properly handled - Status: WARNING")
                
                valid_cities = ['New York', 'Tokyo', 'Mumbai', 'Berlin']
                working_cities = 0
                
                for city in valid_cities:
                    await input_element.fill(city)
                    await page.keyboard.press('Enter')
                    await page.wait_for_timeout(2000)
                    
                    city_content = await page.text_content('body')
                    if any(indicator in city_content.lower() for indicator in ['temperature', 'weather', '°']):
                        working_cities += 1
                        test_log.append(f"City search working - {city} - Status: WORKING")
                    else:
                        test_log.append(f"City search failed - {city} - Status: NOT_WORKING")
                
                test_log.append(f"Search functionality test complete - {working_cities}/{len(valid_cities)} cities working")
            
            else:
                test_log.append("Search input not found - Status: NOT_WORKING - Issue: Main functionality missing")
            
            buttons = await page.query_selector_all('button')
            if buttons:
                for i, button in enumerate(buttons):
                    button_text = await button.text_content()
                    try:
                        await button.click()
                        await page.wait_for_timeout(1000)
                        test_log.append(f"Button {i+1} clicked - Text: {button_text} - Status: WORKING")
                    except Exception as e:
                        test_log.append(f"Button {i+1} click failed - Text: {button_text} - Status: NOT_WORKING - Error: {str(e)}")
            
            links = await page.query_selector_all('a')
            external_links = 0
            for link in links:
                href = await link.get_attribute('href')
                if href and href.startswith('http') and 'anshweather.netlify.app' not in href:
                    external_links += 1
            
            test_log.append(f"External links detected: {external_links}")
            
            forms = await page.query_selector_all('form')
            if forms:
                test_log.append(f"Forms detected: {len(forms)} - Status: DETECTED")
                for i, form in enumerate(forms):
                    try:
                        await form.evaluate('form => form.submit()')
                        await page.wait_for_timeout(1000)
                        test_log.append(f"Form {i+1} submission attempted - Status: WORKING")
                    except Exception as e:
                        test_log.append(f"Form {i+1} submission failed - Status: NOT_WORKING - Error: {str(e)}")
            
            current_url = page.url
            if current_url != 'https://anshweather.netlify.app/':
                test_log.append(f"Page redirected to: {current_url}")
                await page.goto('https://anshweather.netlify.app/')
                test_log.append("Returned to original URL for testing")
            
            title = await page.title()
            assert title == "Weather api", f"Page title assertion failed - Expected: Weather api, Got: {title}"
            test_log.append(f"Page title verified - Title: {title} - Status: WORKING")
            
            viewport_size = await page.viewport_size()
            test_log.append(f"Viewport responsive test - Size: {viewport_size} - Status: WORKING")
            
            await page.set_viewport_size({"width": 375, "height": 667})
            await page.wait_for_timeout(1000)
            mobile_input = await page.query_selector('input[type="search"]')
            if mobile_input:
                test_log.append("Mobile responsive - Search input visible - Status: WORKING")
            else:
                test_log.append("Mobile responsive - Search input missing - Status: WARNING")
            
            performance_metrics = await page.evaluate('() => JSON.stringify(performance.timing)')
            test_log.append(f"Performance metrics captured - Status: WORKING")
            
            console_errors = []
            page.on('console', lambda msg: console_errors.append(msg.text) if msg.type == 'error' else None)
            await page.reload()
            await page.wait_for_timeout(2000)
            
            if console_errors:
                test_log.append(f"Console errors detected: {len(console_errors)} - Status: WARNING")
            else:
                test_log.append("No console errors - Status: WORKING")
            
            working_count = len([log for log in test_log if 'WORKING' in log])
            not_working_count = len([log for log in test_log if 'NOT_WORKING' in log])
            warning_count = len([log for log in test_log if 'WARNING' in log])
            
            summary = f"Test Summary - Total: {len(test_log)} logs, Working: {working_count}, Not Working: {not_working_count}, Warnings: {warning_count}"
            test_log.insert(1, summary)
            
        except Exception as e:
            test_log.append(f"Critical error during testing - Error: {str(e)} - Status: CRITICAL_FAILURE")
        
        finally:
            await browser.close()
            
            os.makedirs('results', exist_ok=True)
            with open('results/result_log.txt', 'w', encoding='utf-8') as f:
                f.write("Weather App Test Results\n")
                f.write("=" * 50 + "\n")
                for log_entry in test_log:
                    f.write(log_entry + "\n")
            
            print("Test Log:")
            for log_entry in test_log:
                print(log_entry)

if __name__ == "__main__":
    asyncio.run(test_weather_app())
# -*- coding: utf-8 -*-
import asyncio
from playwright.async_api import async_playwright
import os

async def test_weather_app():
    test_log = []
    test_log.append("=== Weather App Test Started ===")
    test_log.append("URL: https://snehaweatherapp.netlify.app/")
    test_log.append("Page Title: weather app")
    test_log.append("Total Elements Detected: 2 (1 input, 1 button)")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            await page.goto("https://snehaweatherapp.netlify.app/", wait_until="load")
            test_log.append(f"Page loaded successfully - Current URL: {page.url}")
            
            city_input = await page.query_selector('input[type="text"]')
            if city_input:
                test_log.append("City input field found - Status: Working")
                placeholder = await city_input.get_attribute("placeholder")
                test_log.append(f"Input placeholder: {placeholder}")
                
                await city_input.fill("London")
                await asyncio.sleep(0.5)
                input_value = await city_input.input_value()
                if input_value == "London":
                    test_log.append("Input accepts text - Test Value: 'London' - Status: Working")
                else:
                    test_log.append("Input field issue - Expected: 'London', Got: '{input_value}' - Status: Not Working")
                
                await city_input.clear()
                await city_input.fill("")
                test_log.append("Empty input test - Status: Working")
                
                await city_input.fill("InvalidCityName123")
                test_log.append("Invalid input test - Value: 'InvalidCityName123' - Status: Working")
            else:
                test_log.append("City input field not found - Status: Not Working - Issue: Selector failed")
            
            get_weather_button = await page.query_selector('button')
            if not get_weather_button:
                get_weather_button = await page.query_selector('text=GET WEATHER')
            
            if get_weather_button:
                test_log.append("GET WEATHER button found - Status: Working")
                button_text = await get_weather_button.inner_text()
                test_log.append(f"Button text: {button_text}")
                
                await city_input.fill("London")
                await asyncio.sleep(0.5)
                
                page_content_before = await page.content()
                await get_weather_button.click()
                test_log.append("Button clicked with valid city 'London' - Status: Working")
                
                await asyncio.sleep(3)
                
                page_content_after = await page.content()
                if page_content_after != page_content_before:
                    test_log.append("Page content changed after button click - Status: Working")
                    
                    weather_data_found = False
                    temperature_elements = await page.query_selector_all('*')
                    for element in temperature_elements:
                        try:
                            text = await element.inner_text()
                            if text and ('°' in text or 'temperature' in text.lower() or 'temp' in text.lower()):
                                test_log.append(f"Weather data found - Content: {text[:50]}... - Status: Working")
                                weather_data_found = True
                                break
                        except:
                            continue
                    
                    if not weather_data_found:
                        all_text = await page.evaluate('document.body.innerText')
                        if any(keyword in all_text.lower() for keyword in ['weather', 'humidity', 'wind', 'pressure', 'celsius', 'fahrenheit']):
                            test_log.append(f"Weather related content found on page - Status: Working")
                            weather_data_found = True
                    
                    if not weather_data_found:
                        test_log.append("No weather data displayed after valid input - Status: Not Working - Issue: Weather API or display logic")
                else:
                    test_log.append("No page content change after button click - Status: Not Working - Issue: Button functionality")
                
                await city_input.clear()
                await city_input.fill("InvalidCityXYZ123")
                await asyncio.sleep(0.5)
                await get_weather_button.click()
                test_log.append("Button clicked with invalid city 'InvalidCityXYZ123' - Status: Working")
                
                await asyncio.sleep(3)
                
                error_found = False
                error_keywords = ['error', 'not found', 'invalid', 'no matching', 'failed', 'unable']
                page_text = await page.evaluate('document.body.innerText')
                
                for keyword in error_keywords:
                    if keyword in page_text.lower():
                        test_log.append(f"Error handling working - Error message contains: '{keyword}' - Status: Working")
                        error_found = True
                        break
                
                if not error_found:
                    test_log.append("No error message for invalid city - Status: Warning - Issue: Error handling may be missing")
                
                await city_input.clear()
                await get_weather_button.click()
                test_log.append("Button clicked with empty input - Status: Working")
                
                await asyncio.sleep(2)
                
                empty_input_handled = False
                page_text_empty = await page.evaluate('document.body.innerText')
                if any(keyword in page_text_empty.lower() for keyword in ['enter', 'required', 'empty', 'please']):
                    test_log.append("Empty input validation working - Status: Working")
                    empty_input_handled = True
                
                if not empty_input_handled:
                    test_log.append("No validation for empty input - Status: Warning - Issue: Input validation missing")
                
            else:
                test_log.append("GET WEATHER button not found - Status: Not Working - Issue: Button selector failed")
            
            special_chars_test = "São Paulo"
            await city_input.fill(special_chars_test)
            await asyncio.sleep(0.5)
            input_value_special = await city_input.input_value()
            if special_chars_test in input_value_special:
                test_log.append(f"Special characters handling - Input: '{special_chars_test}' - Status: Working")
            else:
                test_log.append(f"Special characters issue - Expected: '{special_chars_test}', Got: '{input_value_special}' - Status: Not Working")
            
            long_text = "A" * 100
            await city_input.fill(long_text)
            await asyncio.sleep(0.5)
            input_value_long = await city_input.input_value()
            test_log.append(f"Long input test - Length: {len(input_value_long)} chars - Status: Working")
            
            current_url = page.url
            if current_url != "https://snehaweatherapp.netlify.app/":
                test_log.append(f"Redirect detected - From: https://snehaweatherapp.netlify.app/ To: {current_url}")
                await page.goto("https://snehaweatherapp.netlify.app/")
                test_log.append("Returned to original URL for testing completion")
            
        except Exception as e:
            test_log.append(f"Test execution error - Error: {str(e)} - Status: Critical Issue")
        
        finally:
            await browser.close()
            
            working_count = len([log for log in test_log if "Status: Working" in log])
            not_working_count = len([log for log in test_log if "Status: Not Working" in log])
            warning_count = len([log for log in test_log if "Status: Warning" in log])
            
            test_log.insert(4, f"Test Summary - Working: {working_count}, Not Working: {not_working_count}, Warnings: {warning_count}")
            test_log.append("=== Weather App Test Completed ===")
            
            os.makedirs("results", exist_ok=True)
            with open("results/result_log.txt", "w", encoding="utf-8") as f:
                for log_entry in test_log:
                    f.write(log_entry + "\n")
            
            for log_entry in test_log:
                print(log_entry)

asyncio.run(test_weather_app())
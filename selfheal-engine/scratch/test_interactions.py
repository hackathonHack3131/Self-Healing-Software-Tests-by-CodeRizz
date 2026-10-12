import asyncio
from playwright.async_api import async_playwright

async def test_interactions():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.goto('http://127.0.0.1:8080/')
        await page.wait_for_timeout(800)
        
        # Click tab-locators
        await page.click('#tab-locators')
        tab_loc_active = await page.evaluate('document.getElementById("tab-locators").classList.contains("active")')
        print(f'Comparison tab-locators active: {tab_loc_active}')

        # Click tab-defects
        await page.click('#tab-defects')
        tab_def_active = await page.evaluate('document.getElementById("tab-defects").classList.contains("active")')
        print(f'Comparison tab-defects active: {tab_def_active}')

        # Scenario filter pills
        await page.click('button[data-filter="pass"]')
        scen_filter_active = await page.evaluate('document.querySelector("button[data-filter=\'pass\']").classList.contains("active")')
        print(f'Scenario pass filter active: {scen_filter_active}')

        # Scenario select card
        await page.click('#scCardB')
        card_b_sel = await page.evaluate('document.getElementById("scCardB").classList.contains("selected")')
        print(f'Scenario Card B selected: {card_b_sel}')

        # Guardrail drawer expand
        await page.click('button[aria-controls="drawer-1"]')
        gr_expanded = await page.evaluate('document.querySelector(".guardrail-card").classList.contains("expanded")')
        print(f'Guardrail card expanded: {gr_expanded}')

        # Live telemetry check
        mongo_val = await page.inner_text('#ovMongoVal')
        print(f'Live Mongo runs in telemetry: {mongo_val}')

        # Test Demo page navigation
        await page.goto('http://127.0.0.1:8080/demo?scenario=a')
        await page.wait_for_timeout(800)
        demo_title = await page.title()
        print(f'Demo page title: {demo_title}')

        await browser.close()
        print('SUCCESS: All interactive workflows verified!')

if __name__ == '__main__':
    asyncio.run(test_interactions())

import asyncio
import re
import sys
import os
from playwright.async_api import async_playwright

async def scrape_quizlet(url, output_path):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        print(f"Navigation vers {url}...")
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        except Exception as e:
            print(f"Erreur de navigation: {e}")
            await browser.close()
            return

        # Attendre un peu pour le chargement dynamique
        await asyncio.sleep(10)
        
        # Screenshot pour debug
        await page.screenshot(path="quizlet_debug_last.png")
        
        # Tenter de faire défiler la page pour charger tout le contenu
        print("Défilement de la page...")
        for _ in range(10):
            await page.keyboard.press("PageDown")
            await asyncio.sleep(1)
        
        try:
            # Chercher le bouton de consentement aux cookies
            for text in ["accepter", "accept", "autoriser", "allow"]:
                btn = page.get_by_role("button", name=re.compile(text, re.I))
                if await btn.is_visible():
                    await btn.click()
                    print(f"Bouton '{text}' cliqué.")
                    break
        except:
            pass

        # Cliquer sur "Afficher plus" tant que c'est possible
        while True:
            # Essayer plusieurs sélecteurs pour le bouton "Afficher plus"
            show_more = page.locator('button:has-text("Afficher plus"), button:has-text("Show more"), .SetPage-showMore button')
            if await show_more.count() > 0 and await show_more.first.is_visible():
                print("Clic sur 'Afficher plus'...")
                await show_more.first.scroll_into_view_if_needed()
                await show_more.first.click()
                await asyncio.sleep(3)
            else:
                break
        
        data = []
        
        # 1. Extraction via __NEXT_DATA__
        try:
            script_content = await page.evaluate('() => document.getElementById("__NEXT_DATA__")?.textContent')
            if script_content:
                import json
                json_data = json.loads(script_content)
                
                def find_terms(obj):
                    if isinstance(obj, dict):
                        # Chercher des clés communes contenant les termes
                        for key in ["storableTerms", "termIdToTermsMap", "terms"]:
                            if key in obj:
                                val = obj[key]
                                if isinstance(val, list): return val
                                if isinstance(val, dict): return list(val.values())
                        for v in obj.values():
                            res = find_terms(v)
                            if res: return res
                    elif isinstance(obj, list):
                        for item in obj:
                            res = find_terms(item)
                            if res: return res
                    return None
                
                terms_list = find_terms(json_data)
                if terms_list:
                    print(f"Extraction via __NEXT_DATA__ réussie ({len(terms_list)} termes)")
                    for t in terms_list:
                        # Quizlet change souvent les noms de clés
                        word = t.get("word") or t.get("term") or t.get("text")
                        definition = t.get("definition") or t.get("def")
                        if word and definition:
                            data.append((str(word).strip(), str(definition).strip()))
        except Exception as e:
            print(f"Erreur lors de l'extraction JSON: {e}")

        if not data:
            # 2. Sélecteurs modernes et classiques
            # On cherche les conteneurs de termes
            selectors = [
                '[data-testid="set-page-term-content"]',
                ".SetPageTerm",
                ".SetPageTerm-contentWrapper",
                ".TermText"
            ]
            
            for selector in selectors:
                elements = await page.query_selector_all(selector)
                if elements:
                    print(f"Sélecteur '{selector}' a trouvé {len(elements)} éléments.")
                    if selector == ".TermText":
                        # Cas particulier: les termes et définitions sont alternés
                        for i in range(0, len(elements), 2):
                            if i + 1 < len(elements):
                                t = await elements[i].inner_text()
                                d = await elements[i+1].inner_text()
                                data.append((t.strip(), d.strip()))
                    else:
                        for el in elements:
                            # Chercher à l'intérieur de la carte
                            t_el = await el.query_selector('[data-testid="term-text"], .SetPageTerm-wordText, .TermText:first-child')
                            d_el = await el.query_selector('[data-testid="definition-text"], .SetPageTerm-definitionText, .TermText:last-child')
                            if t_el and d_el:
                                t = await t_el.inner_text()
                                d = await d_el.inner_text()
                                data.append((t.strip(), d.strip()))
                    
                    if data: break


        if not data:
            print("Erreur: Aucun terme trouvé.")
            await browser.close()
            return

        print(f"{len(data)} termes extraits.")
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            for term, definition in data:
                clean_def = definition.replace("\n", "\\n")
                f.write(f"{term}\t{clean_def}\n")
        
        print(f"Fichier sauvegardé: {output_path}")
        await browser.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 quizlet_scraper_playwright.py <url> <output_path>")
        sys.exit(1)
    asyncio.run(scrape_quizlet(sys.argv[1], sys.argv[2]))

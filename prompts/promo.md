You are an expert Python automation engineer specializing in promotional content creation.

Create a complete, production-ready script that uses **Selenium WebDriver** (or Playwright - preferred) to generate a high-quality promotional **GIF** for an ERP system demo.

### Requirements:

**Flow to Automate:**
1. Login page → Successful login (use demo credentials)
2. Main Dashboard (show charts)
3. Finance Module
4. HCM/HR Module
5. Procurement → Supplier → Purchase Order
6. Warehouse → Locations → Inventory → Variant Mix → Fabric Rolls
7. Manufacturing → BOM → Production Planning
8. Sales & Distribution → CRM → Customer → Sales → POS → Promotions
9. Projects Module
10. Access Control / Users
11. Final Reports/Dashboard overview

**Technical Specifications:**
- Smooth transitions with ActionChains (hover, click, scroll)
- Realistic delays between actions (1.2–2.5 seconds)
- High-resolution recording (1280x720 or 1920x1080)
- Final output: Optimized `promo_erp_demo.gif` (under 5MB if possible, 10–18 seconds duration)
- Professional feel with clean navigation

**Preferred Tools:**
- Playwright (recommended) with built-in video recording + convert to GIF using ffmpeg
- OR Selenium + pyautogui / mss for screen recording + imageio/ffmpeg
- Include automatic GIF optimization (palette reduction, frame rate control)

Provide:
1. Full working script with clear comments
2. Installation instructions (`playwright`, `ffmpeg`, etc.)
3. How to run command
4. Tips for making it look premium (slow zooms, highlights, etc.)

Target audience: GitHub, LinkedIn, Product Hunt, and website hero section.
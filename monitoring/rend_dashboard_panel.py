"""
    rend_dashboard_panel.py
    Export Generate image from 
    Machine Innovation Dashboard for sentiment analysis.
"""
from playwright.sync_api import sync_playwright

#USERNAME = "francesco.frigerio71@gmail.com"
USERNAME = "admin"
PASSWORD = "admin"


# https://turbo-space-fishstick-q47wggx66w63rg5-3000.app.github.dev/d/adgxjdf/a0bc2dc?orgId=1&from=now-30d&to=now&timezone=browser
DASHBOARD_URL_PANEL_1_TABLE = (
    "http://localhost:3000/"
    "d-solo/adgxjdf/a0bc2dc"
    "?orgId=1&panelId=panel-1"  
)

DASHBOARD_URL_PANEL_2_TIMESERIES = (
    "http://localhost:3000/"
    "d-solo/adgxjdf/a0bc2dc"
    "?orgId=1&panelId=panel-2"  
)

GRAFANA_URL = "http://localhost:3000"

def render_dashboard_machineinnovation(dashboard_url,file_name_png):
    """
        run render from url and file name
    """
    with sync_playwright() as p:

        browser = p.chromium.launch( headless=True,
                                    args=[ "--no-sandbox",
                                    "--disable-dev-shm-usage"
                                        ]
                                    )

        page = browser.new_page(viewport={ "width": 1600,
                                           "height": 900 })
        # 1. Vai alla pagina di login
        page.goto(f"{GRAFANA_URL}/login")

        page.fill('input[name="user"]', USERNAME)
        page.fill('input[name="password"]', PASSWORD)

        # 2. Clicca semplicemente sul pulsante di login
        page.click('button[type="submit"]')

        # 3. Invece di expect_navigation, aspetta che l'URL cambi
        # o che sparisca il form di login (segno che siamo dentro)
        page.wait_for_url(f"{GRAFANA_URL}/**")
        page.wait_for_timeout(2000) # Un piccolo secondo di respiro per i cookie

        # 4. Ora che la sessione è stabilita, vai al pannello
        page.goto(dashboard_url)

        # Aspetta che il grafico sia renderizzato
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)


        page.screenshot(path=file_name_png)

        browser.close()

render_dashboard_machineinnovation(DASHBOARD_URL_PANEL_1_TABLE,"panel_table.png")

render_dashboard_machineinnovation(DASHBOARD_URL_PANEL_2_TIMESERIES,"panel_time_series.png")

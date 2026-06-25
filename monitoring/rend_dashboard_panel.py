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
    # "?orgId=1&panelId=panel-1"  
    "?orgId=1&panelId=panel-1&from=now-90d&to=now&timezone=browser"
)

DASHBOARD_URL_PANEL_2_TIMESERIES = (
    "http://localhost:3000/"
    "d-solo/adgxjdf/a0bc2dc"
    # "?orgId=1&panelId=panel-2"  
    "?orgId=1&panelId=panel-2&from=now-60d&to=now&timezone=browser"
)

GRAFANA_URL = "http://localhost:3000"

def dump_latest_metrics():
    
    last_accuracy = 0.84  

    metrics_dict = {"accuracy": last_accuracy}

    # Salva il file nella cartella monitoring
    with open("./monitoring/latest_metrics.json", "w") as f:
         json.dump(metrics_dict, f)

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
        # page.wait_for_timeout(3000)
        page.wait_for_timeout(10000)

        if page.locator("text=Datasource not found").count() > 0:
            raise Exception("Datasource missing")
        if page.locator("text=Plugin unavailable").count() > 0:
            raise Exception("Grafana plugin missing")
        if page.locator("text=Query error").count() > 0:
            raise Exception("Grafana query error")

        page.screenshot(path=file_name_png)

        browser.close()

render_dashboard_machineinnovation(DASHBOARD_URL_PANEL_1_TABLE,"./images/dashboard_table.png")

render_dashboard_machineinnovation(DASHBOARD_URL_PANEL_2_TIMESERIES,"./images/dashboard_timeseries.png")

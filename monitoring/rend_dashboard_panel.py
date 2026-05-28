"""
    Export Generate image from 
    Machine Innovation Dashboard for sentiment analysis.
"""
from playwright.sync_api import sync_playwright

USERNAME = "admin"
PASSWORD = "pwd@1234567890FF"


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

        # login
        page.goto(f"{GRAFANA_URL}/login")

        page.fill('input[name="user"]', USERNAME)
        page.fill('input[name="password"]', PASSWORD)

        page.click('button[type="submit"]')

        # dashboard
        page.goto(dashboard_url)

        page.wait_for_timeout(5000)

        page.screenshot(path=file_name_png)

        browser.close()

render_dashboard_machineinnovation(DASHBOARD_URL_PANEL_1_TABLE,"panel_table.png")

render_dashboard_machineinnovation(DASHBOARD_URL_PANEL_2_TIMESERIES,"panel_time_series.png")

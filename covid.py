import random
import pickle
import os
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
import pandas as pd

from common import Email, get_browser, get_custom_logger
from settings import TEMP_DIR, DOCS_DIR

logger = get_custom_logger(level="INFO", stream_fmt="color", filename="covid_scraper.log")


def main():
    logger.info("Initializing...")
    driver = get_browser(incognito=True)
    driver.set_page_load_timeout(200)

    try:
        # world_stats
        page_url = "https://www.worldometers.info/coronavirus/#news"
        driver.get(page_url)

        WebDriverWait(
            driver,
            timeout=200,
        ).until(
            expected_conditions.presence_of_element_located(
                (
                    By.CLASS_NAME,
                    "news_date",
                )
            )
        )
        soup = BeautifulSoup(driver.page_source, "html.parser")
        title = soup.find("title").text.strip()

        table_val = [[] for _ in range(14)]
        table_body = soup.find("table", attrs={"id": "main_table_countries_today"}).find("tbody")
        tr_items = table_body.find_all("tr")

        for tr in tr_items:
            td_items = tr.find_all("td")[:14]
            for idx, td in enumerate(td_items):
                table_val[idx].append(td.text.strip())

        df = pd.DataFrame(
            {
                "#": table_val[0],
                "country": table_val[1],
                "total_cases": table_val[2],
                "new_cases": table_val[3],
                "total_deaths": table_val[4],
                "new_deaths": table_val[5],
                "total_recovered": table_val[6],
                "active_cases": table_val[7],
                "serious_critical": table_val[8],
                "tot_cases_per_1M_pop": table_val[9],
                "deaths_per_1M_pop": table_val[10],
                "total_tests": table_val[11],
                "tests_per_1M_pop": table_val[12],
                "population": table_val[13],
            }
        )

        file_path_1 = os.path.join(TEMP_DIR, "world_stats.csv")
        df.to_csv(file_path_1, index=False)
        logger.info("world_stats generated.")

        # usa_stats
        page_url = "https://www.worldometers.info/coronavirus/country/us/"
        driver.get(page_url)

        WebDriverWait(
            driver,
            timeout=200,
        ).until(
            expected_conditions.presence_of_element_located(
                (
                    By.CLASS_NAME,
                    "news_date",
                )
            )
        )
        soup = BeautifulSoup(driver.page_source, "html.parser")

        table_val = [[] for _ in range(11)]
        table_body = soup.find("table", attrs={"id": "usa_table_countries_today"}).find("tbody")
        tr_items = table_body.find_all("tr")

        for tr in tr_items:
            td_items = tr.find_all("td")[:11]
            for idx, td in enumerate(td_items):
                table_val[idx].append(td.text.strip())

        df = pd.DataFrame(
            {
                "state": table_val[0],
                "total_cases": table_val[1],
                "new_cases": table_val[2],
                "total_deaths": table_val[3],
                "new_deaths": table_val[4],
                "active_cases": table_val[5],
                "tot_cases_per_1M_pop": table_val[6],
                "deaths_per_1M_pop": table_val[7],
                "total_tests": table_val[8],
                "tests_per_1M_pop": table_val[9],
            }
        )

        file_path_2 = os.path.join(TEMP_DIR, "usa_stats.csv")
        df.to_csv(file_path_2, index=False)
        logger.info("usa_stats generated.")

        logger.info("Unpickling a random FAQ...")
        with open(os.path.join(DOCS_DIR, "covid_faq.pkl"), "rb") as pkl_file:
            faq = pickle.load(pkl_file)

        logger.info("Sending an email...")
        email_body = (
            random.choice(faq)
            + "\n\nSources:\n• world_stats.csv - https://www.worldometers.info/coronavirus"
            "\n• usa_stats.csv - https://www.worldometers.info/coronavirus/country/us"
            "\n• india_stats.csv - https://www.mohfw.gov.in"
            "\n• mira_bhy.txt - https://bit.ly/MiraBhyCovid19"
            "\n• mbmc_covid_report.pdf - https://www.mbmc.gov.in"
            "\n\n- Notification service designed by Cavin Dsouza\n"
            "© Copyright Worldometers.info - All rights reserved"
        )

        send_email = Email()
        send_email.send(
            from_name="Worldometer",
            to_address=["def@ghi.com"],
            bcc_address=["xyz@mno.com"],
            attachments=[
                file_path_1,
                file_path_2,
            ],
            subject=title,
            body=email_body,
        )
    except Exception as ex:
        logger.error("<%s>: %s", type(ex).__name__, ex, exc_info=True)
    finally:
        driver.quit()

    logger.info("Process completed successfully")


if __name__ == "__main__":
    main()

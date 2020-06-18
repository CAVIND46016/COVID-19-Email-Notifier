import random
import urllib.request as urllib2
import PyPDF2
from os.path import join
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas as pd
import pickle
import re
import time

from common import Email, get_browser, logger
from settings import TEMP_DIR, DOCS_DIR, EMAIL_CONNECTION_PARAMS


def main():
    log = logger(__file__, suffix='week_of_year')

    log.info("Initializing...")
    driver = get_browser(incognito=True)
    driver.set_page_load_timeout(200)

    try:
        # world_stats
        page_url = "https://www.worldometers.info/coronavirus/#news"
        driver.get(page_url)

        WebDriverWait(driver, timeout=200).until(EC.presence_of_element_located((By.CLASS_NAME, "news_date")))
        soup = BeautifulSoup(driver.page_source, "html.parser")
        title = soup.find("title").text.strip()

        table_val = [[] for _ in range(14)]
        table_body = soup.find("table", attrs={"id": "main_table_countries_today"}).find("tbody")
        tr_items = table_body.find_all("tr")

        for tr in tr_items:
            td_items = tr.find_all("td")[:14]
            for idx, td in enumerate(td_items):
                table_val[idx].append(td.text.strip())

        df = pd.DataFrame({'#': table_val[0],
                           'country': table_val[1],
                           'total_cases': table_val[2],
                           'new_cases': table_val[3],
                           'total_deaths': table_val[4],
                           'new_deaths': table_val[5],
                           'total_recovered': table_val[6],
                           'active_cases': table_val[7],
                           'serious_critical': table_val[8],
                           'tot_cases_per_1M_pop': table_val[9],
                           'deaths_per_1M_pop': table_val[10],
                           'total_tests': table_val[11],
                           'tests_per_1M_pop': table_val[12],
                           'population': table_val[13]})

        file_path_1 = join(TEMP_DIR, "world_stats.csv")
        df.to_csv(file_path_1, index=False)
        log.info("world_stats generated.")

        # usa_stats
        page_url = "https://www.worldometers.info/coronavirus/country/us/"
        driver.get(page_url)

        WebDriverWait(driver, timeout=200).until(EC.presence_of_element_located((By.CLASS_NAME, "news_date")))
        soup = BeautifulSoup(driver.page_source, "html.parser")

        table_val = [[] for _ in range(11)]
        table_body = soup.find("table", attrs={"id": "usa_table_countries_today"}).find("tbody")
        tr_items = table_body.find_all("tr")

        for tr in tr_items:
            td_items = tr.find_all("td")[:11]
            for idx, td in enumerate(td_items):
                table_val[idx].append(td.text.strip())

        df = pd.DataFrame({'state': table_val[0],
                           'total_cases': table_val[1],
                           'new_cases': table_val[2],
                           'total_deaths': table_val[3],
                           'new_deaths': table_val[4],
                           'active_cases': table_val[5],
                           'tot_cases_per_1M_pop': table_val[6],
                           'deaths_per_1M_pop': table_val[7],
                           'total_tests': table_val[8],
                           'tests_per_1M_pop': table_val[9]})

        file_path_2 = join(TEMP_DIR, "usa_stats.csv")
        df.to_csv(file_path_2, index=False)
        log.info("usa_stats generated.")

        # india_stats
        page_url = "https://www.mohfw.gov.in/"
        driver.get(page_url)

        WebDriverWait(driver, timeout=200).until(EC.presence_of_element_located((By.TAG_NAME, "footer")))
        soup = BeautifulSoup(driver.page_source, "html.parser")

        table_val = [[] for _ in range(5)]
        table_body = soup.find("table").find("tbody")
        tr_items = table_body.find_all("tr")[:-5]

        for tr in tr_items:
            td_items = tr.find_all("td")[:5]
            for idx, td in enumerate(td_items):
                if idx == 0 and (td.text == '' or not td.text):
                    table_val[idx].append('34')
                else:
                    table_val[idx].append(td.text.strip())

        df = pd.DataFrame({'S. No.': table_val[0],
                           'Name of State / UT': table_val[1],
                           'Total Confirmed cases (Including 111 foreign Nationals)': table_val[2],
                           'Cured/Discharged/Migrated': table_val[3],
                           'Death': table_val[4]})

        for col in df.columns[2:]:
            df[col] = df[col].apply(lambda x: x.replace('#', ''))
            df.loc[(df[col].isnull()) | (df[col] == ''), col] = 0
            df[col] = df[col].astype('float')

        cols = df.columns
        df.loc[len(df.index), cols] = len(df.index) + 1, 'Total', df[cols[2]].sum(),\
                                      df[cols[3]].sum(), df[cols[4]].sum()

        df = df.sort_values(by=['Total Confirmed cases (Including 111 foreign Nationals)'],
                            ascending=False).reset_index(drop=True)
        df['S. No.'] = df.index + 1

        file_path_3 = join(TEMP_DIR, "india_stats.csv")
        df.to_csv(file_path_3, index=False)
        log.info("india_stats generated.")

        # Mira Bhayander stats
        page_url = "https://bit.ly/MiraBhyCovid19"
        driver.get(page_url)

        time.sleep(10)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        content = soup.find("div", attrs={"aria-label": re.compile(r'Mira Bhayandar ')})['aria-label']
        total = soup.find("div", attrs={"id": "legendPanel"})

        summary = total.text
        tmp = summary[summary.find("Total"):]
        tmp = tmp[0: tmp.find("The data")]

        tmp1 = re.findall(r'[^\W\d_]+|\d+', tmp)
        content += "\n\n"
        for i in range(0, len(tmp1)):
            if i % 3 == 0:
                content += tmp1[i]
            elif i % 3 == 1:
                content += ' ' + tmp1[i]
            else:
                content += ' - ' + tmp1[i]
            if (i + 1) % 3 == 0:
                content += '\n'

        element = soup.find_all("div", attrs={"index": "0", "subindex": re.compile(r"\d+")})
        loc_value_sorted = sorted([ele.text for ele in element],
                                  key=lambda k: int(re.findall(r'\d+', k)[-1]) if re.findall(r'\d+', k) else 0,
                                  reverse=True)

        content += '\n' + 'Mira-Bhayandar COVID19 Cases ( Location Not Accurate):' + '\n  ' + '\n  '.join(
            loc_value_sorted)

        file_path_4 = join(TEMP_DIR, "mira_bhy.txt")
        with open(file_path_4, 'w', encoding='utf8') as file:
            file.write(content)
        log.info("mirabhy_stats generated.")

        # MBMC Covid report
        page_url = "https://www.mbmc.gov.in/"
        driver.get(page_url)

        WebDriverWait(driver, timeout=200).until(EC.presence_of_element_located((By.ID, "footer_row")))
        soup = BeautifulSoup(driver.page_source, "html.parser")

        pdf_link = None
        for a_tag in soup.find_all("a"):
            tag_text = re.sub(r' +', ' ', a_tag.text.strip())
            if re.search(r'Covid([- ])19 Daily Report', tag_text) and 'list' not in tag_text.lower():
                pdf_link = a_tag['href']
                break

        file_path_5 = join(TEMP_DIR, 'mbmc_covid_report.pdf')
        tmp_file = join(TEMP_DIR, 'covid.pdf')

        log.info("Downloading covid MBMC report...")
        opener = urllib2.URLopener()
        opener.retrieve(pdf_link, filename=tmp_file)

        pdf_writer = PyPDF2.PdfFileWriter()
        with open(tmp_file, 'rb') as pdf_file, open(file_path_5, 'wb') as pdf_output_file:
            pdf_reader = PyPDF2.PdfFileReader(pdf_file)
            pdf_writer.addPage(pdf_reader.getPage(0))
            pdf_writer.write(pdf_output_file)
        log.info("mbmc covid report generated.")

        log.info("Unpickling a random FAQ...")
        with open(join(DOCS_DIR, "covid_faq.pkl"), "rb") as pkl_file:
            faq = pickle.load(pkl_file)

        log.info("Sending an email...")
        email_body = random.choice(faq) + "\n\nSources:\n• world_stats.csv - https://www.worldometers.info/coronavirus" \
                                          "\n• usa_stats.csv - https://www.worldometers.info/coronavirus/country/us" \
                                          "\n• india_stats.csv - https://www.mohfw.gov.in" \
                                          "\n• mira_bhy.txt - https://bit.ly/MiraBhyCovid19" \
                                          "\n• mbmc_covid_report.pdf - https://www.mbmc.gov.in" \
                                          "\n\n- Notification service designed by Cavin Dsouza\n" \
                                          "© Copyright Worldometers.info - All rights reserved"

        send_email = Email(**EMAIL_CONNECTION_PARAMS)
        send_email.send(from_name='Worldometer',
                        to_address=['def@ghi.com'],
                        bcc_address=['xyz@mno.com'],
                        attachments=[file_path_1, file_path_2, file_path_3, file_path_4, file_path_5],
                        subject=title,
                        body=email_body)

    finally:
        driver.quit()

    log.info("Process completed successfully")


if __name__ == "__main__":
    main()

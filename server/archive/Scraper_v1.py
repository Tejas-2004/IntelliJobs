# this is for indeed
import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent

start_time = time.time()
user_agent = UserAgent()

chrome_options = Options()
desktop_user_agent = user_agent.random.replace("Mobile", "Desktop")
chrome_options.add_argument("--headless")  # Enable headless mode
chrome_options.add_argument(f'user-agent={desktop_user_agent}')  # Set a random user agent
chrome_options.add_experimental_option('prefs', {
    'profile.managed_default_content_settings.images': 2
})

chrome_options.add_experimental_option("detach", True)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
driver.set_window_size(1536, 864)
driver.implicitly_wait(5)

def write_to_csv(data):
    with open('Output13.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(data)

def barrier(loop):
    try:
        english_language_xpath = f"/html/body/div[2]/div[1]/div/div/div[2]/button[1]/span"
        driver.find_element(By.XPATH, english_language_xpath).click()
    except:
        print(f"no question about language- {loop}")
    try:
        browser_select_xpath = f"/html/body/main/div/div[1]/div/div[3]/button"
        driver.find_element(By.XPATH, browser_select_xpath).click()
    except:
        print("no browser or app click option")

for i in range(1, 2):
    driver.get("https://in.indeed.com/browsejobs/Software-Development")
    barrier("i")
    category_xpath = f"/html/body/div/div[2]/div/table/tbody/tr/td/ul/li[{i}]/p[1]/a"
    category = driver.find_element(By.XPATH, category_xpath)
    category_text = category.text
    print(category_text)
    category.click()
    barrier("2i")
    total_jobs_xpath = f"/html/body/main/div/div[2]/div/div[5]/div/div[1]/div[4]/div/div/div[2]/span[1]"
    total_jobs = driver.find_element(By.XPATH, total_jobs_xpath).text
    total_jobs = int(''.join(filter(str.isdigit, total_jobs)))
    for y in range(1):
        barrier("y")
        for k in range(1, 18):
            try:
                try:
                    driver.find_element(By.XPATH, "/html/body/div[3]/div[1]/div[1]/button").click()
                except:
                    print("no pop up bruv")

                left_side_job_xpath = f"/html/body/main/div/div[2]/div/div[5]/div/div[1]/div[5]/div/ul/li[{k}]/div/div/div/div/div/table[1]/tbody/tr/td[1]/div[1]/h2/a"
                driver.find_element(By.XPATH, left_side_job_xpath).click()
                job_title_xpath = f"/html/body/main/div/div[2]/div/div[5]/div/div[2]/div/div/div[2]/div[2]/div[1]/div/div[1]/div[1]/h2/span"
                job_title = driver.find_element(By.XPATH, job_title_xpath).text
                print(job_title)

                location_xpath = f"/html/body/main/div/div[2]/div/div[5]/div/div[2]/div/div/div[2]/div[2]/div[1]/div/div[1]/div[2]/div/div/div/div[2]/div"
                location = driver.find_element(By.XPATH, location_xpath).text

                job_detail = ""
                job_details_xpath = f"/html/body/main/div/div[2]/div/div[5]/div/div[2]/div/div/div[2]/div[2]/div[2]/div/div[2]/div[4]/div/div/div/div/div[1]/div[2]"
                job_details = driver.find_element(By.XPATH, job_details_xpath)
                title_h3 = job_details.find_elements(By.TAG_NAME, "h3")
                uls = job_details.find_elements(By.TAG_NAME, "ul")
                for ul, t in zip(uls, title_h3):
                    li = ul.find_elements(By.TAG_NAME, "li")
                    job_detail += f"{t.text}:"
                    z = 1
                    for l in li:
                        div_xpath = f"/html/body/main/div/div[2]/div/div[5]/div/div[2]/div/div/div[2]/div[2]/div[2]/div/div[2]/div[4]/div/div/div/div/div[1]/div[2]/div[1]/div/ul/li[{z}]/div/div/div[1]"
                        el = driver.find_element(By.XPATH, div_xpath)
                        job_detail += f"{el.text} , "
                        z = z + 1

                # description_string=""
                # job_description_xpath=f"/html/body/main/div/div[2]/div/div[5]/div/div[2]/div/div/div[2]/div[2]/div[2]/div/div[2]/div[9]"
                job_description=driver.find_element(By.ID,"jobDescriptionText")
                description_string=str(job_description.get_attribute('textContent')).strip()
                # job_description=job_description.find_elements(By.XPATH,".//*") # This selects all descendants of the div element
                # print("description string:",description_string)
 

                # Append scraped data to the CSV file
                write_to_csv([category_text, job_title, location, job_detail, description_string])

            except:
                continue

        next_button_xpath = f"/html/body/main/div/div[2]/div/div[5]/div/div[1]/nav/ul/li[6]/a"
        driver.find_element(By.XPATH, next_button_xpath).click()

driver.quit()

end_time = time.time()
print("total time taken ", (end_time - start_time)/60)

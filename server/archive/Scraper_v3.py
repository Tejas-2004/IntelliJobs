# glassdoor
import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent

import requests
from bs4 import BeautifulSoup

start_time = time.time()
user_agent = UserAgent()

chrome_options = Options()
desktop_user_agent = user_agent.random.replace("Mobile", "Desktop")
# chrome_options.add_argument("--headless")  # Enable headless mode
chrome_options.add_argument(f'user-agent={desktop_user_agent}')  # Set a random user agent
chrome_options.add_experimental_option('prefs', {
    'profile.managed_default_content_settings.images': 2
})

chrome_options.add_experimental_option("detach", True)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
driver.set_window_size(1536, 864)
driver.implicitly_wait(10)


def write_to_csv(data):
    with open('Output1000.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(data)

driver.get("https://www.glassdoor.co.in/Job/jobs-SRCH_IC2865319.htm?sortBy=date_desc")

total_jobs = driver.find_element(By.CLASS_NAME,"SearchResultsHeader_jobCount__eHngv").text
total_jobs = int(''.join(filter(str.isdigit, total_jobs)))
print("totalJOBS: ",total_jobs)

i=1
while i<2:
    print(i)
    print("----------------------------*************************************------------------")



    if(i%25==0):
        more_jobs=driver.find_element(By.CLASS_NAME,"JobsList_buttonWrapper__ticwb")
        more_jobs=more_jobs.find_element(By.TAG_NAME,"button").click()
        try:
            close_button=driver.find_element(By.CLASS_NAME,"CloseButton").click()
        except:
            print("no close button")



    try:
        element=driver.find_element(By.XPATH,f"/html/body/div[3]/div[1]/div[3]/div[2]/div[1]/div[2]/ul/li[{i}]/div/div/div[1]/div[1]/a[2]").get_attribute("href")
    except:
        element=driver.find_element(By.XPATH,f"/html/body/div[4]/div[1]/div[3]/div[2]/div[1]/div[2]/ul/li[{i}]/div/div/div[1]/div[1]/a[2]").get_attribute("href")
    print(element)


    result=requests.get(element, headers={'User-Agent': user_agent.random.replace("Mobile", "Desktop")})

    # try:
    #     print("trying")
    #     driver.find_element(By.CLASS_NAME,"TvD9Pc-Bz112c ZYIfFd-aGxpHf-FnSee").click()
    # except:
    #     pass

    # time.sleep(2)
    soup=BeautifulSoup(result.text,"html.parser")

    if("Security | Glassdoor" in str(soup.prettify())):
        print("I AM BEING BLOCKED")
    # print(soup.prettify())



    try:
        job_title=soup.find("h4", class_="heading_Heading__BqX5J heading_Subhead__Ip1aW").text
        i=i+1
    except:
        continue
        
    
    # role=soup.find("h1",class_="heading_Heading__BqX5J heading_Level1__soLZs").text
    # location=soup.find("div",class_="JobDetails_location__mSg5h").text
    # description=soup.find("div",class_="JobDetails_jobDescription__uW_fK JobDetails_blurDescription__vN7nh").text.strip()
    # salary_range=soup.find("div",class_="SalaryEstimate_salaryRange__brHFy").text
    # salary_median_estimate=soup.find("div",class_="SalaryEstimate_salaryEstimateNumber__SC4__").text
    # company_overview=soup.find("section",class_="Section_sectionComponent__nRsB2 JobDetails_jobDetailsSectionContainer__o_x6Z").text.strip()
    # overall_rating=soup.find("div",class_="EmployerProfile_ratingContainer__ul0Ef").text

    # ratings_string=""
    # ratings_label=soup.find_all("span",class_="JobDetails_ratingLabel__VJ8_o")
    # ratings_score=soup.find_all("div",class_="JobDetails_ratingScore___xSXK")
    # for label_element, score_element in zip(ratings_label, ratings_score):
    #         label_text = label_element.text.strip()
    #         score_text = score_element.text.strip()
    #         ratings_string += f"{label_text}: {score_text}\n"
    
    # job_review_pro_con=soup.select('.JobDetails_reviewSummaryWrapper__eaFbQ div')
    # pros=job_review_pro_con[0].text
    # cons=job_review_pro_con[1].text









    try:
        role = soup.find("h1", class_="heading_Heading__BqX5J heading_Level1__soLZs").text
    except:
        role = -1

    try:
        location = soup.find("div", class_="JobDetails_location__mSg5h").text
    except:
        location = -1

    try:
        job_description = soup.find("div", class_="JobDetails_jobDescription__uW_fK JobDetails_blurDescription__vN7nh").text.strip()
    except:
        job_description = -1

    try:
        salary_range = soup.find("div", class_="SalaryEstimate_salaryRange__brHFy").text
    except:
        salary_range = -1

    try:
        salary_median_estimate = soup.find("div", class_="SalaryEstimate_salaryEstimateNumber__SC4__").text
    except:
        salary_median_estimate = -1

    try:
        company_overview = soup.find("section", class_="Section_sectionComponent__nRsB2 JobDetails_jobDetailsSectionContainer__o_x6Z").text.strip()
    except:
        company_overview = -1

    try:
        overall_rating = soup.find("div", class_="EmployerProfile_ratingContainer__ul0Ef").text
    except:
        overall_rating = -1

    ratings_string = ""
    try:
        ratings_label = soup.find_all("span", class_="JobDetails_ratingLabel__VJ8_o")
        ratings_score = soup.find_all("div", class_="JobDetails_ratingScore___xSXK")
        for label_element, score_element in zip(ratings_label, ratings_score):
            label_text = label_element.text.strip()
            score_text = score_element.text.strip()
            ratings_string += f"{label_text}: {score_text}\n"
    except:
        ratings_string = -1

    try:
        job_review_pro_con = soup.select('.JobDetails_reviewSummaryWrapper__eaFbQ div')
        pros = job_review_pro_con[0].text
        cons = job_review_pro_con[1].text
    except:
        pros = cons = -1

    try:
        apply_button=soup.find("button",class_="Button_applyButton__pYKk1 Button_greenTheme__EXYIV")
        apply_link=f'www.glassdoor.co.in{apply_button["data-job-url"]}'
    except:
        apply_link=-1



    write_to_csv([job_title,role,location,job_description,salary_range,salary_median_estimate,company_overview,overall_rating,ratings_string,pros,cons,apply_link])

    # driver.back()







driver.quit()
end_time = time.time()
print("total time taken ", (end_time - start_time)/60)
# this is for naukri.com
import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent

# import requests
# from bs4 import BeautifulSoup

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
driver.maximize_window()
# driver.set_window_size(1536, 864)
driver.implicitly_wait(10)


def write_to_csv(data):
    with open('Output500.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(data)

driver.get("https://www.naukri.com/jobs-in-india?jobAge=30")

driver.find_element(By.ID,"filter-sort").click()
driver.find_element(By.XPATH,"/html/body/div/div/main/div[1]/div[2]/div[1]/div[2]/span/div/ul/li[2]/a").click()


total_jobs=driver.find_element(By.XPATH,"/html/body/div/div/main/div[1]/div[2]/div[1]/div[1]/span").text
total_job=total_jobs.split(" ")[-1]

i=1
while 18<30:

    if(i%20==0):
        driver.find_element(By.XPATH,"/html/body/div/div/main/div[1]/div[2]/div[3]/div/a[2]").click()

    try:
        element=driver.find_element(By.XPATH,f"/html/body/div/div/main/div[1]/div[2]/div[2]/div/div[{i}]/div/div[1]/a").get_attribute("href")
        driver.get(element)
    except:
        print("element xpath not there")
        continue

    # result=requests.get(element, headers={'User-Agent': user_agent.random.replace("Mobile", "Desktop")})    
    time.sleep(10)
    # soup=BeautifulSoup(result.text,"html.parser")

    # print(soup.prettify())


    print(element)




    try:
        job_title=driver.find_element(By.CLASS_NAME,"styles_jd-header-title__rZwM1").text
        print(job_title)
    except:
        print("no job title , trying again")
        continue

    try:
        company_name=driver.find_element(By.CLASS_NAME,"styles_jd-header-comp-name__MvqAI")
        company_name=company_name.find("a").text

    except:
        company_name=-1

    try:
        experience_required=driver.find_element(By.CLASS_NAME,"styles_jhc__exp__k_giM").text
    except:
        experience_required=-1

    try: #isuee
        # job_exp_salary = driver.select('.styles_jhc__exp-salary-container__NXsVd div')
        job_exp=driver.find_element(By.XPATH,"/html/body/div/div/main/div[1]/div[1]/section[1]/div[1]/div[2]/div[1]/div[1]/span").text
        job_salary=driver.find_element(By.XPATH,"/html/body/div/div/main/div[1]/div[1]/section[1]/div[1]/div[2]/div[1]/div[2]/span").text
    except:
        job_exp=-1
        job_salary=-1

    try:
        job_location=driver.find_element(By.CLASS_NAME,"styles_jhc__location__W_pVs").text
    except:
        job_location=-1

    try:
        job_posting_details=driver.find_element(By.CLASS_NAME,"styles_jhc__jd-stats__KrId0").text #posting just now fix karo bot
    except:
        job_posting_details=-1
    
    try:
        job_description=driver.find_element(By.CLASS_NAME,"styles_job-desc-container__txpYf").text
    except:
        job_description=-1

    try:
        about_company=driver.find_element(By.CLASS_NAME,"styles_about-company__lOsvW").text
    except:
        about_company=-1

    job_link=element

































    # try:
    #     job_title=soup.find("h1",class_="styles_jd-header-title__rZwM1").text
    #     print(job_title)
    # except:
    #     print("no job title , trying again")
    #     continue

    # try:
    #     company_name=soup.find("div",class_="styles_jd-header-comp-name__MvqAI")
    #     company_name=company_name.find("a").text

    # except:
    #     company_name=-1

    # try:
    #     experience_required=soup.find("div",class_="styles_jhc__exp__k_giM").text
    # except:
    #     experience_required=-1

    # try:
    #     job_exp_salary = soup.select('.styles_jhc__exp-salary-container__NXsVd div')
    #     job_exp=job_exp_salary[0].text
    #     job_salary=job_exp_salary[1].text
    # except:
    #     job_exp=-1
    #     job_salary=-1

    # try:
    #     job_location=soup.find("span",class_="styles_jhc__location__W_pVs").text
    # except:
    #     job_location=-1

    # try:
    #     job_posting_details=soup.find("div",class_="styles_jhc__jd-stats__KrId0").text #posting just now fix karo bot
    # except:
    #     job_posting_details=-1
    
    # try:
    #     job_description=soup.find("section",class_="styles_job-desc-container__txpYf").text
    # except:
    #     job_description=-1

    # try:
    #     about_company=soup.find("section",class_="styles_about-company__lOsvW").text
    # except:
    #     about_company=-1

    # job_link=element


    driver.back()
    write_to_csv([job_title,company_name,experience_required,job_exp,job_salary,job_location,job_posting_details,job_description,about_company])





# driver.quit()
end_time = time.time()
print("total time taken ", (end_time - start_time))



    



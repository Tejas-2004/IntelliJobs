# this is for glassdoor
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
    with open('Output29.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(data)


driver.get("https://www.glassdoor.co.in/Job/jobs-SRCH_IC2865319.htm?sortBy=date_desc")

total_jobs = driver.find_element(By.CLASS_NAME,"SearchResultsHeader_jobCount__eHngv").text
total_jobs = int(''.join(filter(str.isdigit, total_jobs)))

print("totalJOBS: ",total_jobs)


for i in range(2,3):

    # left_side_job=driver.find_element(By.XPATH,f"/html/body/div[3]/div[1]/div[3]/div[2]/div[1]/div[2]/ul/li[{i}]/div/div/div[1]/div[1]/a[2]")
    # left_side_job.click()

    if(i%25==0):
        more_jobs=driver.find_element(By.CLASS_NAME,"JobsList_buttonWrapper__ticwb")
        more_jobs=more_jobs.find_element(By.TAG_NAME,"button").click()


    try:
        element = driver.find_element(By.XPATH, f"/html/body/div[3]/div[1]/div[3]/div[2]/div[1]/div[2]/ul/li[{i}]/div/div/div[1]/div[1]/a[2]")
        driver.execute_script("arguments[0].click();", element)
    except:
        element = driver.find_element(By.XPATH, f"/html/body/div[4]/div[1]/div[3]/div[2]/div[1]/div[2]/ul/li[{i}]/div/div/div[1]/div[1]/a[2]")
        driver.execute_script("arguments[0].click();", element)




    try:
        close_button=driver.find_element(By.CLASS_NAME,"CloseButton").click()
    except:
        print("no close button")



    # element_xpath=f"/html/body/div[3]/div[1]/div[3]/div[2]/div[1]/div[2]/ul/li[{i}]/div/div/div[1]/div[1]/a[1]"    
    # element_xpath2=f"/html/body/div[4]/div[1]/div[3]/div[2]/div[1]/div[2]/ul/li[{i}]/div/div/div[1]/div[1]/a[1]"
    # try:
    #     job_link=f'{driver.find_element(By.XPATH,element_xpath).get_attribute("href")}'
    #     driver.get(job_link)
    #     print(job_link)
    # except:
    #     job_link=f'{driver.find_element(By.XPATH,element_xpath2).get_attribute("href")}'
    #     driver.get(job_link)
    #     print(job_link)



         

    # try:                                            
    #     job_title = driver.find_element(By.XPATH,"/html/body/div[3]/div[1]/div[3]/div[2]/div[2]/div/div[1]/header/div[1]/a/div[2]/h4").text
    # except:
    #     job_title = driver.find_element(By.XPATH,"/html/body/div[3]/div[1]/div[3]/div[2]/div[2]/div/div[1]/header/div[1]/div[1]/div/h4").text

      
                                                    # /html/body/div[4]/div[1]/div[3]/div[2]/div[2]/div/div[1]/header/div[1]/a/div[2]/h4
    
    
    job_title = driver.find_element(By.XPATH,"//h4[contains(@class, 'heading_Heading__BqX5J') and contains(@class, 'heading_Subhead__Ip1aW')]").text

    print (job_title)
    try:
        role = driver.find_element(By.XPATH,"/html/body/div[3]/div[1]/div[3]/div[2]/div[2]/div/div[1]/header/div[1]/h1").text
    except:
        role = ""

    try:
        location = driver.find_element(By.CLASS_NAME,"JobDetails_location__mSg5h").text
    except:
        location = ""

    try:
        job_description = driver.find_element(By.CLASS_NAME,"JobDetails_jobDescription__uW_fK").get_attribute('textContent').strip()
    except:
        job_description = ""

    try:
        salary_range = driver.find_element(By.CLASS_NAME,"SalaryEstimate_salaryRange__brHFy").text
    except:
        salary_range = ""

    try:
        salary_median_estimate = driver.find_element(By.CLASS_NAME,"SalaryEstimate_medianEstimate__fOYN1").text
    except:
        salary_median_estimate = ""

    try:
        company_overview = driver.find_element(By.CLASS_NAME,"Section_sectionComponent__nRsB2.JobDetails_jobDetailsSectionContainer__o_x6Z").get_attribute('textContent').strip()
    except:
        company_overview = ""

    try:
        overall_rating = driver.find_element(By.CLASS_NAME,"EmployerProfile_ratingContainer__ul0Ef").text
    except:
        overall_rating = ""

    try:
        all_ratings = driver.find_element(By.CLASS_NAME,"JobDetails_ratingTrendList__3G4DA")
        ratings_list_label = all_ratings.find_elements(By.TAG_NAME,"span")
        ratings_list_score = all_ratings.find_elements(By.CLASS_NAME,"JobDetails_ratingScore___xSXK")
        for label_element, score_element in zip(ratings_list_label, ratings_list_score):
            label_text = label_element.text.strip()
            score_text = score_element.text.strip()
            ratings_string += f"{label_text}: {score_text}\n"
    except:
        ratings_string = ""

    try:
        pros = driver.find_element(By.XPATH,"/html/body/div[3]/div[1]/div[3]/div[2]/div[2]/div/div[1]/section/div[3]/div/div[1]").get_attribute('textContent').strip()
    except:
        pros = ""

    try:
        cons = driver.find_element(By.XPATH,"/html/body/div[3]/div[1]/div[3]/div[2]/div[2]/div/div[1]/section/div[3]/div/div[2]").get_attribute('textContent').strip()
    except:
        cons = ""

    try:
        apply_link = f'www.glassdoor.co.in{driver.find_element(By.CLASS_NAME,"Button_applyButton__pYKk1.Button_greenTheme__EXYIV").get_attribute('data-job-url')}'
    except:
        apply_link = ""





























   
    # job_title=driver.find_element(By.XPATH,"/html/body/div[3]/div[1]/div[2]/div/div[1]/div/div[1]/div/header/div[1]/a/div[2]/h4").text
    # role=driver.find_element(By.XPATH,"/html/body/div[3]/div[1]/div[2]/div/div[1]/div/div[1]/div/header/div[1]/h1").text
    # location=driver.find_element(By.CLASS_NAME,"JobDetails_location__mSg5h").text
    # job_description=driver.find_element(By.CLASS_NAME,"JobDetails_jobDescription__uW_fK").get_attribute('textContent').strip()
    # salary_range=driver.find_element(By.CLASS_NAME,"SalaryEstimate_salaryRange__brHFy").text
    # salary_median_estimate=driver.find_element(By.CLASS_NAME,"SalaryEstimate_medianEstimate__fOYN1").text
    # company_overview=driver.find_element(By.CLASS_NAME,"Section_sectionComponent__nRsB2 JobDetails_jobDetailsSectionContainer__o_x6Z").get_attribute('textContent').strip()
    # overall_rating=driver.find_element(By.CLASS_NAME,"EmployerProfile_ratingContainer__ul0Ef").text
    
    # all_ratings=driver.find_element(By.CLASS_NAME,"JobDetails_ratingTrendList__3G4DA")
    # ratings_list_label=all_ratings.find_element(By.TAG_NAME,"span")
    # ratings_list_score=all_ratings.find_element(By.CLASS_NAME,"JobDetails_ratingScore___xSXK")
    # ratings_string = ""
    # for label_element, score_element in zip(ratings_list_label, ratings_list_score):
    #     label_text = label_element.text.strip()
    #     score_text = score_element.text.strip()
    #     ratings_string += f"{label_text}: {score_text}\n"

    # pros=driver.find_element(By.XPATH,"/html/body/div[3]/div[1]/div[2]/div/div[1]/div/div[1]/div/section/div[3]/div/div[1]").get_attribute('textContent').strip()
    # cons=driver.find_element(By.XPATH,"/html/body/div[3]/div[1]/div[2]/div/div[1]/div/div[1]/div/section/div[3]/div/div[2]").get_attribute('textContent').strip()
    # apply_link=f'www.glassdoor.co.in{driver.find_element(By.CLASS_NAME,"Button_applyButton__pYKk1 Button_greenTheme__EXYIV").get_attribute('data-job-url')}'
    







    # column_headings = ['Job Title','Role','Location','Job Description','Salary Range','Salary Median Estimate','Company Overview','Overall Rating','Ratings String','Pros','Cons','Apply Link']

    write_to_csv([job_title,role,location,job_description,salary_range,salary_median_estimate,company_overview,overall_rating,ratings_string,pros,cons,apply_link])

    # driver.back()
























driver.quit()

end_time = time.time()
print("total time taken ", (end_time - start_time)/60)
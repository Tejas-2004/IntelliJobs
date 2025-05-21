import requests
from pymongo import MongoClient, ASCENDING, errors
import time
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()





webhook_url = f"https://discord.com/api/webhooks/{os.getenv('webhook')}"
# MongoDB connection setup
mongo_user = os.getenv('mongo_user')
mongo_password = os.getenv('mongo_password')
if not mongo_user or not mongo_password:
    print('MongoDB credentials not found in environment variables.')
    exit(1)

try:
    client = MongoClient(f"mongodb+srv://{mongo_user}:{mongo_password}@cluster0.y3ugmg6.mongodb.net/")
    db = client.get_database('job_listings')
    collection = db['naukri_jobs']
    collection.create_index([('job_id', ASCENDING)], unique=True)
    print("Mongo connection done.")
except errors.ConnectionFailure as e:
    print(f"Error connecting to MongoDB: {e}")


def log_webhook_console(message, is_error=False):
    timestamp = datetime.now().strftime("[%H:%M:%S]")
    log_message = f"{timestamp} {'[ERROR]' if is_error else '[INFO]'} {message}"
    
    try:
        requests.post(webhook_url, json={'content': log_message})
    except Exception as e:
        print(f"Error sending message to Discord webhook: {e}")
        log_message += f" [Failed to send to webhook: {e}]"
    
    print(log_message)


def scrape_job_listings():
    job_listings_api = 'https://www.naukri.com/jobapi/v3/search'
    headers = {
        'Appid': '109',
        'Systemid': 'Naukri',
        'Content-Type': 'application/json',
        'Host': 'www.naukri.com',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36 OPR/38.0.2220.41',
        'Accept': 'application/json',
        'Connection': 'keep-alive',
    }
    params = {
        'noOfResults': '100',
        'urlType': 'search_by_location',
        'searchType': 'adv',
        'location': 'india',
        'sort': 'f',
        'pageNo': 1,
        'seoKey': 'jobs-in-india',
        'src': 'sortby',
        'glbl_qcrc': '1028',
        'jobAge': '10',
    }

    while True:
        try:
            response = requests.get(job_listings_api, headers=headers, params=params)
            response_data = response.json()

            jobs_page = []
            for job in response_data['jobDetails']:
                job_id = int(job['jobId'])
                # ms -> datetime format 
                job_created_date = int(job['createdDate']) / 1000
                parsed_date = datetime.fromtimestamp(job_created_date).strftime('%Y-%m-%dT%H:%M:%S')

                job_details = {
                    'job_id': job_id,
                    'title': job['title'],
                    'description': job['jobDescription'],
                    'locations': job['placeholders'][2]['label'].split(', ') if 'placeholders' in job else [],
                    'keywords': job['tagsAndSkills'].split(',') if 'tagsAndSkills' in job else [],
                    'company_name': job['companyName'],
                    'job_url': f"https://www.naukri.com{job['jdURL']}" if 'jdURL' in job else '',
                    'experience': job['placeholders'][0]['label'] if 'placeholders' in job else '',
                    'salary': job['placeholders'][1]['label'] if 'placeholders' in job else 'Not Disclosed',
                    'company_logo': job['logoPath'] if 'logoPath' in job else '',
                    'rating': job['ambitionBoxData']['AggregateRating'] if 'ambitionBoxData' in job and 'AggregateRating' in job['ambitionBoxData'] else 'Not Available',
                    'review_count': job['ambitionBoxData']['ReviewsCount'] if 'ambitionBoxData' in job and 'ReviewsCount' in job['ambitionBoxData'] else 0,
                    'created_on': parsed_date,
                    'uploaded_at': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                }
                jobs_page.append(job_details)

            log_webhook_console(f"✅ Scraped Page {params['pageNo']}")

            already_in_db = 0
            for job in jobs_page:
                try:
                    collection.insert_one(job)
                except errors.DuplicateKeyError:
                    already_in_db += 1
                except Exception as e:
                    log_webhook_console(f"Error inserting job into DB: {e}", is_error=True)

            log_webhook_console(f"{already_in_db} Job(s) already in DB.")

            if len(response_data['jobDetails']) < 100:
                log_webhook_console('All pages retrieved.')
                break

            params['pageNo'] += 1
            # time.sleep(10)

        except requests.exceptions.RequestException as e:
            log_webhook_console(f"Error: {e}", is_error=True)
            break


def main():
    try:
        scrape_job_listings()
    except KeyboardInterrupt:
        print("Process interrupted.")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()

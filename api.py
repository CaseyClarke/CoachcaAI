from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import base64
from PIL import Image
import requests
from flask import Flask
from flask import request


def getCoach(lastName, nccp, max_retries=5):
            output = ""

            options = webdriver.ChromeOptions()
            options.add_argument('--headless')

            driver = webdriver.Chrome(options=options)
            driver.get("https://thelocker.coach.ca/access/account/public")
            image = driver.find_element(by=By.XPATH, value="/html/body/div[1]/section/div[2]/div/div/form/fieldset/div[3]/img")

            with open("imageToSave.jpeg", "wb") as fh:
                fh.write(base64.decodebytes(bytes(image.get_attribute("src").replace("data:image/gif;base64,", ""),  "utf-8")))
            
            foo = Image.open('/Users/casey/Desktop/Projects/CoachcaAI/imageToSave.jpeg').convert('RGB')
            foo.save('/Users/casey/Desktop/Projects/CoachcaAI/imageToSave.jpeg', optimize=True, quality=95)

            api_url = 'https://api.api-ninjas.com/v1/imagetotext'
            image_file_descriptor = open('imageToSave.jpeg', 'rb')
            files = {'image': image_file_descriptor}
            headers = {'X-Api-Key': 'q7tdp7qW+feqe01vSgmOzA==s8kUhtmq1uT8X2mf'}
            r = requests.post(api_url, files=files, headers=headers)
            try:
                capchaText = r.json()[0]['text']
            except:
                print("OCR FAILED")
                return getCoach(lastName, nccp, max_retries-1)

            driver.find_element(by=By.ID, value="accountNumber").send_keys(nccp)
            driver.find_element(by=By.ID, value="lastName").send_keys(lastName)
            driver.find_element(by=By.ID, value="captchaText").send_keys(capchaText)
            driver.find_element(by=By.ID, value="view").click()

            try:
                elem = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/section/div/div[2]/div[1]/div[1]/div/span[2]/div/span[1]/div/div/div[2]/div")))
            except:
                if max_retries < 1:
                    return "CODE FAILED OR NO TRANSCRIPT"
                else:
                    return getCoach(lastName, nccp, max_retries-1)
                     
            
            course = driver.find_element(by=By.ID, value="transcript").get_attribute("innerHTML")
            courseList = [
                "Making Head Way in Sport",
                "Safe Sport Training",
                "ASAA Coach Information",
                "Coaching School Sport: Redefining Winning"
            ]

            for c in courseList:
                if course.find(c) != -1:
                    output += "true,"
                else:
                    output += "false,"

            return output



app = Flask(__name__)

@app.route("/getCoach")
def get_Coach():
    return getCoach(request.args.get('lastName'), request.args.get('nccp'), request.args.get('max_retries', 5))

if __name__ == '__main__':
   app.run()
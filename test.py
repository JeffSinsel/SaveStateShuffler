from selenium import webdriver
from selenium.webdriver.firefox.options import Options

links = [
    "https://www.coolmathgames.com/0-papas-burgeria",
    "https://www.coolmathgames.com/0-papas-burgeria",
    "https://www.coolmathgames.com/0-papas-burgeria",
    "https://www.coolmathgames.com/0-papas-burgeria",
    "https://www.coolmathgames.com/0-papas-burgeria",
    "https://www.coolmathgames.com/0-papas-burgeria",
    "https://www.coolmathgames.com/0-papas-burgeria",
    "https://www.coolmathgames.com/0-papas-burgeria",
    "https://www.coolmathgames.com/0-papas-burgeria",
    "https://www.coolmathgames.com/0-papas-burgeria",
]

options = Options()
options.add_argument("--new-window")

driver = webdriver.Firefox(options=options)

for i, link in enumerate(links):
    if i != 0:
        driver.execute_script("window.open();")
        driver.switch_to.window(driver.window_handles[-1])
    driver.get(link)
    driver.execute_script("window.stop();")

driver.switch_to.window(driver.window_handles[2])
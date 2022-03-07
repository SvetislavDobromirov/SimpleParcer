from selenium import webdriver
from selenium.webdriver.firefox.options import Options
options = Options()
options.headless = True

from datetime import datetime
import bs4
import re
from time import sleep
import csv
import os

HEADER = (
    "Слово",
    "Количество"
)
rub_list = (  # list-filter with rubbish words
    "для",
    "без",
    "вас",
    "ваш",
    "вам",
    "ваши",
    "вашу",
    "вашем",
    "все",
    "даже",
    "его",
    "если",
    "или",
    "как",
    "кто",
    "любой",
    "любая",
    "любом",
    "любую",
    "наш",
    "наша",
    "наше",
    "нем",
    "нет",
    "под",
    "после",
    "при",
    "свой",
    "свою",
    "себя",
    "саоя",
    "так",
    "такая",
    "также",
    "такое",
    "таком",
    "тем",
    "этим",
    "уже",
    "что",
    "чтобы",
    "это",
    "этом",
    "этот")


class Parcer:
    def __init__(self):
        self.final_dict = {}
        pass

    # Recieve link, return goal page
    def load_page(self, link):

        #driver = webdriver.Chrome('/usr/local/bin/chromedriver')
        
        driver = webdriver.Firefox(options=options,
                                   executable_path=f"{os.getcwd()}/geckodriver")



        driver.maximize_window()
        driver.get(link)
        pageSource = driver.page_source
        driver.quit()
        return pageSource

    #  Take page for write, string with filename, and write page to file.
    def write_page_to_file(self, page, filename):
        fileToWrite = open(filename, "w")
        fileToWrite.write(page)
        fileToWrite.close()

    # Recieve string filename, return sting text of page
    def load_page_from_file(self, filename):
        with open(filename, "r") as f:
            text = f.read()
        return text

    # Serching goal links in string text page. Return list of links
    # Only 10 links. More links can be setting in init class
    def parcing_links(self, text):
        list_links = []
        soup = bs4.BeautifulSoup(text, 'lxml')
        links_block = soup.select('div.product-card__wrapper')
        count = 0
        for block in links_block:
            href_block = block.select_one('a.product-card__main.j-card-link')
            url = href_block.get('href')
            list_links.append(url)
            count = count + 1
            if count == 10:
                break
        return list_links

    # Function find info in pages of goods and return list of string with info
    # Recieve string text page, return list of string
    def parcing_deep(self, page_text: str):
        final_list = []
        soup = bs4.BeautifulSoup(page_text, 'lxml')
        name_block = soup.select_one("h1.same-part-kt__header")

        if not name_block:
            print("Error parcing_deep no h1.same-part-kt__header")

        try:
            for tag in name_block.findAll("span"):
                if "brand" in str(tag):
                    brand = tag.text
                    final_list.append(brand)
                if "goods" in str(tag):
                    goods = tag.text
                    final_list.append(goods)
        except AttributeError:
            print("Error 118")

        if not final_list:
            print("Error 121")

        about_block = soup.select("div.collapsable__content.j-description")
        for text in about_block:
            if text.text:
                description = text.text
                final_list.append(description)
        tables = soup.select("table.product-params__table")
        tr = soup.select("tr.product-params__row")
        list_of_params = []
        for el in tr:
            par = el.select_one("td,product_params__cell")
            list_of_params.append(par.text)
            final_list.append(par.text)
        return final_list

    # Take lisr with strings from oarcing deep, split sentence, and calculate number of words
    def summ_keys(self, final_list):
        searching_list = []
        for el in final_list:
            list_split = re.split(" |,|\n|/|!|\(|\)|\"|\;|\:|\.|\-", el)
            for word in list_split:
                word = word.lower()
                if word and len(word) > 2 and not any(map(str.isdigit, word)) and word not in rub_list:
                    searching_list.append(word.lower())

        for el in searching_list:
            if el not in self.final_dict.keys():
                self.final_dict[el] = 1
            if el in self.final_dict.keys():
                self.final_dict[el] = self.final_dict[el] + 1
        return self.final_dict

    # show class dict. For testing
    def show_dict(self):
        for key, item in self.final_dict.items():
            print(f"{key} {item}")
            print("1")

    # Wtite result in file cvs. Recieve dict of words and sequence their appearing
    def write_result(self, final):
        with open("result_csv.csv", "w") as file:
            obj_csv = csv.writer(file, quoting=csv.QUOTE_MINIMAL)
            obj_csv.writerow(HEADER)
            for key, item in final.items():
                temp_list = [key, item]
                obj_csv.writerow(temp_list)


# Interface claaa
class Main:
    def __init__(self):
        self.main_link = "https://www.wildberries.ru/catalog/zhenshchinam/odezhda/dzhempery-i-kardigany"
        self.list_links = []
        self.parcer = Parcer()

    # Patcing without saving file of pages. At the end save result in cvs file
    def parcing(self):
        pageSource = self.parcer.load_page(self.main_link)
        list_links = self.parcer.parcing_links(pageSource)
        sleep(0.3)
        for el in list_links:
            pageSource = self.parcer.load_page(el)
            list_for_sum = self.parcer.parcing_deep(pageSource)
            final = self.parcer.summ_keys(list_for_sum)
            sleep(0.1)
        self.parcer.write_result(final)

    # Parding with save files of pages. At the end save result in cvs file
    def parcing_from_files(self):
        final_list = []
        list_of_param = {}
        i = 0
        while (i < 10):
            page = f"page{i + 1}.html"
            text = self.parcer.load_page_from_file(page)
            i = i + 1
            list_for_sum = self.parcer.parcing_deep(text)
            final = self.parcer.summ_keys(list_for_sum)
        self.parcer.write_result(final)
        return final

    # Update files of pages or create new files.
    def update_files(self):
        pageSource = self.parcer.load_page(self.main_link)
        self.parcer.write_page_to_file(pageSource, "page0.html")
        list_links = self.parcer.parcing_links(pageSource)
        i = 1
        for el in list_links:
            pageSource = self.parcer.load_page(el)
            self.parcer.write_page_to_file(pageSource, f"page{i}.html")
            i = i + 1

    # Run three modes
    def run(self, choose):
        if choose == "1":
            try:
                self.update_files()
                print("ОК")
            except Exception as info:
                print("Error update files")
                print(info)

        elif choose == "2":
            try:
                self.parcing_from_files()
                print("OK")
            except:
                print("Error parcing from files. Try to update files.")

        elif choose == "3":

            try:
                start_time = datetime.now()
                self.parcing()
                print(f"time = {datetime.now() - start_time}")
            except Exception as Ex:
                print("Error Parcing")
                print(Ex)
        else:
            print("Error. Something very strange")


if __name__ == "__main__":
    path_driver = f"{os.getcwd()}/geckodriver"
    print(path_driver)
    functions = ("Functions:\n"
                 "1. Update saved pages or create new.\n"
                 "2. Parcing fron saved files.\n"
                 "3. Parcing without saved files.\n")
    while True:
        choose = input(functions)
        if (choose == "1" or choose == "2" or choose == "3"):
            main = Main()
            main.run(choose)
            break
        else:
            print("Incorrect input, please repeate")

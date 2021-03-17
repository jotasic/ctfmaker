'''
1. 주어진 Url 페이지 접속
2. 웹스크래핑 시작
 - 리턴은 Map형태로 반환
3. 파일 생성
'''

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.support.expected_conditions import presence_of_all_elements_located
from selenium.webdriver.support.ui import Select

EX_LIST_URL = "https://www.leetcode.com/problemset/all/"


def getCodingTestPageUrls():
    urls = []
    options = webdriver.ChromeOptions()
    options.add_argument("headless")

    with webdriver.Chrome(ChromeDriverManager().install(), options=options) as driver:
        driverWait = WebDriverWait(driver, 30)
        driver.get(EX_LIST_URL)

        xpath = '//*[@id="question-app"]/div/div[2]/div[2]/div[2]/table/tbody[1]/tr[*]/td[3]/div/a'

        urls = [el.get_attribute("href") for el in driverWait.until(presence_of_all_elements_located(
            (By.XPATH, xpath)))]

    return urls


def getCodingTestPageInfo(urls):
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    results = []

    with webdriver.Chrome(ChromeDriverManager().install(), options=options) as driver:
        driverWait = WebDriverWait(driver, 10)

        for url in urls:
            print(f"Scrapping Page: {url}")

            driver.get(url)
            # 언어 선택 창을 연다
            driverWait.until(presence_of_element_located(
                (By.XPATH, '//*[@id="app"]/div/div[2]/div[1]/div/div[3]/div/div[1]/div/div[1]/div[1]/div'))).click()

            # 파이썬 객체를 찾는다.
            langs = driverWait.until(presence_of_element_located(
                (By.CLASS_NAME, 'ant-select-dropdown-menu'))).find_elements_by_tag_name("li")

            selectedLang = None
            for lang in langs:
                if lang.text == "Python3":
                    selectedLang = lang
                    break

            # 파이썬 객체를 선택한다.
            selectedLang.click()

            # 1. 문제의 Tittle 추출 > 파일명으로 사용
            title = driverWait.until(presence_of_element_located(
                (By.XPATH, '//*[@id="app"]/div/div[2]/div/div/div[1]/div/div[1]/div[1]/div/div[2]/div/div[1]/div[1]'))).text
            start = title.find(".") + 1
            title = title[start:].strip().replace(" ", "_")

            # 2. 문제를 추출 (문제 및  Test code 작성에 사용)
            content = driverWait.until(presence_of_element_located(
                (By.XPATH, '//*[@id="app"]/div/div[2]/div/div/div[1]/div/div[1]/div[1]/div/div[2]/div/div[2]')))

            # 2-1. Test Code에 필요한 input, output 추출
            examples = content.find_elements_by_tag_name("pre")

            inputs = []
            outputs = []
            for example in examples:
                lines = example.text.split("\n")

                if not ("input" in lines[0].lower() and "output" in lines[1].lower()):
                    continue

                startIdx = lines[0].find(":") + 1
                inputs.append(lines[0][startIdx:].strip())

                startIdx = lines[1].find(":") + 1
                outputs.append(lines[1][startIdx:].strip())

            # 2-2. 문제 및 예제를 주석으로 처리
            content = "'''\n" + content.text + "\n'''"

            # 3. Code를 추출
            codeLines = [c.text for c in driverWait.until(
                presence_of_all_elements_located((By.CLASS_NAME, 'CodeMirror-line')))]

            # 3-1. Code를 하나의 객체에 담는다.
            code = ""
            for line in codeLines:
                code += line + "\n"

            # 4. Test code에 필요한 class, 함수 명 추출
            startFind = code.rfind("class")
            startIdx = code.find(" ", startFind) + 1
            endIdx = code.find(":", startFind)
            className = code[startIdx:endIdx]

            startFind = code.rfind("def")
            startIdx = code.find(" ", startFind) + 1
            endIdx = code.find("(", startFind)
            functionName = code[startIdx:endIdx]

            instanceName = "s"

            results.append({"title": title, "content": content, "code": code, "input": inputs, "output": outputs,
                            "instanceName": instanceName, "className": className, "functionName": functionName})

        # 파일 저장
        # with open(f"{title}.py", "w") as file:
        #     file.write(content)
        #     file.write("\n\n")
        #     file.write(code)
        #     file.write("\n\n")
        #     file.write(f"{instanceName} = {className}()\n")

        #     for inputText, outputText in zip(inputs, outputs):
        #         file.writelines(
        #             f"assert {instanceName}.{functionName}({inputText}) == {outputText}\n")

    print("Done...")
    return results


def makeCodingTestFile(informations, path=""):
    for info in informations:
        print(f"saving {info['title']}")
        with open(f"{path}{info['title']}.py", "w") as file:
            file.write(info["content"])
            file.write("\n\n")
            file.write(info["code"])
            file.write("\n\n")
            file.write(f"{info['instanceName']} = {info['className']}()\n")

            for inputText, outputText in zip(info["input"], info["output"]):
                file.writelines(
                    f"assert {info['instanceName']}.{info['functionName']}({inputText}) == {outputText}\n")

    print("Done..")


if __name__ == "__main__":
    urls = ["https://www.leetcode.com/problems/two-sum/", "https://www.leetcode.com/problems/add-two-numbers/",
            "https://www.leetcode.com/problems/longest-substring-without-repeating-characters/", "https://www.leetcode.com/problems/median-of-two-sorted-arrays/"]

    # urls = ["https://www.leetcode.com/problems/add-two-numbers/"]

    urls = getCodingTestPageUrls()
    print(urls)
    results = getCodingTestPageInfo(urls)
    makeCodingTestFile(results, "/Users/tasic/results/")

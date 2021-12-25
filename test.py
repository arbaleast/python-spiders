from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import re
import requests
from bs4 import BeautifulSoup

# 添加配置防止打印一些无用的日志
options = webdriver.FirefoxOptions()
options.add_argument('-headless')
service = Service('D:\\Program Files\\geckodriver.exe')
driver = webdriver.Firefox(service=service, options=options)
driver.implicitly_wait(30)
#目标链接
url = 'http://www.jianbiaoku.com/webarbs/book/421/4246194.shtml'
# 打开网页
driver.get(url)


def get_file_name():                                                #获取规范名
    file_name = driver.find_element(By.CSS_SELECTOR, 'span.catalog_name a').text
    #print(file_name)
    return file_name

def del_hide(content):                                              #迭代，根据index删除隐藏的list元素
    #print(len(content))                                             #删除前的元素个数 
    k = 0 
    while k < len(content):
        if content[k].is_displayed() == False:
            content.pop(k) 
            del_hide(content)    
        else:
            #print('false', k)
            k += 1
    #print('当前元素数：', len(content))                                            #删除后的元素个数
    return content

def get_img_lct(element):                                           #获取图片位置序号和图片资源
    i = 0
    #print(len(element))
    img_src = {}
    
    while i < len(element):

        if len(element[i].text) == 0:
            img_path = driver.find_element(By.CSS_SELECTOR, '.book_content img').get_attribute('src')
            img_src[i] = img_path

            total = len(img_src) - 2                                #最终计算值
            img_src["img_total"] = total
            left = len(element) - int(img_src["img_total"]) 
            img_src["element_left"] = left 

            #print(len(img_src), img_src, left)
            return img_src
        else:
            left = 0
            img_src["img_total"] = 0                                #初始化字典值： img_total, element_left, img_path
            img_src["element_left"] = 0
            i += 1 
    return img_src

def img_order(dic):
    tmp_list = list(dic.keys())
    b = tmp_list[2:]
    return b       

def get_content():
    all_content = driver.find_elements(By.CSS_SELECTOR, 'div.book_right>div>p')                            
    left_elements = del_hide(all_content)                                                                   #删除内容标签的隐藏元素

    img_path = get_img_lct(left_elements)                                                               #获取图片位置，内容
    #print(img_path)

    k = 0
    i = 0                                                                                               #遍历按顺序、层级写入文本，图片
    while i < len(left_elements) - int(img_path["img_total"]):                                                                                                                                           
        body_content = driver.find_elements(By.CSS_SELECTOR, 'div.book_right>div>p')[i].text                                          
        print('写入内容：', body_content)

        write_to_file(body_content)

        if i in img_order(img_path):
            a = img_path[img_order(img_path)[k]]
            b = "[" + body_content +"]" + "(" + a + ")"
            write_to_file(b)
            print(a)
            k += 1
        
        i += 1

def deal_content_level():                                                   #将获取到的内容写入字典
    tmp_level = driver.find_element(By.CSS_SELECTOR, 'ul.book_catalog>li.li_selected').get_attribute('data-level')        ###判断当前选择的层                                                                                           
    data_level = int(tmp_level)
    print('\n\n目录层级：', data_level)                                                     #打印当前层级的class属性，显示当前所在层级

    match data_level:                                                                                        #对不同层级，分情况处理
        case 1:
            all_content = driver.find_elements(By.CSS_SELECTOR, 'div.book_right>div>p')                            
            left_elements = del_hide(all_content)
            img_path = get_img_lct(left_elements)

            l = 0 
            while l < len(left_elements) - int(img_path["img_total"]):
                body_content = driver.find_elements(By.CSS_SELECTOR, 'div.book_container>div.book_right>div>p')[l].text
                write_to_file(body_content)
                l += 1
        case 2:                                                                                                 ###对前选择的层级，文本和图片写入md文档
            get_content()
        case 3:
            get_content()

def write_to_file(text):                                                 #命名，并保存文本
    f=open( get_file_name() + '.md','a+', encoding='utf-8')
    f.writelines(text + '\n')
    f.close()

def iterate_catalog():                                              #判断所有目录是否遍历过
    current_sid = driver.find_element(By.CSS_SELECTOR, 'ul.book_catalog>li.li_selected').get_attribute('data-sid')      ###判断当前选择的层                                                                                           
    final_sid = driver.find_element(By.CSS_SELECTOR, 'ul.book_catalog>li:last-child').get_attribute('data-sid')
    counts = driver.find_elements(By.CSS_SELECTOR, 'ul.book_catalog>li')

    i = 0
    for find in counts:
        if current_sid == final_sid:
            return False
        else:
            return True
        
        #print(find.get_attribute('data-sid'), i, current_sid, final_sid)
        i += 1
                    
def main():
    #对规范目录进行迭代


    while iterate_catalog():   #当未遍历到最后目录时继续下载文本
        deal_content_level()
        driver.find_element(By.CSS_SELECTOR, '.next_catalog>a').click()
    else:
        deal_content_level()
    

    print("all text has download")  #下载完输出已完成
                

main()
#getContent()
#write_to_file("123", "something")
#iterate_catalog()
driver.quit()
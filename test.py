from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.select import Select
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
url = 'http://www.jianbiaoku.com/webarbs/book/421/4246213.shtml'
# 打开网页
driver.get(url)

def check_element_exists(driver, condition, element):               #检查元素是否存在
    try:
        driver.find_element(condition, element)
        return True
    except Exception as e:
        return False

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
    left = 0
    img_src = {'img_total': 0, 'element_left': 0, 'img_total': 0}                                #初始化字典值： img_total, element_left, img_path
    #print(len(element))
    
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
            i += 1 
    return img_src

def img_order(dic):                                                 #同上
    tmp_list = list(dic.keys())
    b = tmp_list[2:]
    return b       

def title_level(order):                                             #对标题分级
    tmp = re.split(r'[.]', order)
    match len(tmp):
        case 3:                                                     #三级标题
            return '-'
        case 1:
            return '\t-'

def write_body():                                                   #写入数据
    title_tmp = driver.find_elements(By.CSS_SELECTOR, 'div.book_right>div.book-content-show>div,p>p>span')      
    main = driver.find_elements(By.CSS_SELECTOR, 'div.book_right>div.book-content-show>p')

    left_elements = del_hide(main)                                                                         #删除内容标签的隐藏元素

    img_path = get_img_lct(left_elements)                                                                   #获取图片序数，内容，数量，并写入字典
    #print(img_path)

    k = 0
    i = 0                                                                                                   #遍历按顺序、层级写入文本，图片
    while i < len(left_elements):                                                                           #循环次数=除隐藏外的文本、图片元素总数
        if left_elements[i].tag_name == 'div':
            title_del = title_tmp[i].text
            title = '#' + title_del
            write_to_file(title)
        elif i in img_order(img_path):                                                                        #判断写入行是否为图片；否,则继续写入文字
            a = img_path[img_order(img_path)[k]]
            b = "![]" + "(" + a + ")"
            write_to_file(b)
            print(a)
            k += 1                                                                                           
        else:
            body_tmp = left_elements[i].text                #写入文本元素
            body = re.split(r'[\u2002]+', body_tmp,1)
            if len(body) == 2:                          
                level = title_level(body[0])
                write_to_file(level + body[0] + '\t' + body[1])
                print('写入内容：', level, body[0], '\t', body[1])
            else:
                print(body[0])
                write_to_file(body[0])
            
        i += 1

def get_content_level():                                            #将获取到的内容写入字典
    tmp_level = driver.find_element(By.CSS_SELECTOR, 'ul.book_catalog>li.li_selected').get_attribute('data-level')        ###判断当前选择的层                                                                                           
    data_level = int(tmp_level)
    print('\n\n目录层级：', data_level)                                                     #打印当前层级的class属性，显示当前所在层级

    match data_level:                                                                                        #对不同层级，分情况处理
        case 1:
            write_body()
        case 2:
            print('判断内容是否重复')
            if check_element_exists(driver, By.CSS_SELECTOR, 'ul.book_catalog>li.li_selected>span.fold.icon_down'):
                msg = print('跳过重复部分')
                return msg
            else:
                write_body()
        case 3:
            write_body()

def write_to_file(text):                                            #命名，并保存文本
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
    while iterate_catalog():   #当未遍历到最后目录时继续下载文本
        get_content_level()
        driver.find_element(By.CSS_SELECTOR, '.next_catalog>a').click()
    else:
        get_content_level()
    print("all text has download")  #下载完输出已完成
                

main()
driver.quit()
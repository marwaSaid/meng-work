from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

import json
import pprint
import re
import time
import datetime
import sys
import shutil
pp = pprint.PrettyPrinter(indent=4)

# all course data
date_to_use = '11-03-2014'
jsonfile = open('all-courses-' + date_to_use + '.json', 'r')
course_info = json.load(jsonfile)
jsonfile.close()

# copy previous file in case something happens
def copy_prev():
    shutil.copy('all-courses-enhanced-' + date_to_use + '.json', 'all-courses-enhanced-' + date_to_use + '-prev.json')

copy_prev()

# data already added
jsonfileprev = open('all-courses-enhanced-' + date_to_use + '.json', 'r')
try:
    courses_prev = json.load(jsonfileprev)
except ValueError:
    # no JSON objects
    courses_prev = ''

jsonfileprev.close()

guid_list = []
for course in courses_prev:
    guid_list.append(course['guid'])

# got from http://www.obeythetestinggoat.com/how-to-get-selenium-to-wait-for-page-load-after-a-click.html
def wait_for(condition_function):
    start_time = time.time()
    while time.time() < start_time + 3:
        if condition_function():
            return True
        else:
            time.sleep(0.1)
    raise Exception(
        'Timeout waiting for {}'.format(condition_function.__name__)
    )

class wait_for_page_load(object):

    def __init__(self, browser):
        self.browser = browser

    def __enter__(self):
        self.old_page = self.browser.find_element_by_tag_name('html')

    def page_has_loaded(self):
        try:
            new_page = self.browser.find_element_by_tag_name('html')
            return new_page.id != self.old_page.id
        except NoSuchElementException:
            return False

    def __exit__(self, *_):
        wait_for(self.page_has_loaded)

def iframe_src_contains_youtube(iframe):
    try:
        val = "youtube" in iframe.get_attribute("src")
        return val
    except:
        return False
    
def iframe_and_iframe_src_contains_youtube(driver):
    return EC.presence_of_element_located((By.TAG_NAME, 'iframe')) and iframe_src_contains_youtube(driver.find_element_by_tag_name('iframe'))


driver = webdriver.Firefox()
driver.get('https://courses.edx.org/login')

raw_input('press enter to continue after you logged in yourself')

# input('Click "Archived" on the side tab')

# list_of_course_links = driver.find_elements_by_class_name("course-link")

num_courses_processed = 0

if courses_prev:
    new_course_list = courses_prev
else:
    new_course_list = []

for course in course_info:
    if course['guid'] not in guid_list:
        # print course

        avail = ""
        if 'Availability' in course:
            avail = course['Availability']
        elif 'availability' in course:
            avail = course['availability']
        
        if avail != 'Starting Soon' and avail != 'Upcoming' and 'PekingX' not in course['schools'] and 'TsinghuaX' not in course['schools']:
            try:
                start = datetime.datetime.now()

                # before you open the file again, save the old version
                copy_prev()

                with open('all-courses-enhanced-' + date_to_use + '.json', 'w') as json_enhanced_file:
                    list_of_course_vids = []
                    list_of_course_subtitles = []
                    pp.pprint(course)
                    driver.get(course['url'])
                    driver.switch_to_frame(driver.find_element_by_class_name('iframe-register'))

                    # if avail != 'Starting Soon':
                    # if we are already registered, just access the courseware
                    try:
                        # driver.find_element_by_class_name("access-courseware")
                        driver.find_element_by_class_name("access-courseware").click()

                        # raw_input('press enter to continue')
                        # wait for 'Courseware' to load
                        element = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.LINK_TEXT, 'Courseware'))
                        )
                    except NoSuchElementException:
                        try:
                            if 'has-option-verified' in driver.find_element_by_class_name("action-register").get_attribute('class'):
                                # enroll in a verified course under honor system
                                driver.find_element_by_class_name("action-register").click()
                                element = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((By.NAME, "honor_mode"))
                                )
                                driver.find_element_by_name("honor_mode").click()


                                driver.get(course['url'])
                                driver.switch_to_frame(driver.find_element_by_class_name('iframe-register'))
                                driver.find_element_by_class_name("access-courseware").click()

                                # raw_input('press enter to continue')
                                # wait for 'Courseware' to load
                                element = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((By.LINK_TEXT, 'Courseware'))
                                )
                                # driver.find_element_by_class_name("access-courseware").click()
                            else:
                                # enroll in a regular course
                                driver.find_element_by_class_name("action-register").click()

                                # element = WebDriverWait(driver, 10).until(
                                    # EC.presence_of_element_located((By.CLASS_NAME, "access-courseware"))
                                # )

                                # driver.find_element_by_class_name("access-courseware").click()

                                # raw_input('press enter to continue')
                                # wait for 'Courseware' to load
                                # element = WebDriverWait(driver, 10).until(
                                    # EC.presence_of_element_located((By.LINK_TEXT, 'Courseware'))
                                # )

                                driver.get(course['url'])
                                driver.switch_to_frame(driver.find_element_by_class_name('iframe-register'))
                                driver.find_element_by_class_name("access-courseware").click()

                                # raw_input('press enter to continue')
                                # wait for 'Courseware' to load
                                element = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((By.LINK_TEXT, 'Courseware'))
                                )

                        except NoSuchElementException:
                            print "There was a NoSuchElementException"
                            # driver.get(course['url'])
                            raw_input("Press enter to continue to the next course")

                    try:
                        # driver.find_element_by_class_name("access-courseware").click()

                        # access to the courseware
                        driver.find_element_by_link_text('Courseware').click()

                        # TODO: wait for page to load
                        element = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, '//nav[@aria-label="Course Navigation"]'))
                        )
                        # raw_input('press enter to continue')

                        cousreware_url = driver.current_url
                        nav = driver.find_element_by_xpath('//nav[@aria-label="Course Navigation"]') # (find the course navigation)
                        # click each chapter in course navigation
                        chapters = nav.find_elements_by_class_name("chapter")
                        # in each chapter, click each a inside the list element (or maybe just click each list element)
                        chapter_count = 0
                        for chapter_index in range(len(chapters)):
                            nav = driver.find_element_by_xpath('//nav[@aria-label="Course Navigation"]')
                            chapters = nav.find_elements_by_class_name("chapter")
                            chapter = chapters[chapter_index]

                            chapter.find_element_by_tag_name('h3').find_element_by_tag_name('a').click()
                            links = chapter.find_elements_by_tag_name('li')

                            # raw_input('press enter to continue')

                            link_count = 0
                            for link_index in range(len(links)):
                                nav = driver.find_element_by_xpath('//nav[@aria-label="Course Navigation"]')
                                chapters = nav.find_elements_by_class_name("chapter")
                                chapter = chapters[chapter_index]

                                chapter.find_element_by_tag_name('h3').find_element_by_tag_name('a').click()

                                # raw_input('press enter to continue')

                                links = chapter.find_elements_by_tag_name('li')
                                link = links[link_index]
                                # link.find_element_by_tag_name('a').click()
                                
                                # videos within one clicked link
                                # raw_input('press enter to continue')

                                # TODO: make a better wait?
                                # wait
                                # driver.implicitly_wait(2) #seconds
                                with wait_for_page_load(driver):
                                    link.find_element_by_tag_name('a').click()

                                    vid_elems = driver.find_elements_by_class_name('seq_video')

                                    if vid_elems:
                                        vid_count = 0
                                        for vid_elem_index in range(len(vid_elems)):
                                            vid_elems = driver.find_elements_by_class_name('seq_video')

                                            if vid_elems:
                                                vid_elem = vid_elems[vid_elem_index]
                                                vid_elem.click()

                                            # raw_input('press enter to continue')

                                            try:
                                                element = WebDriverWait(driver, 10).until(
                                                    EC.presence_of_element_located((By.TAG_NAME, 'iframe'))
                                                )
                                                # driver.get(driver.current_url)
                                                # driver.implicitly_wait(3)
                                            except:
                                                driver.get(driver.current_url)
                                                driver.implicitly_wait(3)



                                            # TODO: NEED TO RELOAD THE PAGE UNTIL THE SRC OF THE IFRAME
                                            # HAS SOMETHING IN IT
                                            # try:
                                            #     element = WebDriverWait(driver,10).until(iframe_and_iframe_src_contains_youtube)
                                            # except TimeoutException:
                                            #     driver.get(driver.current_url)
                                            #     driver.implicitly_wait(3)
                                                # element = WebDriverWait(driver,10).until(iframe_and_iframe_src_contains_youtube)

                                            # try:
                                            #     element = WebDriverWait(driver, 10).until(
                                            #         EC.presence_of_element_located((By.TAG_NAME, 'iframe'))
                                            #     )
                                            #     driver.implicitly_wait(2)
                                            # except TimeoutException:
                                            #     # reload page 
                                            #     driver.get(driver.current_url)
                                            #     element = WebDriverWait(driver, 10).until(
                                            #         EC.presence_of_element_located((By.TAG_NAME, 'iframe'))
                                            #     )
                                            #     driver.implicitly_wait(2)

                                            # driver.implicitly_wait(5)
                                            iframes = driver.find_elements_by_tag_name('iframe')
                                            full_url = ''
                                            for frame in iframes:
                                                if "youtube" in frame.get_attribute('src'):
                                                    full_url = frame.get_attribute('src')

                                            # full_url = last_iframe.get_attribute('src')
                                            m = re.search('/embed/(?P<id>.*)', full_url.split('?')[0])
                                            # youtube video ID
                                            # print "videoID = ", m.group('id')
                                            if m:
                                                list_of_course_vids.append(m.group('id'))
                                            else:
                                                print "VIDEO NOT FOUND"
                                                raw_input("Press enter to continue after perhaps fixing this")
                                            transcript_link = ''

                                            try:
                                                # print "transcript download link = ", driver.find_element_by_link_text('Download transcript').get_attribute('href')
                                                transcript_link = driver.find_element_by_link_text('Download transcript').get_attribute('href')
                                            except NoSuchElementException:
                                                # print "no 'Download transcript' link found"
                                                try:
                                                    transcript_link = driver.find_element_by_link_text('transcript').get_attribute('href')
                                                except:
                                                    transcript_link = ''

                                            list_of_course_subtitles.append(transcript_link) 

                                            vid_count += 1
                                    else:
                                        try:
                                            full_url = driver.find_element_by_tag_name('iframe').get_attribute('src')
                                            m = re.search('/embed/(?P<id>.*)', full_url.split('?')[0])
                                            # youtube video ID
                                            # print "videoID = ", m.group('id')
                                            vid_id = m.group('id')

                                            try:
                                                # print "transcript download link = ", driver.find_element_by_link_text('Download transcript').get_attribute('href')
                                                transcript_link = driver.find_element_by_link_text('Download transcript').get_attribute('href')
                                            except NoSuchElementException:
                                                # print "no 'Download transcript' link found"
                                                transcript_link = ''

                                        except (NoSuchElementException, AttributeError):
                                            # print "No video on this page"
                                            vid_id = ''
                                            transcript_link = ''

                                        if vid_id != '':
                                            list_of_course_vids.append(vid_id)
                                            list_of_course_subtitles.append(transcript_link)

                                    link_count += 1

                            chapter_count += 1

                                
                        # TODO: when done with clicking around, navigate back to course ware page in courseware_url?
                    except Exception as e:
                        print "There was a Exception", e

                        # print list_of_course_vids
                        # print list_of_course_subtitles
                        raw_input('press enter to continue and record where this error came from')

                    # print list_of_course_vids
                    # print list_of_course_subtitles
                    course['vid_ids'] = list_of_course_vids
                    course['num_vids'] = len(list_of_course_vids)
                    course['subtitles'] = list_of_course_subtitles
                    # pp.pprint(course)
                    new_course_list.append(course)

                    json.dump(new_course_list, json_enhanced_file)


                    # new_course_list_as_json_obj = json.dumps(new_course_list)
                    # json.dump(new_course_list_as_json_obj, json_enhanced_file)

                    num_courses_processed += 1
                    # raw_input('press enter to continue')
                end = datetime.datetime.now()
            except:
                with open('all-courses-enhanced-' + date_to_use + '.json', 'w') as json_enhanced_file:
                    json.dump(new_course_list, json_enhanced_file)

                print "Unexpected error:", sys.exc_info()[0]
                raw_input("enter to continue")
                end = datetime.datetime.now()
                # raise

            print "num_processed = ", num_courses_processed
            print end - start

driver.quit()
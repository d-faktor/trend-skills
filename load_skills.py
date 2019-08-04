import sqlite3
import ssl
import urllib.request
import urllib.parse
import urllib.error
import json


def init_table():
    # Ignore SSL certificate errors
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    conn = sqlite3.connect('trendSkills.sqlite')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS Skills
        (skill TEXT, amount INTEGER)''')
    conn.commit()
    conn.close()


def make_vacancy_list(vacancy_list, json_vac):
    per_pages_amount = len(json_vac["items"])
    for i in range(per_pages_amount):
        vacancy_list.append(json_vac["items"][i]["id"])


def find_pages_amount(vacancy_search_url):
    try:
        hh_request = urllib.request.urlopen(
            vacancy_search_url).read().decode()  # at first step we trying to find total amount and then run search
        json_vac = json.loads(hh_request)
        return int(json_vac["pages"])
    except BaseException:
        print("Unable to open first page")
        return 0


def find_next_page(vacancy_search_url, page_num):
    try:
        next_vacancy_url = vacancy_search_url + "&page=" + str(page_num)
        hh_request = urllib.request.urlopen(next_vacancy_url).read().decode()
        json_vac = json.loads(hh_request)
        return json_vac
    except BaseException:
        print("Unable to open page")
        return []


def insert_into_db(cursor, skills):
    for skill in skills.keys():
        cursor.execute('SELECT amount FROM Skills WHERE skill=?', (skill,))
        try:
            row = cursor.fetchone()
        except:
            row = None

        if row is None:
            cursor.execute('INSERT OR IGNORE INTO Skills (skill, amount) VALUES ( ?, ?)', (skill, skills[skill]))
        else:
            cursor.execute('UPDATE Skills SET amount = amount + ? WHERE skill = ?', (skills[skill], skill))


def add_skills(json_vac, skills):
    skills_amount = len(json_vac)
    for i in range(skills_amount):
        skills[json_vac[i]["name"]] = skills.get(json_vac[i]["name"], 0) + 1


def find_skills(vacancy_list, cursor):
    current_vacancy_url = "https://api.hh.ru/vacancies/"
    skills = dict()
    for vacancy_id in vacancy_list:
        hh_request = urllib.request.urlopen(current_vacancy_url + str(vacancy_id)).read().decode()
        json_vac = json.loads(hh_request)
        if len(json_vac["key_skills"]) > 0:
            add_skills(json_vac["key_skills"], skills)
    insert_into_db(cursor, skills)


def crawl_skills(vacancy_search_url):
    conn = sqlite3.connect('trendSkills.sqlite')
    cur = conn.cursor()

    pages_amount = find_pages_amount(vacancy_search_url)
    vacancy_list = list()
    for i in range(pages_amount):
        json_vac = find_next_page(vacancy_search_url, i)
        make_vacancy_list(vacancy_list, json_vac)
    find_skills(vacancy_list, cur)
    print("Skills from", pages_amount, "pages is found.")
    conn.commit()
    cur.close()


if __name__ == '__main__':
    init_table()
    while True:
        date_from = input('Input date from(YYYY-MM-DD format). Enter to exit:')
        if len(date_from) < 1:
            break

        date_to = input('Input date to(YYYY-MM-DD format). Enter to exit:')
        if len(date_to) < 1:
            break

        vacancy_search_url = "https://api.hh.ru/vacancies?specialization=1.221&date_from=" + date_from + "&date_to=" + date_to
        print(vacancy_search_url)
        crawl_skills(vacancy_search_url)

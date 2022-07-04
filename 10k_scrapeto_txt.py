import pdb
import time
import pandas as pd
import urllib
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup as BeautifulSoup
# from fake_useragent import UserAgent
import requests
# ua = UserAgent()
import os



# Given CIK of a company, it returns the links to all the 10-K reports
def get_list(cik):
    print(cik)
    base_url = "http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&type=10-K&count=1000&output=xml&CIK=" + str(cik)
    
    href = []

    req = requests.get(base_url, headers={'User-Agent': 'Mozilla/5.0'})
    # req = req.json()
    # print('request complete')
    # print(req)
    html = req.content
    # print('urlopen complete'+'-'*50)
    # print(html)


    sec_soup = BeautifulSoup(html, features='xml')

    # sec_page = urlopen(Request(base_url, headers={'User-Agent': 'Mozilla/5.0'}))

    # sec_page = urlopen(Request(base_url, headers={'User-Agent': 'Safari'}))
    # sec_page = urllib.request.urlopen(base_url)
    # sec_soup = BeautifulSoup(sec_page)

    filings = sec_soup.find_all("filing")
    # filings = sec_soup.find_all('filing')
    # print(filings)

    for filing in filings:
        date = str(filing.find("dateFiled"))[11:21]

        # report_year = int(filing.datefiled.get_text()[0:4])
        # report_year = int(filing.get('dateFiled')[0:4])
        report_year = date[0:4]

        if (filing.type.get_text() == "10-K"):
            href.append(filing.filingHREF.get_text())
    
    return href


# Given links of 10-K reports it downloads txt file from each of the links 
# and creates the folder for a company(cik) with all its reports
def download_report(url_list, cik):
    years = []
    
    target_base_url = 'http://www.sec.gov'
    
    for report_url in url_list:

        report_page = requests.get(report_url, headers={'User-Agent': 'Mozilla/5.0'})

        # report_page = urlopen(Request(report_url, headers={'User-Agent': 'Chrome/77./0.3865.90'}))
        # report_page = urllib.request.urlopen(report_url)
        html = report_page.content
        report_soup = BeautifulSoup(html, features='xml')
        
        xbrl_file = report_soup.findAll('tr')
        # print(xbrl_file)

        for item in xbrl_file:
            # print(item)
            try:
                a = item.findAll('td')[1].get_text()

                # if 'text file' in item.findAll('td')[1].get_text():
                if 'text file' in a:
                    # Get year in which it was filed
                    year = item.findAll('td')[2].get_text().split('-')[1]
                    if int(year) >= 0 and int(year) <= 50:
                        year = '20' + year
                    else:
                        year = '19' + year

                    # Get the txt file
                    txt_link = target_base_url + item.findAll('td')[2].find('a')['href']
                    
                    req = requests.get(txt_link, headers={'User-Agent': 'Mozilla/5.0'})
                    
                    txt_report = req.content

                    # txt_report = urlopen(Request(txt_link, headers={'User-Agent': 'Mozilla/5.0'}))
                    # txt_report = urllib.request.urlopen(txt_link)

                    # Make folder for the company if it doesnt exist
                    if not os.path.exists('dataset/' + cik):
                        os.makedirs('dataset/' + cik)

                    # Create txt file for the report in its folder
                    output = open('dataset/' + cik + '/' + year + '.txt', 'wb')
                    # output.write(txt_report.read())
                    output.write(txt_report)
                    output.close()


                    years.append(year)
                    print('Download Successful')
                    #
                    # Wait for a while 
                    time.sleep(3)
            except:
                pass


    return years


fwrite = open('index.txt', 'a')
# fwrite.write('CIK|Ticker|Name|Exchange|SIC|Business|Incorporated|IRS|Years_of_files\n')


# dataframe 생성 완료
df = pd.DataFrame(columns=['CIK'])
for line in open("cik_ticker.csv", 'r'):
    row = line.split('|')
    cik = row[0]
    if cik == 'CIK':
        pass
    else:
        ap = {'CIK': cik}
        df = df.append(ap, ignore_index=True)

# df2 = df.iloc[9865:]

#change to df2 to continue
for cik in df['CIK']:
    print('Trying for: ' + str(cik))

    url_list = get_list(cik)
    print('Got list for for: ' + str(cik))

    years = download_report(url_list, cik)
    
    # break
    # pdb.set_trace()
    
    if years:
        years = ','.join(years)
        write_line = line.strip() + '|' + years + '\n'
        fwrite.write(write_line)
        print(cik)
    print('--' * 50, '\n')

# for line in open("cik_ticker.csv", 'r'):
#     row = line.split('|')
#     cik = row[0]

#     if cik =='CIK':
#         continue
#     else:
#         print('Trying for: ' + str(cik))

#         url_list= get_list(cik)
#         print('Got list for for: ' + str(cik))

#         years = download_report(url_list, cik)

#         # pdb.set_trace()
#         if years:
#             years = ','.join(years)
#             write_line = line.strip() + '|' + years + '\n'
#             fwrite.write(write_line)
#             print(cik)
#     print('--'*50, '\n')

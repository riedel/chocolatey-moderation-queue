import requests
from bs4 import BeautifulSoup
import bs4
import locale
import pandas as pd

locale.setlocale( locale.LC_ALL, 'en_US.UTF-8' ) 
i=0;
n=0;
dfs=[]
while True:
  # URL of the webpage containing the list item
  i=i+1
  url = f"https://community.chocolatey.org/packages?q=&moderatorQueue=true&moderationStatus=all-statuses&prerelease=false&sortOrder=package-download-count&page={i}"
  
  # Send a GET request to the URL
  response = requests.get(url)
  
  # If the GET request is successful, the status code will be 200
  if response.status_code == 200:
      # Get the content of the response
      page_content = response.content
  
      # Create a BeautifulSoup object and specify the parser
      soup = BeautifulSoup(page_content, 'html.parser')
  
      list = soup.select('ul.package-list-view')
      # Find all list items on the page
      list_items = list[0].children
      
      # Loop through each list item
      j=0
      for item in list_items:
          package={}
          j=j+1
          # Find the package name
          if type(item) == bs4.element.NavigableString :
             continue
          n=n+1
          _,_,package["id"],package["version"] = item.find('a').get('href').split('/')
          #text.strip()
          #package["name"] = ' '.join(package_name.split(' ')[:-1])
          #package["version"] = package_name.split(' ')[-1]
          package["downloads"] = locale.atoi(item.select('span.badge')[0].text.strip().split(' ')[0])
          package["url"]=f"https://community.chocolatey.org/api/v2/Packages(Id='{package['id']}',Version='{package['version']}')"
          entry = BeautifulSoup(requests.get(package["url"]).content, 'xml').find('entry')
          properties = {child.name: child.text for child in entry.find("m:properties").findChildren()}
          properties["DownloadCount"] = package["downloads"]
          properties["Id"] = package["id"]
          dfs.append(properties)
      if j<30:
            break 
else:
    print("Failed to retrieve the webpage")

df=pd.DataFrame.from_records(dfs)
# Reorder DataFrame
important_columns=["Id", "Version", "Title", "DownloadCount"]
package_columns = [col for col in df.columns if col.startswith('Package')]
# other_columns = [col for col in df.columns if not col in (important_columns + package_columns)]
df = df[important_columns + package_columns]
print(df.to_markdown('README.md'))
df.to_csv('moderator_queue.csv') 

# vgchartzfull - A crawler to download data from Global Videogame Sales

vgchartzfull.py is a python@3 crawler script based on BeautifulSoup.
It creates a csv dataset with data from 61,181 games. based on data from [VGChartz Site](http://www.vgchartz.com/gamedb/).  

## Output

The dataset is saved in the file specified at cfg/resources.json, by default "dataset/vgsales.csv".

## Install & execution

You will need to have some dependencies compiled at **requirements.txt**.

It can be installed by pip.

```bash

  # Install dependencies
  $> pip install -r requirements.txt
  
  # Run
  $> python vgchartzfull.py
  

```

## Dictionary

The dataset it's composed by this fields, and the data is collected with this [methodology](https://www.vgchartz.com/methodology.php).

| Field | Description              |
|-------|--------------------------|
| Rank  | Ranking of overall sales |
| Name | The games name |
| Genre | Genre of the game |
| Platform | Platform of the games release (i.e. PC,PS4, etc.) |
| Developer | Developer of the game | 
| Publisher | Publisher of the game |
| Vgchartz_Score | Score at VGcharz site | 
| Critic_Score | Score at Critic | 
| User_Score | Score by VGcharts users' site | 
| Total_Shipped | Total worldwide shipments (in millions) | 
| Total_Sales | Total worldwide sales (in millions) |
| NA_Sales | Sales in North America (in millions) |
| EU_Sales | Sales in Europe (in millions) |
| JP_Sales | Sales in Japan (in millions) |
| Other_Sales | Sales in the rest of the world (in millions) |
| Release_Date | Year of the game's release |
| Last_Update | Last update of this register |

## TODO

- [x] Fetch Each Genre Separately
- [x] Scrap the Genre names from the page, instead of specify them hardcode on an arrary. 
- [x] Replace the Rank Column with the Unique Id of vgsales site.
- [x] Add Genre Column 
- [x] Data Cleanse:
  - [x] Merge all files
  - [x] Merge the Total_Shipped and Total_Sales columns as it seems they completes 
- [ ] Add Jupyter notebook for Pivots, and statistics, and Trends. 
- [ ] publish output to Github web site. 
- [ ] Add some unit testing, based on Github testing, to create a daily built of the site. 

## Links

* [vgchartz.com](https://www.vgchartz.com)
* [Original Crawler](https://github.com/GregorUT/vgchartzScrape)
* [Kaggle Dataset](https://www.kaggle.com/gregorut/videogamesales)

## Greetings

Thanks to [Chris Albon](http://chrisalbon.com/python/beautiful_soup_scrape_table.html) 

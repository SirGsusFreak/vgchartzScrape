from bs4 import BeautifulSoup, element
from random import randint, choice, shuffle
import urllib
import urllib.request
import pandas as pd
import numpy as np
import logging
import time
import json
import os

def create_random_header():
    """
    Create a random user agent in order to better mimic user behaviour.
    :return JSON with User-Agent as key and random browser-os combo as value
    """
    browsers = ["Mozilla", "Chrome"]
    os_list = ["Windows NT 6.1; Win64; x64", "X11; Linux x86_64"]
    major_version = randint(properties['minimum_major_version'], properties['maximum_major_version'])
    minor_version = randint(properties['minimum_minor_version'], properties['maximum_minor_version'])
    chosen_browser = choice(browsers)
    chosen_os = choice(os_list)

    user_agent = '{}/{}.{} ({})'.format(
        chosen_browser,
        major_version,
        minor_version,
        chosen_os)
    header = {'User-Agent': user_agent}
    return header

def generate_remaining_url(*, query_parameters):
    """
    Generate an url with a list of videogames from the query params configured at resources.json
    :return: Url with page number
    """
    reply=''
    for param in query_parameters:
        value=query_parameters.get(param, None)
        reply += f"&{param}={value}" if value is not None else f"&{param}="
    logging.debug(f"Url Generated: {base_url}N{reply}")
    return reply

def get_page(*, url):
    """
    Perform a GET request to the given URL and return results.
    Add a wait logic that, combined with random header, will help avoiding
    HTTP 429 error.
    :param url: webpage URL
    :return: HTML page's body
    """
    logging.debug("Current URL: {}".format(url))
    header = create_random_header()
    request = urllib.request.Request(url, headers=header)
    result = urllib.request.urlopen(request).read()
    time.sleep(randint(properties['minimum_sleep_time'], properties['maximum_sleep_time']))
    return result

def parse_number(*, number_string):
    """
    Return string parsed to float with custom format for millions (m)
    :param number_string:
    :return: a float number right parsed
    """
    if "m" in number_string:
        reply = number_string.strip('m')
        reply = str(float(reply) * 1000000)
    else:
        reply=number_string

    return float(reply) if not reply.startswith("N/A") else np.nan

def parse_date(*, date_string):
    """
    Return the date received as string onto timestamp or N/A.
    :param date_string:
    :return: A timestamp in panda date format
    """
    if date_string.startswith('N/A'):
        date_formatted = 'N/A'
    else:
        #i.e. date_string = '18th Feb 20'
        date_formatted = pd.to_datetime(date_string)

    return date_formatted

def add_current_game_data(*,
                          current_id,
                          current_game_name,
                          current_game_genre,
                          current_platform,
                          current_publisher,
                          current_developer,
                          current_vgchartz_score,
                          current_critic_score,
                          current_user_score,
                          current_total_shipped,
                          current_total_sales,
                          current_sales_na,
                          current_sales_pal,
                          current_sales_jp,
                          current_sales_ot,
                          current_release_date,
                          current_last_update):
    """
    Add all the game data to the related lists
    """
    game_name.append(current_game_name)
    id.append(current_id)
    platform.append(current_platform)
    genre.append(current_game_genre)
    publisher.append(current_publisher.strip())
    developer.append(current_developer.strip())
    vgchartz_score.append(current_vgchartz_score)
    critic_score.append(current_critic_score)
    user_score.append(current_user_score)
    total_shipped.append(current_total_shipped)
    total_sales.append(current_total_sales)
    sales_na.append(current_sales_na)
    sales_pal.append(current_sales_pal)
    sales_jp.append(current_sales_jp)
    sales_ot.append(current_sales_ot)
    release_date.append(current_release_date)
    last_update.append(current_last_update)

def download_data(*, start_page, end_page, genre):
    """
    Download games data from vgchartz: only data whose pages are in the range (start_page, end_page) will be downloaded
    :param start_page:
    :param end_page:
    :param genre:
    :return:
    """
    downloaded_games = 0  # Results are decreasingly ordered according to Shipped units
    for page in range(start_page, end_page + 1):
        page_url = "{}{}{}".format(base_url, str(page), remaining_url)
        current_page = get_page(url=page_url)
        soup = BeautifulSoup(current_page, features="html.parser")
        logging.info("Downloaded page {}".format(page))

        # get the first page, and find number of result for the specific Genre.
        th_tags = soup.find("th")
        record_count = int(th_tags.contents[0][(len('Results: (')):][:-1].replace(',', ''))
        logging.info("Number of games found: {}".format(record_count))

        # We locate the game through search <a> tags with game urls in the main table
        a_tags = soup.find_all("a")
        game_tags = list(filter(lambda x: x.attrs['href'].startswith('https://www.vgchartz.com/game/'), a_tags[10:]))

        for tag in game_tags:
            current_game_name = " ".join(tag.string.split())
            data = tag.parent.parent.find_all("td")

            # Get the resto of attributes traverse up the DOM tree looking for the cells in results' table
            current_platform = data[3].find('img').attrs['alt']
            current_publisher = data[4].string
            current_developer = data[5].string
            current_vgchartz_score = parse_number(number_string=data[6].string)
            current_critic_score = parse_number(number_string=data[7].string)
            current_user_score = parse_number(number_string=data[8].string)
            current_total_shipped = parse_number(number_string=data[9].string)
            current_total_sales = parse_number(number_string=data[10].string)
            current_sales_na = parse_number(number_string=data[11].string)
            current_sales_pal = parse_number(number_string=data[12].string)
            current_sales_jp = parse_number(number_string=data[13].string)
            current_sales_ot = parse_number(number_string=data[14].string)
            current_release_date = parse_date(date_string=data[15].string)
            current_last_update = parse_date(date_string=data[16].string)
            game_url = tag.attrs['href']
            current_id = int(game_url[(len('https://www.vgchartz.com/game/')):].split('/')[0])

            # game genre is fetched from the query
            current_game_genre = genre

            add_current_game_data(
                current_id = current_id,
                current_game_name=current_game_name,
                current_game_genre=current_game_genre,
                current_platform=current_platform,
                current_publisher=current_publisher,
                current_developer=current_developer,
                current_vgchartz_score=current_vgchartz_score,
                current_critic_score=current_critic_score,
                current_user_score=current_user_score,
                current_total_shipped=current_total_shipped,
                current_total_sales=current_total_sales,
                current_sales_na=current_sales_na,
                current_sales_pal=current_sales_pal,
                current_sales_jp=current_sales_jp,
                current_sales_ot=current_sales_ot,
                current_release_date=current_release_date,
                current_last_update=current_last_update)

            downloaded_games += 1

    logging.info("Number of downloaded resources: {}".format(downloaded_games))
    return record_count, downloaded_games

def save_games_data(*, filename, separator, enc):
    """
    Save all the downloaded data into the specified file
    :param filename
    :param separator
    :param enc
    """
    columns = {
        'Id': id,
        'Name': game_name,
        'Genre': genre,
        'Platform': platform,
        'Publisher': publisher,
        'Developer': developer,
        'Vgchartz_Score': vgchartz_score,
        'Critic_Score': critic_score,
        'User_Score': user_score,
        'Total_Shipped': total_shipped,
        'Total_Sales': total_sales,
        'NA_Sales': sales_na,
        'PAL_Sales': sales_pal,
        'JP_Sales': sales_jp,
        'Other_Sales': sales_ot,
        'Release_Date': release_date,
        'Last_Update': last_update
    }

    df = pd.DataFrame(columns)
    df = df[[ 'Id', 'Name', 'Genre', 'Platform', 'Publisher', 'Developer',
              'Vgchartz_Score', 'Critic_Score', 'User_Score', 'Total_Shipped',
              'Total_Sales', 'NA_Sales', 'PAL_Sales', 'JP_Sales', 'Other_Sales',
              'Release_Date', 'Last_Update' ]]

    df.to_csv(filename, sep=separator, encoding=enc, index=False)

def apply_func(row):

    if row['Total_Sales'] is None:
        row['Total_Sales'] = row['Total_Shipped']
    return row


def merge_csv_files(base_path, separator, enc):
    output_file = 'vgsales.csv'
    all_files = [f for f in os.listdir(base_path)
                 if os.path.isfile(os.path.join(base_path, f)) and f.endswith('.csv') and f != output_file]
    li = []
    for filename in all_files:
        df = pd.read_csv(base_path + '/' + filename, index_col=None, header=0)
        li.append(df)
    df = pd.concat(li, axis=0, ignore_index=True)

    df = df.apply(apply_func, axis=1)
    del df['Total_Shipped']

    df.to_csv(base_path + '/' + output_file, sep=separator, encoding=enc, index=False)


if __name__ == "__main__":

    properties = None

    with open("cfg/resources.json") as file:
        properties = json.load(file)

    logging.root.handlers = []
    logging.basicConfig(format='%(asctime)s|%(name)s|%(levelname)s| %(message)s',
                        level=logging.DEBUG,
                        filename=properties["application_log_filename"])

    # set up logging to console
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)

    # set a format which is simpler for console use
    formatter = logging.Formatter(fmt='%(asctime)s|%(name)s|%(levelname)s| %(message)s', datefmt="%d-%m-%Y %H:%M:%S")
    console.setFormatter(formatter)
    logging.getLogger("").addHandler(console)

    logging.info('Application started')
    base_url = properties['base_page_url']
    params_dict = properties['query_parameters']

    # Buffers
    id = []
    game_name = []
    genre = []
    platform = []
    publisher, developer = [], []
    critic_score, user_score, vgchartz_score = [], [], []
    total_shipped = []
    total_sales, sales_na, sales_pal, sales_jp, sales_ot = [], [], [], [], []
    release_date, last_update = [], []

    # download the first page and get the number of records from it.
    params_dict = properties['query_parameters']
    required_results = params_dict['results']
    params_dict['results'] = '1'
    remaining_url = generate_remaining_url(query_parameters=params_dict)
    page_url = "{}{}{}".format(base_url, str(1), remaining_url)
    logging.info("Downloading First Page for it's meta data")
    current_page = get_page(url=page_url)

    soup = BeautifulSoup(current_page, features="html.parser")
    select_tags = soup.find_all("select")
    generes_tag = list(filter(lambda x: x.attrs['name'] == 'genre', select_tags))[0]
    genres_list = [x.attrs['value'].replace(' ', '+') for x in generes_tag.findChildren('option') if x.attrs['value'] != '']
    logging.info("Geners Found: {}".format(genres_list))

    # get the first page, and find number of result for the specific Genre.
    th_tags = soup.find("th")
    record_count = int(th_tags.contents[0][(len('Results: (')):][:-1].replace(',', ''))
    logging.info("Number of games found: {}".format(record_count))

    params_dict['results'] = required_results
    shuffle(genres_list)
    total_record_count = 0
    for cur_genre in genres_list:
        params_dict['genre'] = cur_genre
        remaining_url = generate_remaining_url(query_parameters=params_dict)
        start_page_no = 1

        # Reset Buffers
        id = []
        game_name = []
        genre = []
        platform = []
        publisher, developer = [], []
        critic_score, user_score, vgchartz_score = [], [], []
        total_shipped = []
        total_sales, sales_na, sales_pal, sales_jp, sales_ot = [], [], [], [], []
        release_date, last_update = [], []
        end_page_no = 1

        # download the first page and get the number of records from it.
        record_count, downloaded = download_data(
            start_page=start_page_no,
            end_page=start_page_no,
            genre=cur_genre)

        total_record_count += downloaded

        start_page_no += 1
        while len(id) < record_count:
            record_count, downloaded = download_data(
                start_page=start_page_no,
                end_page=start_page_no,
                genre=cur_genre)
            start_page_no += 1
            total_record_count += downloaded

        save_games_data(
            filename='dataset/vgsales_' + cur_genre + '.csv',
            separator=properties['separator'], enc=properties['encoding'])

    merge_csv_files('dataset', separator=properties['separator'], enc=properties['encoding'])

    logging.info("Fetched records: {}".format(total_record_count))


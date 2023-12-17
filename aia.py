import os
import datetime
import requests
import os.path
from datetime import datetime, timedelta
import requests
import re
from bs4 import BeautifulSoup

def listFD(url, ext=''):
    """
    Generate a list of file URLs with a specified file extension in a given directory URL.

    Args:
        url (str): The URL of the directory to list files from.
        ext (str, optional): The file extension to filter by. Defaults to an empty string (no filtering).

    Returns:
        list: A list of file URLs in the specified directory with the given file extension.

    Example:
        file_urls = listFD('https://example.com/files', ext='.txt')
    """
    page = requests.get(url).text
    soup = BeautifulSoup(page, 'html.parser')
    return [url + '/' + node.get('href') for node in soup.find_all('a') if node.get('href').endswith(ext)]

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)

class AIA:

    def download_range(start_date, end_date, channel, resolution, download_path):
        """
        Download a range of SDO (Solar Dynamics Observatory) images for a specific channel and resolution.

        Args:
            start_date (datetime): The start date for the range.
            end_date (datetime): The end date for the range.
            channel (str): The SDO channel identifier. For example, '0171', '0193', '0304'.
            resolution (str): The resolution of the images. For example, '512', '1024'.
            download_path (str): The local directory path where the images will be downloaded.

        Returns:
            None

        Example:
            start_date = datetime(2023, 12, 1)
            end_date = datetime(2023, 12, 17)
            channel = '0193'
            resolution = '512'
            download_path = '/path/to/download'
            download_range(start_date, end_date, channel, resolution, download_path)
        """      
        # https://sdo.gsfc.nasa.gov/assets/img/browse/2023/12/17/20231217_154717_512_0193.jpg 
        sdo_url = "https://sdo.gsfc.nasa.gov"
        browse_path = "/assets/img/browse/"
        
        for single_date in daterange(start_date, end_date):
            print(f"Downloading:... {single_date.strftime('%Y-%m-%d')}")
            dayurl = f"https://sdo.gsfc.nasa.gov/assets/img/browse/{single_date.strftime('%Y/%m/%d')}"
            files = listFD(dayurl, "jpg")
            
            needle = f"{resolution}_{channel}.jpg"
            filesOfInterest = filter(lambda f: needle in f, files)
            
            for file in filesOfInterest:
                # Determine date "20231217_170741_512_0193.jpg"
                f = os.path.splitext(os.path.basename(file))[0]
                split = f.split('_')
                stamp = split[0]+split[1]
                # 20231217153753
                date = datetime.strptime(stamp, '%Y%m%d%H%M%S')
                if(date < start_date):
                    continue
                # Download
                filename = os.path.join(download_path, f"{os.path.basename(file)}")
                
                if(not os.path.isfile(f"{filename}")):
                    print(f"Download: {file} => {filename}")
                    try:
                        response = requests.get(file)
                        response.raise_for_status()  # Raise an HTTPError for bad responses
                        with open(filename, 'wb') as file:
                            file.write(response.content)
                    except requests.exceptions.RequestException as e:
                        print(f"Error {file} => {filename} ({e})")
                else:
                    print(f"Exists: {file} => {filename}")
        
    def download_latest_time(channel):
        """
        Download the latest timestamp from the Solar Dynamics Observatory (SDO) for a specified channel.

        Args:
            channel (str): The SDO channel identifier. Possible values are '0094', '0131', '0171', '0193', '0211', '0304', '0335',
                        '1600', '1700', 'HMIB', 'HMII', 'HMID', 'HMIBC', 'HMIIF', 'HMIIC'.

        Returns:
            datetime: The timestamp of the latest image capture.

        Notes:
            The function fetches the timestamp data from the 'times' file associated with the specified SDO channel.
            If the download fails, the current time is used as a fallback timestamp.

        Example:
            timestamp = download_latest_time('0193')
        """
        # Construct URLs for the latest image and its corresponding timestamp
        sdo_url = "https://sdo.gsfc.nasa.gov"
        latest_path = "/assets/img/latest/"
        latest_times = f"times{channel}.txt"
        timesurl = f"{sdo_url}/{latest_path}{latest_times}"

        # Fetch timestamp data from the times file
        try:
            times = requests.get(timesurl)                    
        except requests.exceptions.RequestException as e:
            print(f"Error downloading file: {e}")

        # Extract timestamp using regular expressions
        match = re.search(r'^[^:]*:\s*(.*)$', times.text)
        if match:
            timestring = match.group(1)
        else:
            # use current time is times file download failed
            timestring = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Convert timestamp string to a datetime object
        timestamp = datetime.strptime(timestring, "%Y%m%d_%H%M%S")
        return timestamp

    def download_latest_image(channel, resolution, download_path):
        """
        Downloads the latest solar image from the Solar Dynamics Observatory (SDO) for a specified channel and resolution.
        Images are updated per 15 minutes.

        Args:
            channel (str): The SDO channel identifier. Possible values are '0094', '0131', '0171', '0193', '0211', '0304', '0335',
                        '1600', '1700', 'HMIB', 'HMII', 'HMID', 'HMIBC', 'HMIIF', 'HMIIC'.
            resolution (str): The resolution of the image. Possible values are '4096', '2048', '1024', '512'.
            download_path (str): The local directory path where the image will be downloaded.

        Returns:
            tuple: A tuple containing the filename of the downloaded image and the timestamp of the image capture.

        Example:
            filename, timestamp = download_latest('0193', '4096', '/path/to/download')
        """
        # Construct URLs for the latest image and its corresponding timestamp
        sdo_url = "https://sdo.gsfc.nasa.gov"
        latest_path = "/assets/img/latest/"
        latest_file = f"latest_{resolution}_{channel}.jpg"
        latest_times = f"times{channel}.txt"
        imageurl = f"{sdo_url}/{latest_path}{latest_file}"
        timesurl = f"{sdo_url}/{latest_path}{latest_times}"

        timestamp = AIA.download_latest_time(channel)
        timestring = timestamp.strftime("%Y%m%d_%H%M%S")

        # Download the image and save it locally
        filename = os.path.join(download_path, f"{timestring}_{os.path.basename(imageurl)}")
        filename = filename.replace('latest_','')
        if(not os.path.isfile(f"{filename}")):
            print(f"Download: {file} => {filename}")
            try:
                response = requests.get(imageurl)
                response.raise_for_status()  # Raise an HTTPError for bad responses
                with open(filename, 'wb') as file:
                    file.write(response.content)
            except requests.exceptions.RequestException as e:
                print(f"Error {file} => {filename} ({e})")
        else:
            print(f"Exists: {file} => {filename}")
        return filename, timestamp

    def download_latest_video(channel, resolution, download_path):
        """
        Downloads the latest solar video from the Solar Dynamics Observatory (SDO) for a specified channel and resolution.

        Args:
            channel (str): The SDO channel identifier. Possible values are '0094', '0131', '0171', '0193', '0211', '0304', '0335',
                        '1600', '1700', 'HMIB', 'HMII', 'HMID', 'HMIBC', 'HMIIF', 'HMIIC'.
            resolution (str): The resolution of the image. Possible values are '4096', '2048', '1024', '512'.
            download_path (str): The local directory path where the image will be downloaded.

        Returns:
            tuple: A tuple containing the filename of the downloaded image and the timestamp of the image capture.

        Example:
            filename, timestamp = download_latest('0193', '4096', '/path/to/download')
        """
        # Construct URLs for the latest image and its corresponding timestamp
        sdo_url = "https://sdo.gsfc.nasa.gov"
        latest_path = "/assets/img/latest/mpeg/"
        latest_file = f"latest_{resolution}_{channel}.mp4"
        latest_times = f"times{channel}.txt"
        imageurl = f"{sdo_url}/{latest_path}{latest_file}"

        # use current time is times file download failed
        timestamp = datetime.now()
        timestring = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Download the image and save it locally
        filename = os.path.join(download_path, f"{timestring}-{os.path.basename(imageurl)}")
        try:
            response = requests.get(imageurl)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            with open(filename, 'wb') as file:
                file.write(response.content)
            print(f"Downloaded successfully to: {filename}")
        except requests.exceptions.RequestException as e:
            print(f"Error downloading file: {e}")

        return filename, timestamp

if __name__ == "__main__":

    channel = "0193"
    resolution = "512"
    download_path = "./data/"

    #print(AIA.download_latest_time(channel))
    #download_images(start_date, end_date, channel, resolution, download_path)
    #download_latest_image(channel,resolution,download_path)
    #download_latest_video(channel,resolution,download_path)
    AIA.download_range(datetime.now()-timedelta(hours=2), datetime.now(), channel, resolution, download_path)
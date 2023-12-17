import os
import datetime
import requests
import os.path
import datetime
import requests
import re

class AIA:
    def download_latest_time(self, channel):
        """
        Download the latest timestamp from the Solar Dynamics Observatory (SDO) for a specified channel.

        Args:
            channel (str): The SDO channel identifier. Possible values are '0094', '0131', '0171', '0193', '0211', '0304', '0335',
                        '1600', '1700', 'HMIB', 'HMII', 'HMID', 'HMIBC', 'HMIIF', 'HMIIC'.

        Returns:
            datetime.datetime: The timestamp of the latest image capture.

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
            timestring = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Convert timestamp string to a datetime object
        timestamp = datetime.datetime.strptime(timestring, "%Y%m%d_%H%M%S")
        return timestamp

    def download_latest_image(self, channel, resolution, download_path):
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

        timestamp = self.download_latest_time(channel)
        timestring = timestamp.strftime("%Y%m%d_%H%M%S")

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

    def download_latest_video(self, channel, resolution, download_path):
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
        timestamp = datetime.datetime.now()
        timestring = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

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

    print(AIA.download_latest_time(channel))
    #download_images(start_date, end_date, channel, resolution, download_path)
    #download_latest_image(channel,resolution,download_path)
    #download_latest_video(channel,resolution,download_path)

# Introduction
This script was built to utilize the Google Cloud Vision API, to compare expected to display toll rates. This is done by using the text and object recognition features of the API. The script was built to analyze the results of the SR 520 bridge, but could be modified to analyze the rates for any system, or systems. Results are recorded in a log file that uses the naming scheme `yyyymmdd_hhmmss_vision_process.log`. 

# Installation
Running the script requires installing the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install). It also requires access to the Google Cloud [Vision API](https://cloud.google.com/docs/authentication/getting-started#windows). The easiest way to enable access is to create a project, access account, and download the JSON key. 

# Execution
The traffic cameras need to be centered on the toll signs, otherwise it will not be possible to recognize the rate text. Different cameras can be used, but the urls need to be modified. This modification can be done by change the following lines of code:

```
# default configuration
urls['east'][0] = 'https://images.wsdot.wa.gov/nw/520vc00414.jpg'
urls['west'][0] = 'https://images.wsdot.wa.gov/nw/520vc00430.jpg'

# new configuration
urls['east'][0] = 'new_east_camera_url'
urls['west'][0] = 'new_west_camera_url'
```

The end date of the script and interval can also be modified. 

```
end_time = datetime.datetime(end_year, end_month, end_day)
image_download_interval_secs = [analysis_interval]
```

Running the script. It is important to import the environment variable for the Google cloud API key before running the script, otherwise an exception is raised. 

```
python check_web_images.py
```


# Pricing
The pricing for the API calls is reasonable. The first 1k requests are free, the next 1k-5M requests are $1.50/1,000 requests. If requests are made every 5 minutes for a week, this amounts to around $3.00 for a little over 2,000 requests. 
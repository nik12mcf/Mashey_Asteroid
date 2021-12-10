# Mashey Asteroid Hunter

Python (3.6) Data pipeline for NeoWs (Near Earth Object Web Service), which is a system that tracks asteroids and their approaches to Earth.

## Installation

Use Python Poetry for virtual environment and dependency management:

curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -

Once poetry is installed, run "poetry install" in the terminal in the same directory as the pyproject.toml file.

Packages Used:

- requests
- json
- threading
- datetime
- calendar
- vcr
- os
- pytest

## Usage

For testing, install pytest and run "pytest test_mashey.py". Make sure to have a testing_data folder in the same directory so that the scraped data can be saved locally.

Simply call asteroid_closest_approach and nearest_misses to retrieve JSON data. 

nearest_misses function returns JSON data that includes the 10 nearest misses, historical or expected, of asteroids impacting Earth. Asteroid data is returned with all time nearest miss in close_approach_data, but excludes any additional close_approach_data (relative to Earth).

asteroid_closest_approach function returns JSON data that includes each asteroid and its all time closest approach (relative to Earth) in the close approach data.

## Warnings

If running test cases, some files that are created during function calls may require lots of disk space. Scraped data for asteroid_closest_approach and nearest_misses functions are stored locally to avoid re-calling both functions. This helped with developing test cases by avoiding these calls after an initial run.

## Notes and Further Considerations
Multithreading can be used to speed up the process for sending requests to the NASA api. This was implemented at first but after reaching the api limit and recieving HTTP Error 429, I decided for sequential execution and vcr casettes to record requests.

To resolve the HTTP Error 429 a proxy server can be used wherein a bad request triggers the rotation to another ip address. I have had this error before in my data scraping programs and I utilized chromedriver and configured json files to accept premium proxies that require authentification. An example of this authentification is provided below which I have coded and used for my own benefit in other projects. This is just for consideration.
```python
"""
    Set up proxy authentication to generate a special file and upload it to chromedriver dynamically 
    using the following code below. This code configures selenium with chromedriver to use HTTP proxy 
    that requires authentication with user/password pair.
"""
def setup_chromedriver_proxy_auth(PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS):
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """

    background_js = """
    var config = {
            mode: "fixed_servers",
            rules: {
            singleProxy: {
                scheme: "http",
                host: "%s",
                port: parseInt(%s)
            },
            bypassList: ["localhost"]
            }
        };

    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%s",
                password: "%s"
            }
        };
    }

    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
    );
    """ % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)

    return [manifest_json, background_js]
    
"""
This function sets up selenium to use chrome for web scraping, currently chrome driver is one of the
fastest drivers for webscraping but it does not allow for extensions while in headless mode. Therefore,
if planning to use multithreading be aware that there is a hardware limit due to non-headless mode. Chrome
driver in its current state, for this specific project, should only be used for headless mode without
extensions (no proxies that include auths) and in non-headless mode.
"""
def init_chromedriver_driver(proxy_auth, use_proxy=False, user_agent=None):
    path = os.path.dirname(os.path.abspath(__file__))
    chrome_options = webdriver.ChromeOptions()

    if use_proxy:
        pluginfile = 'proxy_auth_plugin.zip'

        with zipfile.ZipFile(pluginfile, 'w') as zp:
            zp.writestr("manifest.json", proxy_auth[0])
            zp.writestr("background.js", proxy_auth[1])
        chrome_options.add_extension(pluginfile)
    if user_agent:
        chrome_options.add_argument('--user-agent=%s' % user_agent)
    driver = webdriver.Chrome(
        os.path.join(path, 'chromedriver'),
        chrome_options=chrome_options)
    return driver
```

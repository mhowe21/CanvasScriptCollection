# imports and install
import json
import multiprocessing
import itertools
import subprocess
import sys
import tempfile
try:
    import requests
except ModuleNotFoundError:
    print("attempting to install requests")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
try:
    import pandas
except ModuleNotFoundError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas"])
# import local modules


class inputAndRun():

    def inputs(self, Token, Domain, Users, **kwargs):
        """Input for running the page view script. 
        Requires a Rest Token An instance Domain, a list of users.
        As optional arguments takes a start date and end date.
        As well as a cpuCount option for multiprocessing."""
        self.Token = Token
        self.domain = Domain
        self.users = Users

        self.startDate = kwargs.get("Start_Date", None)
        self.endDate = kwargs.get("End_Date", None)
        self.cpuCount = kwargs.get("CPU_Count", multiprocessing.cpu_count())

        # remove whitespace from users entry.
        # Then split on commas into a list.
        self.users = self.users.replace(" ", "")
        self.usersList = self.users.split(",")

    def run(self):
        """Given a domain and various arguments
        """
        pool = multiprocessing.Pool()
        # calls(tok,env,sd,ed).pageViewsCSV()
        c = calls(self.Token, self.domain, self.startDate, self.endDate)

        # multiprocess users
        print("Running...")
        try:
            pool.map(c.pageViewsCSV, self.usersList)
            pool.join()
            pool.close()
        # catch possible errors at the end of a sequence 
        # close the multithreaded tabs.
        except:
            pool.close()
            print("Done")


class calls():
    def __init__(self, canvasToken, instance, startTime=None, endTime=None):
        self.canvasToken = canvasToken
        self.instance = instance
        self.JSONData = {}
        self.startTime = startTime
        self.endTime = endTime

    def pageViewsCSV(self, userID):
        """Get JSON object for users page views."""

        includeHeader = True
        burnFile = tempfile.TemporaryFile("a+")
        url = f"https://{self.instance}/api/v1/users/{userID}/page_views"
        payload = {"per_page": "100",
                   "start_time": self.startTime, "end_time": self.endTime}
        headers = {"Authorization": f"Bearer {self.canvasToken}"}

        while(url != None):
            response = requests.request(
                "GET", url, headers=headers, data=payload)
            burnFile = response.text.encode("utf8")
            dataframe = pandas.read_json(burnFile)
            dataframe.to_csv(f"user_{userID}_pageview.csv", mode="a",
                             header=includeHeader, index=False, encoding="utf8")
            # turn off headers after the first set of canvas data is returned and written
            includeHeader = False

            try:
                linkHeaders = response.links["next"]["url"]
                url = linkHeaders
            except KeyError:
                url = None

        return None

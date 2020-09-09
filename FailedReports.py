import json
# attempt to install requests if not found attempt to install it via pip
try:
    import requests
except ModuleNotFoundError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])


class inputAndRun():
    def __init__(self, token, domain, allAccounts):
        self.token = token
        self.domain = domain
        self.allAccounts = False
        self.API = apiData(self.token, self.domain)

    def run(self):
        if self.allAccounts is True:
            accountList = self.API.mapAccounts()
            for account in accountList:
                self.API.getReportsJson
                iCanvasAPI.getReportsJson(accountNumber)
                if(len(CanvasAPI.failedReports()) > 0):
                    print(
                        f"the following reports failed {CanvasAPI.failedReports()} for account {accountNumber}")
                if(len(CanvasAPI.runningReports()) > 0):
                    print(
                        f"the following reports are still running {CanvasAPI.runningReports()} for account {accountNumber}")
            print("done!")
        elif allAccounts is False:
            print("running...")
            self.API.getReportsJson()
            if(len(self.API.failedReports()) > 0):
                print(
                    f"the following reports {self.API.failedReports()} gave an error in the root account")
            if(len(self.API.runningReports()) > 0):
                print(
                    f"the following reports {self.API.runningReports()} are still running in the root account")
            print("done")


class apiData():
    def __init__(self, token, domain):
        self.token = token
        self.domain = domain
        self.jData = {}

    def getReportsJson(self, account="self"):
        """Run an API call to get a list of reports in canvas for that account level."""
        url = f"https://{self.domain}/api/v1/accounts/{account}/reports"

        payload = {'per_page': '100'}
        files = [

        ]
        headers = {'Authorization': f'Bearer {self.token}',
                   }

        response = requests.request(
            "GET", url, headers=headers, data=payload, files=files)
        self.jData = response.json()

        return self.jData

    def failedReports(self):
        """Return a list of reports that failed.
        Takes the jsonObject created when getReportsJson is called."""
        failedItems = []
        for item in self.jData:
            try:
                if(item["last_run"]["status"] == "error" or item["last_run"]["status"] == "failed"):
                    failedItems.append(item["report"])

            # we might not have a field for a never run report so we will skip over it.
            except TypeError:
                continue

        return(failedItems)

    def runningReports(self):
        """Return a list of reports that were currently still running when the program was executed.
        Takes the jsonObject created when getReportsJson is called"""
        runningItems = []
        for item in self.jData:
            try:
                if(item["last_run"]["status"] == "running"):
                    runningItems.append(item["last_run"]["report"])
            except TypeError:
                continue

        return(runningItems)

    def mapAccounts(self):
        """Return a list of all account IDs in an instance"""
        accountsList = []
        # add the root account to the list
        accountsList.append("self")

        url = f"https://{self.domain}/api/v1/accounts/self/sub_accounts"

        payload = {'per_page': '100',
                   'recursive': 'true'}
        files = []
        headers = {
            'Authorization': f'Bearer {self.token}',
        }

        while(url is not None):
            response = requests.request(
                "GET", url, headers=headers, data=payload, files=files)
            accountJData = response.json()

            for items in accountJData:
                accountsList.append(items["id"])
            # in the event the account has more then 100 sub accounts continue to gather sub account IDs
            try:
                rLinks = response.links["next"]["url"]
                url = rLinks
            except KeyError:
                url = None

        return accountsList

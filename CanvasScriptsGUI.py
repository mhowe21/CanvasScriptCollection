from tkinter import *
from tkinter import ttk
import os
import subprocess
try:
    from cryptography.fernet import Fernet
except ModuleNotFoundError:
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "cryptography"])
    from cryptography.fernet import Fernet
# import scripts
import FailedReports
import PageViews


class Cipher():
    def __init__(self):
        self.token = None

    def generate_key(self):
        """
        Generates a new encryption key and saves it to the working directory.
        """
        key = Fernet.generate_key()
        with open("secret.key", "wb") as key_file:
            key_file.write(key)

    def load_key(self):
        """
        Loads the secret key from a file in the current working directory.
        """
        return open("secret.key", "rb").read()

    def encryptFile(self, filename, key, data):
        """
        Given a filename path and a key it encrpys and writes to the file.
        """
        f = Fernet(key)
        with open(filename, "wb") as file:
            data = data.encode()
            encrypted_data = f.encrypt(data)
            file.write(encrypted_data)

    def decrypt(self, filename, key):
        """
        Given a filename string path and a key decrypt the file.
        """
        f = Fernet(key)
        with open(filename, "rb") as file:
            # read the encrypted data
            encrypted_data = file.read()
            decrypted_data = f.decrypt(encrypted_data)
        return decrypted_data


class MainGUI():
    def __init__(self):
        self.root = Tk()
        self.entryField = None
        self.crypter = Cipher()

    def _confirmTokenEntry(self):
        token = self.entryField.get()
        if(os.path.isfile("secret.key") is False):
            self.crypter.generate_key()
            key = self.crypter.load_key()
            self.crypter.encryptFile("tokenFile.env", key, token)
            # Next block testing only remove after confirmation.
            # decryptedToken = (self.crypter.decrypt
            # ("tokenFile.env", key).decode("utf-8"))
            # print(decryptedToken)

        else:
            key = self.crypter.load_key()
            self.crypter.encryptFile("tokenFile.env", key, token)

    def _tokenMenu(self):
        gettoken = Toplevel(self.root)
        addTokenLabel = ttk.Label(gettoken, text="Enter Canvas REST Token")
        addTokenLabel.pack()
        self.entryField = Entry(gettoken, show="*")
        self.entryField.pack()
        enterTokenButton = ttk.Button(
            gettoken, text="Enter Token", command=lambda:
            [self._confirmTokenEntry(), gettoken.destroy()])
        enterTokenButton.pack(side="left")
        cancelButton = ttk.Button(
            gettoken, text="Cancel", command=gettoken.destroy)
        cancelButton.pack(side="right")

    # GUI options on select
    def _listSelect(self, event=None):
        """Select an item from the list
        Then show its options"""
        selection = self.scriptList.curselection()
        selection = selection[0]
        # print(selection)
        if selection == 0:
            self.pageViewsOptions()
        elif selection == 1:
            self.failedReportsOptions()

    def pageViewsOptions(self):
        # reset selection
        self.optionsFrame.destroy()
        self.GUI_options()

        domainEntryLabel = ttk.Label(
            self.optionsFrame, text="""Enter Instance domain
            (e.g canvas.instructure.com)""")
        self.domainEntry = Entry(self.optionsFrame)
        userIDEntryLablel = ttk.Label(
            self.optionsFrame, text="Enter list of users seperated by comma")
        self.userIDEntry = Entry(self.optionsFrame)
        startDateEntryLabel = ttk.Label(self.optionsFrame,
                                        text="""Enter Start Date format yyyy-mm-dd
        Leave blank for all""")
        self.startDateEntry = Entry(self.optionsFrame)
        endDateEntryLabel = ttk.Label(self.optionsFrame,
                                      text="""Enter End Date format yyyy-mm-dd
        Leave blank for all""")
        self.endDateEntry = Entry(self.optionsFrame)

        key = self.crypter.load_key()
        tokenString = self.crypter.decrypt("tokenFile.env", key).decode()

        PV = PageViews.inputAndRun()
        runButton = ttk.Button(self.optionsFrame, text="Run", command=lambda:
                               [PV.inputs(tokenString, self.domainEntry.get
                                          (
                                          ), self.userIDEntry.get(), Start_Date=self.startDateEntry.get(), End_Date=self.endDateEntry.get()), PV.run()])

        domainEntryLabel.grid()
        self.domainEntry.grid()
        userIDEntryLablel.grid()
        self.userIDEntry.grid()
        startDateEntryLabel.grid()
        self.startDateEntry.grid()
        endDateEntryLabel.grid()
        self.endDateEntry.grid()
        runButton.grid()

        self.root.update()

    def failedReportsOptions(self):
        self.optionsFrame.destroy()
        self.GUI_options()
        self.SelectedOption = StringVar()

        domainEntryLabel = ttk.Label(self.optionsFrame, text="""Enter Instance Domain
        e.g canvas.instructure.com)""")
        domainEntry = self.domainEntry = Entry(self.optionsFrame)

        RadiobuttonLabel = ttk.Label(
            self.optionsFrame, text="""Scan All sub accounts.""")
        R1 = ttk.Radiobutton(self.optionsFrame, text="Yes",
                             value=True, var=self.SelectedOption)
        R2 = ttk.Radiobutton(self.optionsFrame, text="No",
                             value=False, var=self.SelectedOption)

        key = self.crypter.load_key()
        tokenString = self.crypter.decrypt("tokenFile.env", key).decode()
        runButton = ttk.Button(self.optionsFrame, text="Run", command=lambda: FailedReports.inputAndRun(
            tokenString, domainEntry.get(), self.SelectedOption))

        domainEntryLabel.grid()
        domainEntry.grid()
        RadiobuttonLabel.grid()
        R1.grid()
        R2.grid()
        runButton.grid()

    def GUI_Menu(self):
        menubar = Menu(self.root)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Set Token", command=self._tokenMenu)

        filemenu.add_separator()

        filemenu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        self.root.config(menu=menubar)

        # left hand script list and select
        listFrame = Frame(self.root)
        listFrame.grid(row=1, column=0, rowspan=2,
                       stick="nsew", padx=10, pady=10)
        ttk.Label(listFrame, text="Scripts", background="gray").grid(
            row=0, column=0, stick="nsew")
        self.scriptList = Listbox(listFrame, selectmode="SINGLE", height=30)
        self.scriptList.insert(1, "Page Views")
        self.scriptList.insert(2, "Failed Reports")
        self.scriptList.insert(3, "Hawkspan")
        # bind the button
        self.scriptList.bind('<Double-1>', self._listSelect)
        self.scriptList.grid(row=1, column=0)

        # right center options for selected script

    def GUI_options(self):
        self.optionsFrame = Frame(self.root)
        self.optionsFrame.grid(row=1, column=1, stick="nsew", padx=10, pady=10)
        ttk.Label(self.optionsFrame, text="Options", background="lightblue").grid(
            row=0, column=0, stick="nsew")

    # output
    def GUI_output(self):
        outputFrame = Frame(self.root)
        outputFrame.grid(row=2, column=1, stick="nsew", padx=10, pady=10)
        ttk.Label(outputFrame, text="output", background="lightgreen").grid(
            row=0, column=0, stick="nsew")
        outputTextBox = Text(outputFrame, state=NORMAL,
                             height=20).grid(row=1, column=0)

    def RUN_GUI(self):
        self.root.mainloop()

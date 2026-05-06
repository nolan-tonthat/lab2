# Summary: This module contains the user interface and logic for a graphical user interface version of the stock manager program.

from datetime import datetime
from os import path
from tkinter import *
from tkinter import ttk
from tkinter import messagebox, simpledialog, filedialog
import csv
import stock_data
from stock_class import Stock, DailyData
from utilities import clear_screen, display_stock_chart, sortStocks, sortDailyData

class StockApp:
    def __init__(self):
        self.stock_list = []
        #check for database, create if not exists
        if path.exists("stocks.db") == False:
            stock_data.create_database()

 # This section creates the user interface

        # Create Window
        self.root = Tk()
        self.root.title("Stock Manager")
        self.root.geometry("700x550")

        # Add Menubar
        self.menubar = Menu(self.root)

        # Add File Menu
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Save Data", command=self.save)
        self.filemenu.add_command(label="Load Data", command=self.load)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit",      command=self.root.quit)
        self.menubar.add_cascade(label="File", menu=self.filemenu)

        # Add Web Menu 
        self.webmenu = Menu(self.menubar, tearoff=0)
        self.webmenu.add_command(
            label="Scrape Data from Yahoo! Finance...",
            command=self.scrape_web_data)
        self.webmenu.add_command(
            label="Import CSV from Yahoo! Finance...",
            command=self.importCSV_web_data)
        self.menubar.add_cascade(label="Web", menu=self.webmenu)

        # Add Chart Menu
        self.chartmenu = Menu(self.menubar, tearoff=0)
        self.chartmenu.add_command(label="Show Chart", command=self.display_chart)
        self.menubar.add_cascade(label="Chart", menu=self.chartmenu)
 
        self.root.config(menu=self.menubar)

        # Add menus to window       


        # Add heading information
        self.headingLabel = Label(self.root, text="No Stock Selected",
                                  font=("Arial", 14, "bold"))
        self.headingLabel.pack(pady=5)
        
        #frame
        mainFrame = Frame(self.root)
        mainFrame.pack(fill=BOTH, expand=True, padx=5, pady=5)
        # Add stock list
        listFrame = Frame(mainFrame)
        listFrame.pack(side=LEFT, fill=Y, padx=(0, 5))
        Label(listFrame, text="Stocks").pack()
        self.stockList = Listbox(listFrame, width=12, exportselection=False)
        self.stockList.pack(fill=Y, expand=True)
        self.stockList.bind("<<ListboxSelect>>", self.update_data)
        

        #notebook
        self.notebook = ttk.Notebook(mainFrame)
        self.notebook.pack(fill=BOTH, expand=True)
        
        # Add Tabs
        manageTab = Frame(self.notebook)
        self.notebook.add(manageTab, text="Manage")
 
        addFrame = LabelFrame(manageTab, text="Add Stock")
        addFrame.pack(fill=X, padx=5, pady=5)
        Label(addFrame, text="Symbol:").grid(row=0, column=0, sticky=W, padx=3, pady=2)
        self.addSymbolEntry = Entry(addFrame, width=10)
        self.addSymbolEntry.grid(row=0, column=1, sticky=W, padx=3, pady=2)
        Label(addFrame, text="Name:").grid(row=1, column=0, sticky=W, padx=3, pady=2)
        self.addNameEntry = Entry(addFrame, width=25)
        self.addNameEntry.grid(row=1, column=1, sticky=W, padx=3, pady=2)
        Label(addFrame, text="Shares:").grid(row=2, column=0, sticky=W, padx=3, pady=2)
        self.addSharesEntry = Entry(addFrame, width=10)
        self.addSharesEntry.grid(row=2, column=1, sticky=W, padx=3, pady=2)
        Button(addFrame, text="Add Stock", command=self.add_stock).grid(
            row=3, column=0, columnspan=2, pady=4)
 
        sharesFrame = LabelFrame(manageTab, text="Update Shares")
        sharesFrame.pack(fill=X, padx=5, pady=5)
        Label(sharesFrame, text="Shares:").grid(row=0, column=0, sticky=W, padx=3, pady=2)
        self.updateSharesEntry = Entry(sharesFrame, width=10)
        self.updateSharesEntry.grid(row=0, column=1, sticky=W, padx=3, pady=2)
        Button(sharesFrame, text="Buy",  command=self.buy_shares).grid(row=1, column=0, padx=3, pady=4)
        Button(sharesFrame, text="Sell", command=self.sell_shares).grid(row=1, column=1, padx=3, pady=4)
 
        deleteFrame = LabelFrame(manageTab, text="Delete Stock")
        deleteFrame.pack(fill=X, padx=5, pady=5)
        Button(deleteFrame, text="Delete Selected Stock", command=self.delete_stock).pack(pady=4)
        

        # Set Up Main Tab


        # Setup History Tab
        historyTab = Frame(self.notebook)
        self.notebook.add(historyTab, text="History")
        self.dailyDataList = Text(historyTab, wrap=NONE)
        histScroll = Scrollbar(historyTab, command=self.dailyDataList.yview)
        self.dailyDataList.configure(yscrollcommand=histScroll.set)
        histScroll.pack(side=RIGHT, fill=Y)
        self.dailyDataList.pack(fill=BOTH, expand=True)
        
        
        # Setup Report Tab
        reportTab = Frame(self.notebook)
        self.notebook.add(reportTab, text="Report")
        self.stockReport = Text(reportTab, wrap=NONE)
        repScroll = Scrollbar(reportTab, command=self.stockReport.yview)
        self.stockReport.configure(yscrollcommand=repScroll.set)
        repScroll.pack(side=RIGHT, fill=Y)
        self.stockReport.pack(fill=BOTH, expand=True)

        ## Call MainLoop
        self.root.mainloop()

# This section provides the functionality
       
    # Load stocks and history from database.
    def load(self):
        self.stockList.delete(0,END)
        stock_data.load_stock_data(self.stock_list)
        sortStocks(self.stock_list)
        for stock in self.stock_list:
            self.stockList.insert(END,stock.symbol)
        messagebox.showinfo("Load Data","Data Loaded")

    # Save stocks and history to database.
    def save(self):
        stock_data.save_stock_data(self.stock_list)
        messagebox.showinfo("Save Data","Data Saved")

    # Refresh history and report tabs
    def update_data(self, evt):
        if self.stockList.curselection():
            self.display_stock_data()

    # Display stock price and volume history.
    def display_stock_data(self):
        symbol = self.stockList.get(self.stockList.curselection())
        for stock in self.stock_list:
            if stock.symbol == symbol:
                self.headingLabel['text'] = stock.name + " - " + str(stock.shares) + " Shares"
                self.dailyDataList.delete("1.0",END)
                self.stockReport.delete("1.0",END)
                self.dailyDataList.insert(END,"- Date -   - Price -   - Volume -\n")
                self.dailyDataList.insert(END,"=================================\n")
                for daily_data in stock.DataList:
                    row = daily_data.date.strftime("%m/%d/%y") + "   " +  '${:0,.2f}'.format(daily_data.close) + "   " + str(daily_data.volume) + "\n"
                    self.dailyDataList.insert(END,row)

                #display report
                self.stockReport.insert(END, "Report for: " + stock.symbol + " " + stock.name + "\n")
                self.stockReport.insert(END, "Shares: " + str(stock.shares) + "\n")
                self.stockReport.insert(END, "=" * 45 + "\n")
                if len(stock.DataList) == 0:
                    self.stockReport.insert(END, "*** No daily history.\n")
                else:
                    prices   = [d.close for d in stock.DataList]
                    earliest = stock.DataList[0].close
                    latest   = stock.DataList[-1].close
                    gain_loss = (latest - earliest) * stock.shares
                    self.stockReport.insert(END, "Earliest Price : " + '${:0,.2f}'.format(earliest) + "\n")
                    self.stockReport.insert(END, "Latest Price   : " + '${:0,.2f}'.format(latest) + "\n")
                    self.stockReport.insert(END, "Min Price      : " + '${:0,.2f}'.format(min(prices)) + "\n")
                    self.stockReport.insert(END, "Max Price      : " + '${:0,.2f}'.format(max(prices)) + "\n")
                    self.stockReport.insert(END, "Gain / Loss    : " + '${:0,.2f}'.format(gain_loss) + "\n")

                    

    
    # Add new stock to track.
    def add_stock(self):
        new_stock = Stock(self.addSymbolEntry.get(),self.addNameEntry.get(),float(str(self.addSharesEntry.get())))
        self.stock_list.append(new_stock)
        self.stockList.insert(END,self.addSymbolEntry.get())
        self.addSymbolEntry.delete(0,END)
        self.addNameEntry.delete(0,END)
        self.addSharesEntry.delete(0,END)

    # Buy shares of stock.
    def buy_shares(self):
        symbol = self.stockList.get(self.stockList.curselection())
        for stock in self.stock_list:
            if stock.symbol == symbol:
                stock.buy(float(self.updateSharesEntry.get()))
                self.headingLabel['text'] = stock.name + " - " + str(stock.shares) + " Shares"
        messagebox.showinfo("Buy Shares","Shares Purchased")
        self.updateSharesEntry.delete(0,END)

    # Sell shares of stock.
    def sell_shares(self):
        symbol = self.stockList.get(self.stockList.curselection())
        for stock in self.stock_list:
            if stock.symbol == symbol:
                stock.sell(float(self.updateSharesEntry.get()))
                self.headingLabel['text'] = stock.name + " - " + str(stock.shares) + " Shares"
        messagebox.showinfo("Sell Shares","Shares Sold")
        self.updateSharesEntry.delete(0,END)

    # Remove stock and all history from being tracked.
    def delete_stock(self):
       symbol = self.stockList.get(self.stockList.curselection())
       self.stock_list[:] = [s for s in self.stock_list if s.symbol != symbol]
       self.stockList.delete(0, END)
       for s in self.stock_list:
           self.stockList.insert(END, s.symbol)
       self.headingLabel['text'] = "No Stock Selected"
       self.dailyDataList.delete("1.0", END)
       self.stockReport.delete("1.0", END)

    # Get data from web scraping.
    def scrape_web_data(self):
        dateFrom = simpledialog.askstring("Starting Date","Enter Starting Date (m/d/yy)")
        dateTo = simpledialog.askstring("Ending Date","Enter Ending Date (m/d/yy")
        try:
            stock_data.retrieve_stock_web(dateFrom,dateTo,self.stock_list)
        except:
            messagebox.showerror("Cannot Get Data from Web","Check Path for Chrome Driver")
            return
        self.display_stock_data()
        messagebox.showinfo("Get Data From Web","Data Retrieved")

    # Import CSV stock history file.
    def importCSV_web_data(self):
        symbol = self.stockList.get(self.stockList.curselection())
        filename = filedialog.askopenfilename(title="Select " + symbol + " File to Import",filetypes=[('Yahoo Finance! CSV','*.csv')])
        if filename != "":
            stock_data.import_stock_web_csv(self.stock_list,symbol,filename)
            self.display_stock_data()
            messagebox.showinfo("Import Complete",symbol + "Import Complete")   
    
    # Display stock price chart.
    def display_chart(self):
        symbol = self.stockList.get(self.stockList.curselection())
        display_stock_chart(self.stock_list,symbol)


def main():
        app = StockApp()
        

if __name__ == "__main__":
    # execute only if run as a script
    main()
#can now analyze with 3 different regressions
#get predictions and overlays of data
#TODO next version:> Error Handling, Widgets writing on top of each other, adding more analyses, and polishing

import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.neighbors import KNeighborsRegressor
import numpy as np
import csv
import random
import xlrd
import xlsxwriter
import math

root = tk.Tk()

def dist(x,y):#dist from zero
    return math.sqrt((x)**2 + (y)**2)

class AnalysisGUI:
    def __init__(self, master):
        #basic setup and initial display
        self.master = master
        master.title("Generalysis: Data Analysis Tool")
        master.geometry("850x800")
        #data
        self.data = []
        #gridded labels
        tk.Label(master, text= "File Location").grid(row=1)
        tk.Label(master, text= "X Attribute").grid(row=2)
        tk.Label(master, text= "Y Attribute").grid(row=3)
        tk.Label(master, text= "Analysis Overlay").grid(row=6)
        #ungridded labels
        self.attr_label = tk.Label(master, text= "Attributes:>")
        #self.attr_label.grid(row=5)
        #entries
        self.loc_entry = tk.Entry(master)
        self.loc_entry.grid(row=1, column = 1)
        self.col1_entry = tk.Entry(master)
        self.col1_entry.grid(row=2, column = 1)
        self.col2_entry = tk.Entry(master)
        self.col2_entry.grid(row=3, column = 1)
        #drop down menu
        self.analysis_option_list = ('Linear Regression', '2nd Deg Polynomial Regression', '3rd Deg Polynomial Regression')
        self.analysis_variable = tk.StringVar()
        self.analysis_variable.set(self.analysis_option_list[0])
        self.analysis_option_menu = tk.OptionMenu(master, self.analysis_variable, *self.analysis_option_list)
        self.analysis_option_menu.grid(row=6, column=1)
        #enter data button
        enter_button = tk.Button(master, text="Enter", command = self.first_process).grid(row=7, column=1)
        #matplotlib plot init
        self.figure = plt.Figure(figsize=(5,5), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, self.master)
        #clear graph button:
        self.clear_graph_button = tk.Button(master, text='Clear Overlays', command = self.ax.clear)

    def first_process(self):
        #get the data that the user specifies
        f_raw = self.loc_entry.get()
        x_col = self.col1_entry.get()
        y_col = self.col2_entry.get()
        self.x, self.y, cats = self.fetchData(f_raw, x_entry=x_col, y_entry= y_col)
        #plot/scatter
        self.graphData(self.x, self.y)
        self.graphAnalysis(self.x, self.y, self.analysis_variable.get())    
        #show graph
        self.canvas.get_tk_widget().grid(row=9, column=0)
        self.canvas.draw()
        #prediction values
        tk.Label(self.master, text='Values to Predict').grid(row = 9, column=1)
        self.prediction_values_entry = tk.Entry(self.master)
        self.prediction_values_entry.grid(row=9, column = 2)
        predict_button = tk.Button(text='Predict Values', command= self.second_process)
        predict_button.grid(row=10, column = 2)
        #show clear button
        self.clear_graph_button.grid(row=8, column=1)

    def fetchData(self, file_entry_raw, x_entry=1, y_entry=1, single = False):
        #get usable file loc
        splt = file_entry_raw.split('\\')
        filetype = splt[-1].split('.')
        filetype = filetype[1] 
        location = '//'.join(splt)

        all_data = []
        #get all data
        if filetype == 'txt':
            loc = open(location).read()
            raw = loc.split('\n')
            for i in range(len(raw)):
                all_data.append(raw[i].split(', '))
            #remove empty lists
            all_data = [dp for dp in all_data if dp != ['']]
        elif filetype == 'xlsx' or filetype == 'xls':
            wb = xlrd.open_workbook(location)
            sheet = wb.sheet_by_index(0)
            for i in range(sheet.nrows):
                all_data.append(sheet.row_values(i))
        elif filetype == 'csv':
            with open(location) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                for row in csv_reader:
                    all_data.append(row)
                all_data = [dp for dp in all_data if dp != [''] and dp != []]
        print(all_data)
        #get the columns that the user wants
        x = []
        y = []
        if single == False:
            try:
                x_entry = int(x_entry)
                y_entry = int(y_entry)
            except ValueError:
                x_entry = all_data[0].index(x_entry)
                y_entry = all_data[0].index(y_entry)

            for i in range(len(all_data)):
                if i > 0:
                    x.append(float(all_data[i][int(x_entry)]))
                    y.append(float(all_data[i][int(y_entry)]))
            cats = [all_data[0][int(x_entry)], all_data[0][int(y_entry)]]
            self.data = []
            for i in range(len(x)):
                self.data.append([x[i], y[i]])

        elif single == True:
            float_arr = []
            for i in range(len(all_data)):
                for j in range(len(all_data[i])):
                    float_arr.append(float(all_data[i][j]))

            x = float_arr 
            y = 0
            cats = all_data[0]
        return x, y, cats

    def second_process(self):
        #get values to predict
        chc = self.analysis_variable.get()
        pred_vals_raw = self.prediction_values_entry.get()
        if len(pred_vals_raw.split(',')) > 1:
            split_vals = pred_vals_raw.split(',')
            for i in range(len(split_vals)):
                split_vals[i] = float(split_vals[i])
            pred_vals = split_vals
        elif '.xlsx' in pred_vals_raw or '.xls' in pred_vals_raw or '.csv' in pred_vals_raw or '.txt' in pred_vals_raw:
            pred_vals, y, cats = self.fetchData(pred_vals_raw, single=True)
            print(pred_vals)
            print(y)
            print(cats)
        #Get the x and y from the data
        ins = []
        outs = []
        for i in range(len(self.data)):
            for j in range(len(self.data[i])):
                if j == 0:
                    ins.append(self.data[i][j])
                else:
                    outs.append(self.data[i][j])
        preds = self.graphAnalysis(ins, outs, chc, unknowns=pred_vals, predicting=True)
        #Make message look good
        label_var = tk.StringVar()
        label_var.set('Predictions from ' + self.analysis_variable.get() + ' model')
        pred_title = tk.Label(self.master, textvariable= label_var)
        pred_title.grid(row=10, column=0)
        pred_str = ['Unknown' + '\t' + 'Prediction' + '\n']
        for i in range(len(pred_vals)):
            pred_str.append(str(pred_vals[i]) + '\t' + str(preds[i]) + '\n')
        pred_str = ' '.join(pred_str)
        print(pred_str)
        pred_var = tk.StringVar()
        pred_var.set(pred_str)
        self.pred_message = tk.Message(self.master, textvariable=pred_var)
        self.pred_message.grid(row=11, column=0)

    def sort_labeled(self, arr):
        return arr[0]

    def graphAnalysis(self, x, y, choice, unknowns=[], predicting=False):
        #sort the x and y low to high so plots don't look weird
        dists = []
        for i in range(len(x)):
            dists.append([dist(x[i],y[i]), i])
        dists = sorted(dists, key = self.sort_labeled)
        sorted_xs = []
        sorted_ys = []
        for i in range(len(dists)):
            sorted_xs.append(x[dists[i][1]])
            sorted_ys.append(y[dists[i][1]])
        x = sorted_xs
        y = sorted_ys
        #reshape
        x = np.array(x).reshape(-1, 1)
        y = np.array(y).reshape(-1, 1)
        unknowns = np.array(unknowns).reshape(-1, 1)
        print(unknowns)
        predictions = []
        if choice == 'Linear Regression':
            lr = LinearRegression()
            lr.fit(x,y)
            if predicting == True:
                predictions = lr.predict(unknowns)
                print(predictions)
                self.graphData(unknowns, predictions, plotting=True)
            else:
                self.graphData(x, lr.predict(x), plotting=True)
        elif choice == '2nd Deg Polynomial Regression':
            poly_feat = PolynomialFeatures(degree=2)
            x_poly = poly_feat.fit_transform(x)
            lr = LinearRegression()
            lr.fit(x_poly, y)
            if predicting == True:
                x_poly = poly_feat.fit_transform(unknowns)
                predictions = lr.predict(x_poly)
            else:
                self.graphData(x, lr.predict(x_poly), plotting=True)
        elif choice == '3rd Deg Polynomial Regression':
            poly_feat = PolynomialFeatures(degree=3)
            x_poly = poly_feat.fit_transform(x)
            lr = LinearRegression()
            lr.fit(x_poly, y)
            if predicting == True:
                x_poly = poly_feat.fit_transform(unknowns)
                predictions = lr.predict(x_poly)
            else:
                self.graphData(x, lr.predict(x_poly), plotting=True)
        #elif choice == 'KNN':
        #    kn = KNeighborsRegressor()
        #    kn.fit(x, y)
        #    predictions = kn.predict(unknowns)

        return predictions

    def graphData(self, x, y, plotting=False):
        #plot data
        categories = [self.col1_entry.get(), self.col2_entry.get()]
        if plotting == False:
            self.ax.scatter(x,y)
        else:
            self.ax.plot(x,y, color='k')
        self.ax.set_xlabel(categories[0])
        self.ax.set_ylabel(categories[1])

ag = AnalysisGUI(root)
root.mainloop()

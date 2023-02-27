                                                                                                                                                                                              #plan1: use pandas to load the file directly
import pandas
import matplotlib.pyplot as plt
import os
import win32com.client as win32
import pandas as pd
import numpy as np
from pathlib import Path
from pywintypes import com_error
import time


import matplotlib.pyplot as plt
import os

def draw_bar_and_line_chart(df, title, output_folder, df_comp=None):
    '''
    Draw a stacked bar chart and a line chart for comparison
    '''
    
    # find the index location of the maximum value of the second element
    # like 0, 1, 2...
    df["name"] = df.index
    df = df.reset_index(drop=True)
    max_index = df.iloc[:, 1].idxmax()
    max_index_location = df.index.get_loc(max_index)
    temp = df.iloc[max_index_location].copy()
    df.iloc[max_index_location] = df.iloc[-1]
    df.iloc[-1] = temp

    if df_comp is not None:
        df_comp["name"] = df_comp.index
        df_comp = df_comp.reset_index(drop=True)
        temp = df_comp.iloc[max_index_location].copy()
        df_comp.iloc[max_index_location] = df_comp.iloc[-1]
        df_comp.iloc[-1] = temp

    fig, ax1 = plt.subplots()

    ax1.bar(range(len(df.index)), df.iloc[:, 0],  color='green', label = "Finish")
    if df.iloc[-1, 1] > 0:
        ax1.bar(len(df.index)-1, df.iloc[-1, 1], bottom=df.iloc[-1, 0], color='red', label= "Max Gap")
    if df.iloc[:len(df.index)-1, 1].max() > 0:
        ax1.bar(range(len(df.index)-1), df.iloc[:len(df.index)-1, 1],  bottom=df.iloc[:len(df.index)-1, 0], color='yellow', label="Gap")

    # show the label at the right top of the bar, auto adjust the size according to ax1's column's length
    ax1.legend(loc='upper right', bbox_to_anchor=(1, 1), fontsize='small')
    
    # set the x-axis by the "name"
    ax1.set_xticks(range(len(df.index)))
    ax1.set_xticklabels(df["name"])
    
    # Add value labels to the bar chart
    for i in range(len(df)):
        if df.iloc[i, 0] == 0:
            plt.text(i, df.iloc[i, 1]/2, int(df.iloc[i, 1]), ha='center', va='center')
        elif df.iloc[i, 1] == 0:
            plt.text(i, df.iloc[i, 0]/2, int(df.iloc[i, 0]), ha='center', va='center')
        else:
            plt.text(i, df.iloc[i, 0] / 2,  int(df.iloc[i, 0]), ha='center', va='center')
            plt.text(i, (2 * df.iloc[i, 0] + df.iloc[i,1]) / 2,  int(df.iloc[i, 1]), ha='center', va='center')

    # Add a second y-axis (on right) and draw a line chart if df_comp is not None
    if df_comp is not None:
        df_diff= df_comp.iloc[:,1]-df.iloc[:,1]
        df_diff_percent=df_diff.copy()
        # if the element of df_diff is 0, leave this element as 0. Otherwise, calculate the percentage
        for i in range(len(df_diff_percent)):
            if df_diff_percent.iloc[i] != 0:
                df_diff_percent.iloc[i] = df_diff_percent.iloc[i]/df.iloc[i,1]
        df_diff_percent = df_diff_percent*100
        df_diff_percent = df_diff_percent.round(2)
        # set 0 as the center point and draw the line chart of df_diff
        ax2 = ax1.twinx()
        ax2.plot(range(len(df.index)), df_diff_percent.iloc[:], color='blue')
        # set the y-axis as percentage format, % sign
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}%".format(x)))
         # Add value labels to the line chart according to the line location
        for i in range(len(df)):
            plt.text(i, df_diff_percent.iloc[i], str(df_diff_percent.iloc[i])+"%", ha='center', va='bottom')

    # Set the chart title
    plt.title(title)

    # Save the image to the output folder
    plt.savefig(os.path.join(output_folder, title + '.png'))


def extract_gap(input_folder):
    ''' 
    Extract the gap between the last two columns
    for the status of the same file name, it should be counted as a whole
    '''
    status_data = dict()
    file_number = dict()
    files = os.listdir(input_folder)
    for file in files:
        file_name = file.split('.')[0].split('_')[0]
        file_path = os.path.join(input_folder, file)
        # read the sixth sheet (pivot_table) and set the six row as the column name
        df = pandas.read_excel(file_path, sheet_name=5, header=5)
        # check whether there is a column named "None"
        if 'None' not in df.columns:
            df['None'] = 0
            df = df[['None', df.columns[-2]]]
        else:
            df = df[['None', df.columns[-1]]]
        df = df.iloc[-1:]
        # "NN" is sum (last element) minus "None"
        df['NN'] = df[df.columns[-1]] - df['None']
        # drop the the total column
        df = df.drop(df.columns[-2], axis=1)
        # set all the index as 0
        df.index = [0]
        # add the dataframe to the dictionary
        # if the file name is the same, add the dataframe value to the same key
        if file_name in status_data.keys():
            status_data[file_name] = status_data[file_name] + df
            file_number[file_name] += 1

        else:
            status_data[file_name] = df
            file_number[file_name] = 1
    # convert the dictionary to dataframe, the key is the index
    df = pandas.concat(status_data)
    # rename the column name
    df = df.rename(columns={'None': 'Number of gap', 'NN': 'Number of fixed'})
    # exchange the two elements in df 
    df = df[['Number of fixed', 'Number of gap']]
    # set the index by the first element of the index
    df.index = df.index.map(lambda x: x[0])
    # rename the index name by adding the file_number
    df.index = df.index.map(lambda x: (x, file_number[x]))
    return df

def extract_linked_request(input_folder):
    '''
    use win32 read the eighth sheet (pivot_table)
    '''
    # give the absolute path of the files
    linked_request_data = dict()
    file_number = dict()
    files = os.listdir(input_folder)
    for file in files:
        try:
            file_name = file.split('.')[0].split('\\')[-1].split('_')[0]
            file_path = os.path.join(input_folder, file)
            excel = win32.gencache.EnsureDispatch('Excel.Application')
            # excel.Visible = True
            try:
                wb = excel.Workbooks.Open(file_path)
            except com_error as e:
                if e.excepinfo[5] == -2146827284:
                    print(f'Failed to open spreadsheet.  Invalid filename or location: {file_path}')
                    exit()
                else:
                    raise e
            ws = wb.Worksheets(8)
            # select the range of the pivot table
            pvtTable = ws.Range('C3').PivotTable
            page_range_item = []
            for i in pvtTable.PageRange:
                page_range_item.append(str(i))
            # set filter as "Agreed" if filter contains "Agreed"
            # if not, set filter as "None"
            if 'Agreed' in page_range_item:
                pvtTable.PivotFields(page_range_item[0]).CurrentPage = 'Agreed'
            else:
                pvtTable.PivotFields(page_range_item[0]).CurrentPage = 'None'
            data = pvtTable.DataBodyRange.Value
            # extract the first element and the last element of the list
            df = pandas.DataFrame(data[-1][0:]).T
            # just rename the last column as 'Sum' and the first column as 'Number of required link'
            # do not change other column names
            df.rename(columns={df.columns[-1]: 'Sum', df.columns[0]: 'Number of required link'}, inplace=True)
            # and then create another element by last column minus the first column
            df['Number of requirednotlink'] = df['Sum'] - df['Number of required link']
            # keep the first and the last column
            df = df[['Number of required link', 'Number of requirednotlink']]
            if file_name in linked_request_data.keys():
                linked_request_data[file_name] = linked_request_data[file_name] + df
                file_number[file_name] += 1
            else:
                linked_request_data[file_name] = df
                file_number[file_name] = 1
            wb.Close(False)
        except Exception as e:
            excel.Application.Quit()
    excel.Application.Quit()  
    # convert the dict to dataframe, the key is the index
    df = pandas.concat(linked_request_data)
    # set the first column "Number of requiredlink", the second column "Number of requirednotlink"
    # df.columns = ['Number of required link', 'Number of requirednotlink']
    # set the index by the first element of the index
    df.index = df.index.map(lambda x: x[0])
    df.index = df.index.map(lambda x: (x, file_number[x]))
    return df

# auto_draw that contains compared_folder
def auto_draw(input_folder,  output_folder, document_type, compared_folder=None):
    # df_gap = pd.read_excel('output\df_gap.xlsx', index_col=[0, 1])
    # df_link = pd.read_excel('output\df_link.xlsx', index_col=[0, 1])

    df_gap = extract_gap(input_folder)
    df_link = extract_linked_request(input_folder)
    # xlsx to dataframe
    
    # draw the bar chart with document_type
    current_time = time.strftime("%Y-%m-%d", time.localtime())
    if compared_folder==None:
        # print(1)
        draw_bar_and_line_chart(df_gap, f'{current_time} Project {document_type} Report Status', output_folder)
        draw_bar_and_line_chart(df_link, f'{current_time} Project {document_type} Report Link', output_folder)
    else:
        df_gap_comp = extract_gap(compared_folder)
        df_link_comp = extract_linked_request(compared_folder)
        # df_gap_comp = pd.read_excel('output\df_gap_comp.xlsx', index_col=[0, 1])
        # df_link_comp = pd.read_excel('output\df_link_comp.xlsx', index_col=[0, 1])
        draw_bar_and_line_chart(df_gap,  f'{current_time} Project {document_type} Report Status', output_folder, df_gap_comp)
        draw_bar_and_line_chart(df_link,  f'{current_time} Project {document_type} Report Link', output_folder, df_link_comp)
    # # save the dataframe to excel
    # df_gap.to_excel(os.path.join(output_folder, 'df_gap.xlsx'))
    # df_link.to_excel(os.path.join(output_folder, 'df_link.xlsx'))
    # df_gap_comp.to_excel(os.path.join(output_folder, 'df_gap_comp.xlsx'))
    # df_link_comp.to_excel(os.path.join(output_folder, 'df_link_comp.xlsx'))

if __name__ == '__main__':
    # # give the absolute path of the folder
    # input_folder = r'C:\Users\sophie\OneDrive\桌面\autoDraw\new'
    # compared_folder = r'C:\Users\sophie\OneDrive\桌面\autoDraw\pre'
    input_folder = r'C:\Users\sophie\OneDrive\桌面\autoDraw\example_original'
    compared_folder = r'C:\Users\sophie\OneDrive\桌面\autoDraw\example_compared' 
    output_folder = r'C:\Users\sophie\OneDrive\桌面\autoDraw\output'
    # if not os.path.exists(output_folder):
    #     os.mkdir(output_folder)
    auto_draw(input_folder, output_folder, 'status', compared_folder)

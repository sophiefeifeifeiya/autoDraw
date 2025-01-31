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


def exchange_max_location(df,df_comp=None):
    """Exchange the max value location with the last row"""
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
        return df, df_comp
    else:
        return df



def draw_bar_and_line_chart(df, title, output_folder, df_comp=None):
    '''
    Draw a stacked bar chart and a line chart for comparison with matplotlib
    '''

    fig, ax1 = plt.subplots()

    ax1.bar(range(len(df.index)), df.iloc[:, 0],  color='green', label = "No Gap")
    if df.iloc[-1, 1] > 0:
        ax1.bar(len(df.index)-1, df.iloc[-1, 1], bottom=df.iloc[-1, 0], color='red', label= "Max Gap")
    if df.iloc[:len(df.index)-1, 1].max() > 0:
        ax1.bar(range(len(df.index)-1), df.iloc[:len(df.index)-1, 1],  bottom=df.iloc[:len(df.index)-1, 0], color='yellow', label="Existing Gap")
    
    # set the x-axis by the "name"
    ax1.set_xticks(range(len(df.index)))
    ax1.set_xticklabels(df["name"], rotation=45, ha='right')
    
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
        df_diff=df.iloc[:,1] - df_comp.iloc[:,1]
        df_diff_percent=df_diff.copy()
        # if the element of df_diff is 0, leave this element as 0. Otherwise, calculate the percentage
        for i in range(len(df_diff_percent)):
            if df_diff_percent.iloc[i] != 0:
                df_diff_percent.iloc[i] = df_diff_percent.iloc[i]/df.iloc[i,1]
        df_diff_percent = df_diff_percent*100
        df_diff_percent = df_diff_percent.round(2)

        # increase the length of top of the ax1
        ax1.set_ylim(top=(df.iloc[:, 0].max() + df.iloc[:, 1].max())*1.1)


        # add text above the stacked bar chart to show the percentage of the difference
        for i in range(len(df_diff_percent)):
            plt.text(i, df.iloc[i, 0] + df.iloc[i, 1]+(df.iloc[:, 0].max() + df.iloc[:, 1].max())*0.1, str(df_diff_percent.iloc[i]) + "%", ha='center', va='center')

       
        # let the legend and title will not be cut off 
        fig.set_figwidth(2+len(df)*1.5)
        # plt.tight_layout()
        # title will not be cut off
        if len(df)<=8:
            ax1.legend(fontsize='small', loc = (1.20, 0.8))
            # add comments to the right of the chart, which is "(COEM, Project Amount)"
            plt.text(len(df_diff_percent), 1000, "(COEM, Project Amount)", fontsize='small')
            plt.subplots_adjust(top=0.8, bottom=0.4, right=0.6)
        else:
            ax1.legend(fontsize='small', loc = (1.05, 0.8))
            plt.text(len(df_diff_percent)*1.05, (df.iloc[:, 0].max() + df.iloc[:, 1].max())*0.6, "(COEM, Project Amount)", fontsize='small')
            plt.subplots_adjust(top=0.9, bottom=0.3, right = 0.8)
        
    else:
        # draw the ax1 only
        ax1.legend(fontsize='small', loc = (1.05, 0.8))


    # Set the chart title
    plt.title(title)

    # Save the image to the output folder
    plt.savefig(os.path.join(output_folder, title + '.png'))

def extract_coem_gap(input_folder):
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

def extract_coem_linked_request(input_folder):
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
            pvtTable.PivotFields(page_range_item[0]).CurrentPage = 'Agreed' 

            print(pvtTable.PivotFields(page_range_item[0]).CurrentPage)
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
            print("problem", file_path, e)
            excel.Application.Quit() 
        time.sleep(3)
    # convert the dict to dataframe, the key is th e index
    df = pandas.concat(linked_request_data)
    # set the first column "Number of requiredlink", the second column "Number of requirednotlink"
    df.index = df.index.map(lambda x: x[0])
    df.index = df.index.map(lambda x: (x, file_number[x]))
    return df

# auto_draw that contains compared_folder
def auto_draw_coem(input_folder,  output_folder, document_type, product, compared_folder=None):
    df_gap = pd.read_excel('output\df_gap.xlsx', index_col=[0])
    df_link = pd.read_excel('output\df_link.xlsx', index_col=[0])

    # df_gap = extract_coem_gap(input_folder)
    # df_link = extract_coem_linked_request(input_folder)
    # draw the bar chart with document_type
    current_time = time.strftime("%Y-%m-%d", time.localtime())
    if compared_folder==None:
        # df_gap=exchange_max_location(df_gap)
        # df_link = exchange_max_location(df_link)
        draw_bar_and_line_chart(df_gap, f'{current_time}_{product}_Project_{document_type} Report_Status', output_folder)
        draw_bar_and_line_chart(df_link, f'{current_time}_{product}_Project_{document_type} Report_Link', output_folder)
    else:
        df_gap_comp = pd.read_excel('output\df_gap_comp.xlsx', index_col=[0])
        df_link_comp = pd.read_excel('output\df_link_comp.xlsx', index_col=[0])
        # df_gap_comp = extract_coem_gap(compared_folder)
        # df_link_comp = extract_coem_linked_request(compared_folder)
        # df_gap, df_gap_comp = exchange_max_location(df_gap, df_gap_comp)
        # df_link, df_link_comp = exchange_max_location(df_link, df_link_comp)
        draw_bar_and_line_chart(df_gap,  f'{current_time}_{product}_Project_{document_type} Report_Status', output_folder, df_gap_comp)
        draw_bar_and_line_chart(df_link,  f'{current_time}_{product}_Project_{document_type} Report_Link', output_folder, df_link_comp)
    # #     save the dataframe to excel
    # df_gap.to_excel(os.path.join(output_folder, 'df_gap.xlsx'))
    # df_link.to_excel(os.path.join(output_folder, 'df_link.xlsx'))
    # df_gap_comp.to_excel(os.path.join(output_folder, 'df_gap_comp.xlsx'))
    # df_link_comp.to_excel(os.path.join(output_folder, 'df_link_comp.xlsx'))


if __name__ == '__main__':
    # # give the absolute path of the folder
    # input_folder = r'C:\Users\sophie\OneDrive\桌面\autoDraw\new'
    # compared_folder = r'C:\Users\sophie\OneDrive\桌面\autoDraw\pre'
    input_folder = r'C:\Users\sophie\OneDrive\桌面\autoDraw\new'
    compared_folder = r'C:\Users\sophie\OneDrive\桌面\autoDraw\pre' 
    output_folder = r'C:\Users\sophie\OneDrive\桌面\autoDraw\output'
    # if not os.path.exists(output_folder):
    #     os.mkdir(output_folder)
    auto_draw_coem(input_folder, output_folder, 'status', 'FR', compared_folder)

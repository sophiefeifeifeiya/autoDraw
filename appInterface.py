from pathlib import Path  # core python module
import pandas as pd  # pip install pandas openpyxl
import PySimpleGUI as sg  # pip install pysimplegui
from autoDrawCOEM import auto_draw_coem
from autoDrawProject import auto_draw_project

def is_valid_path(filepath):
    if filepath and Path(filepath).exists():
        return True   
    sg.popup_error("Filepath not correct")
    return False
 

# draw that contains compared folder
def draw(input_folder, output_folder, document_type, product, image_type, compared_folder=None):
    if image_type == "COEM":
        if compared_folder is None:
            auto_draw_coem(input_folder, output_folder, document_type, product)
        else:
            auto_draw_coem(input_folder,  output_folder, document_type, product,  compared_folder)
    elif image_type == "Project":
        if compared_folder is None:
            auto_draw_project(input_folder, output_folder, document_type, product)
        else:
            auto_draw_project(input_folder, output_folder, document_type, product,  compared_folder)
    sg.popup_no_titlebar("Done! :)")



def main_window():
    # ------ Menu Definition ------ #
    # menu_def = [["Toolbar", ["Command 1", "Command 2", "---", "Command 3", "Command 4"]],
    #             ["Help", ["Settings", "About", "Exit"]]]


    # ------ GUI Definition ------ #
    layout = [
        # [sg.MenubarCustom(menu_def, tearoff=False)],
              [sg.T("Main data Folder:", s=15, justification="r"), sg.I(key="-IN-"), sg.FolderBrowse()],
              # creata a new option to let user to select the folder to be compared (can be empty)
              [sg.T("Compared Folder:", s=15, justification="r"), sg.I(key="-PRE-"), sg.FolderBrowse()],
              [sg.T("Output Folder:", s=15, justification="r"), sg.I(key="-OUT-"), sg.FolderBrowse()],
              # create an option that let user to select, including 3 buttons, "Customer"  "System" "Software"
              [sg.T("Document Type:", s=15, justification="r"), sg.Radio("Customer", "RADIO1", default=True, key="-CUSTOMER-"), sg.Radio("System", "RADIO1", key="-SYSTEM-"), sg.Radio("Software", "RADIO1", key="-SOFTWARE-")],
              [sg.T("Product:", s=15, justification="r"), sg.Radio("FR", "RADIO2", default=True, key="-FR-"), sg.Radio("CR", "RADIO2", key="-CR-"), sg.Radio("MPC", "RADIO2", key="-MPC-")],
              # create an option to select the type of images, including "COEM", "Project" 
              [sg.T("Image Type:", s=15, justification="r"), sg.Radio("COEM", "RADIO3", default=True, key="-COEM-"), sg.Radio("Project", "RADIO3", key="-PROJECT-")],
              [sg.Exit(s=16, button_color="tomato"), sg.B("Auto-draw", s=16)],]

    window_title = settings["GUI"]["title"]
    window = sg.Window(window_title, layout, use_custom_titlebar=True)

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, "Exit"):
            break
        # if event == "About":
        #     window.disappear()
        #     sg.popup(window_title, "Version 1.0", "Convert Excel files to CSV", grab_anywhere=True)
        #     window.reappear()
        # if event in ("Command 1", "Command 2", "Command 3", "Command 4"):
        #     sg.popup_error("Not yet implemented")
        if event == "Auto-draw":
            if (is_valid_path(values["-IN-"])) and (is_valid_path(values["-OUT-"])) and values["-PRE-"]:
                if(is_valid_path(values["-PRE-"])):
                    draw(
                        input_folder=values["-IN-"],
                        compared_folder=values["-PRE-"],
                        output_folder=values["-OUT-"],
                        # document
                        document_type= "Customer" if values["-CUSTOMER-"] else "Software" if values["-SOFTWARE-"] else "System",
                        product= "FR" if values["-FR-"] else "CR" if values["-CR-"] else "MPC",
                        image_type= "COEM" if values["-COEM-"] else "Project",
                    )

            elif(is_valid_path(values["-IN-"])) and (is_valid_path(values["-OUT-"])):
                draw(
                    input_folder=values["-IN-"],
                    output_folder=values["-OUT-"],
                    # document
                    document_type= "Customer" if values["-CUSTOMER-"] else "Software" if values["-SOFTWARE-"] else "System",
                    product= "FR" if values["-FR-"] else "CR" if values["-CR-"] else "MPC",
                    image_type= "COEM" if values["-COEM-"] else "Project",
                )
    window.close()



if __name__ == "__main__":
    SETTINGS_PATH = Path.cwd()
    # create the settings object and use ini format
    settings = sg.UserSettings(
        path=SETTINGS_PATH, filename="config.ini", use_config_file=True, convert_bools_and_none=True
    )
    theme = settings["GUI"]["theme"]
    font_family = settings["GUI"]["font_family"]
    font_size = int(settings["GUI"]["font_size"])
    sg.theme(theme)
    sg.set_options(font=(font_family, font_size))
    main_window()

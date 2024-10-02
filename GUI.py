import customtkinter
import queue
import subprocess
import sys
import threading
import tkinter
import tkinter.messagebox
from get_data import get_est_list
from main import main


# Global variables
global est_data

# Setting the color palette for the GUI. Will use blue accents on top of whatever mode the user is running their OS in
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

# Naming the application
APP_NAME = "Upcharge Patch"


# Using TextboxStream to output the print statements to the 'Output Console' within the GUI
class TextboxStream:
    def __init__(self, textbox, text_queue):
        self.textbox = textbox
        self.queue = text_queue
        self.textbox.configure(wrap=tkinter.WORD)

    def write(self, text):
        self.queue.put(text)
        self.textbox.insert(tkinter.END, text)
        self.textbox.see(tkinter.END)

    def flush(self):
        pass


# Event for when the CSV button is pressed
def csv_button_event():
    try:
        # Use subprocess to open File Explorer in the current directory
        subprocess.Popen('explorer .')
        print("Opened File Explorer in the current directory.\n")
    except Exception as e:
        print(f"Error opening File Explorer: {e}\n")


class GUI(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        ''' WINDOW SETTINGS '''
        self.title("Primo Upcharge Patch")
        self.geometry("1200x580")

        ''' GRID LAYOUT SETTINGS w/ WEIGHT'''
        # Defining dynamic resizing weight on column 1 and 2 (textbox and scrollable switch frame)
        self.grid_columnconfigure((1, 2), weight=1)
        # Setting weight on rows 0, 1, and 2, keeping them anchored to the window regardless of size
        self.grid_rowconfigure((0, 1, 2), weight=1)

        ''' SIDEBAR FRAME '''
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text=APP_NAME,
                                                 font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.sidebar_button_3 = customtkinter.CTkButton(self.sidebar_frame, command=csv_button_event,
                                                        text="CSV Files")
        self.sidebar_button_3.grid(row=1, column=0, padx=20, pady=10)


        ''' PATCH BUTTON'''
        self.patch_button = customtkinter.CTkButton(
            master=self,
            fg_color="#98FF98",
            text_color="Black",
            text="PATCH",
            width=230,
            height=50,
            state="normal"
        )
        self.patch_button.grid(row=3, column=3, padx=(20, 20), pady=(20, 20), sticky="se")
        self.patch_button.configure(command=self.patch_button_click)


        ''' TEXT BOX OUTPUT CONSOLE '''
        self.textbox = customtkinter.CTkTextbox(self, width=250)
        self.textbox.grid(row=0, column=1, rowspan=3, padx=(20, 0), pady=(20, 0), sticky="nsew")
        # Redirect print statements to the textbox
        self.output_queue = queue.Queue()
        sys.stdout = TextboxStream(self.textbox, self.output_queue)


        ''' RADIO BUTTON FRAME FOR MODE SELECTION'''
        # Frame
        self.radiobutton_frame = customtkinter.CTkFrame(self)
        self.radiobutton_frame.grid(row=0, column=3, rowspan=3, padx=(20, 20), pady=(20, 0), sticky="nsew")
        # Variable
        self.radio_var = tkinter.IntVar(value=0)
        # Label
        self.label_radio_group = customtkinter.CTkLabel(master=self.radiobutton_frame, text="Select Mode:")
        self.label_radio_group.grid(row=0, column=2, columnspan=1, pady=10, sticky="ew")
        # Select establishments button
        self.select_est_radio_button = customtkinter.CTkRadioButton(master=self.radiobutton_frame, variable=self.radio_var,
                                                                    value=0, text="Select Establishments")
        self.select_est_radio_button.grid(row=1, column=2, pady=10, padx=20, sticky="w")
        self.select_est_radio_button.bind("<ButtonRelease-1>", self.select_est_button_click)
        # All establishments button
        self.all_est_radio_button = customtkinter.CTkRadioButton(master=self.radiobutton_frame, variable=self.radio_var,
                                                                 value=1, text="All Establishments")
        self.all_est_radio_button.grid(row=2, column=2, pady=10, padx=20, sticky="w")
        self.all_est_radio_button.bind("<ButtonRelease-1>", self.all_est_button_click)


        ''' SCROLLABLE FRAME FOR EST SWITCHES '''
        self.scrollable_frame = customtkinter.CTkScrollableFrame(self, label_text="Site List")
        self.scrollable_frame.grid(row=0, column=2, rowspan=4, padx=(20, 0), pady=(20, 20), sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        # Define scrollable_frame_switches as an instance variable
        self.scrollable_frame_switches = []
        # Retrieve the establishment data and populate switches as well as the global variable definition
        global est_data
        est_data = get_est_list()
        self.populate_switches_from_dict()


        ''' PROGRESS BAR '''
        self.progressbar_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.progressbar_frame.grid(row=3, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.progressbar_frame.grid_columnconfigure(0, weight=1)
        self.progressbar_frame.grid_rowconfigure(3, weight=1)
        self.progressbar = customtkinter.CTkProgressBar(self.progressbar_frame)
        self.progressbar.grid(row=1, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")


        ''' DEFAULT VALUES '''
        self.textbox.delete("1.0", "end")
        self.textbox.insert("0.0", "Output Console\n\nMode: Upcharge Patch\n\n- Patch catering items\n\n")
        self.progressbar.set(0)


    ''' PATCH BUTTON EVENT '''
    # Patch button event configuration
    def patch_button_click(self):
        # Clearing out the textbox
        self.textbox.delete("1.0", tkinter.END)

        # Setting the progress bar to 'indeterminate', which will make it move while processing is active
        self.progressbar.configure(mode="indeterminate")
        self.progressbar.start()

        # Disabling the 'Patch' button, so it cannot be clicked while function is running
        self.patch_button.configure(state="disabled")

        # Reference the est_data variable, which is populated on creation with est data
        global est_data

        # Create a list to store the "id" values
        id_list = []

        ''' Get switch status and populate id_list for call to main function '''
        # Get the "id" values associated with the names of switches that are in the "On" state
        for i, switch in enumerate(self.scrollable_frame_switches):
            # Check if switch is selected
            if switch.get():
                # Get the text of the switch, will be the same as the key in the dict ('name')
                est_name = switch.cget('text')
                # Get the 'id' of the est from the dict
                est_id = est_data.get(est_name)

                # Print the est id and name for clarity in GUI which establishments are selected on run
                print(f"Est {est_id}: {est_name}\n")

                # Append the id to the id_list, which will be passed to the main function for execution
                id_list.append(est_id)

        # Defining a function to run this in a separate thread. Keeps GUI functional while running
        def run_operation():
            # Calling the main function with the id_list as a param. Gets data in parallel for each est in list.
            main(id_list)
            # Notify the main thread that the operation is complete. (Does nothing. Text output handled in func)
            self.operation_complete()

        ''' THREAD INIT '''
        # Create a thread to run the operation
        operation_thread = threading.Thread(target=run_operation)
        # Start the thread
        operation_thread.start()
        # Check if the thread has completed periodically
        self.check_operation_status(operation_thread)


    ''' THREAD FUNCTIONS '''
    def check_operation_status(self, operation_thread):
        # If thread is alive, keep checking until it is finished
        if operation_thread.is_alive():
            self.after(1000, lambda: self.check_operation_status(operation_thread))
        else:
            # The thread has completed. Make the patch button active again and stop the progress bar from moving
            self.progressbar.stop()
            self.progressbar.configure(mode="determinate")
            self.patch_button.configure(state="normal")


    def operation_complete(self):
        # This function could be configured to do something once the operation is finished. Just passing for now
        pass


    ''' RADIO BUTTON EVENTS '''
    def all_est_button_click(self, event):
        # If clicked, for each switch in the scrollable frame, set the state to active (select())
        if self.radio_var.get() == 1:
            for switch in self.scrollable_frame_switches:
                switch.select()


    def select_est_button_click(self, event):
        # If clicked, deselect all switches within the frame
        if self.radio_var.get() == 0:
            for switch in self.scrollable_frame_switches:
                switch.deselect()


    ''' POPULATE RADIO BUTTONS '''
    def populate_switches_from_dict(self):
        # For each est in est_data...
        for i, est_name in enumerate(est_data.keys()):
            # Create a switch with the name of the est
            switch = customtkinter.CTkSwitch(
                master=self.scrollable_frame,
                text=est_name
            )
            switch.grid(row=i, column=0, padx=10, pady=(0, 20), sticky="w")
            self.scrollable_frame_switches.append(switch)


if __name__ == "__main__":
    app = GUI()
    app.mainloop()
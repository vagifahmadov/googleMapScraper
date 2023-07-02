import importlib
import tkinter
from tkinter import *
from tkinter import ttk

if __name__ == "__main__":

    # submit and visual view
    def submit_button_func(search: str, scroll_map: str, label, attempt_value: str, progress):
        notify = ''
        color = '#000'
        label.config(text=notify, fg=color)
        if scroll_map == '' or attempt_value == '':
            notify = "Not inserted fields or some thing went wrong"
            color = "#f00"
        else:
            error = False
            task = 'src.scraper'
            Task = importlib.import_module(task).Task
            t = Task()
            try:
                t.scroll_times = int(scroll_map)
                t.attempt = int(attempt_value)
            except ValueError as e:
                error = True
                notify = "Invalid value"
                color = "#f00"
            if error is False:
                progress.start(10)
                pb.grid(columnspan=2, row=3, pady=15)
                t.queries.append(search)
                t.filtered_data = {}
                t.begin_task()
                result_pro = t.result_process
                notify = "" if result_pro['success'] is True else result_pro['message']
                color = "#000" if result_pro['success'] is True else "#f00"
        result = []
        print(f'search:{search}\nscroll:{scroll_map}\nattempt:{attempt_value}')
        progress.stop()
        progress.grid_forget()
        label.config(text=notify, fg=color)
        return result

    window = tkinter.Tk()

    window.title("GoogleMap BOT")
    frame = tkinter.Frame(window, padx=10, pady=10)
    frame.pack()
    window.resizable(False, False)
    window.geometry('550x320')
    # image = PhotoImage(file="turkey.png")
    # window.iconphoto(True, image)

    #  1st head TAB label
    website_title = tkinter.LabelFrame(frame)
    website_title.grid(row=0, column=0)
    website_name = tkinter.Label(website_title, text="GoogleMap scraper", fg='#f00', pady=10, padx=10, font=10)
    website_name.grid(row=0, column=0)

    # 2nd head big TAB label
    head_label = tkinter.LabelFrame(frame, text="Type your place and objects", pady=10, padx=10, font=14)
    head_label.grid(row=1, column=0)

    # progress bar
    pb = ttk.Progressbar(
        head_label,
        orient='horizontal',
        mode='indeterminate',
        length=350
    )
    pb.grid(columnspan=2, row=3, pady=15)
    pb.grid_forget()

    search_label = tkinter.Label(head_label, text="Search:", font=10, padx=20)
    search_label.grid(row=0, column=0, sticky=E)

    search_box = tkinter.Entry(head_label, font=3)
    search_box.grid(row=0, column=1)

    scroll_times_label = tkinter.Label(head_label, text="Scroll times(min. x10):", font=10, padx=20)
    scroll_times_label.grid(row=1, column=0, sticky=E)

    scroll_times = tkinter.Entry(head_label, font=3)
    # remaining_days.insert(0, 10)
    scroll_times.grid(row=1, column=1)

    attempt_label = tkinter.Label(head_label, text="Attempt:", font=10, padx=20)
    attempt_label.grid(row=2, column=0, sticky=E)

    attempt = tkinter.Entry(head_label, font=3)
    # remaining_days.insert(0, 10)
    attempt.grid(row=2, column=1)

    # 3rd TAB label
    # footer_tab = tkinter.LabelFrame(frame, pady=30, padx=10, font=10)
    # footer_tab.grid(row=2, column=0)

    # error TAB
    error_label_tab = tkinter.LabelFrame(frame, pady=5, padx=5)
    # result TAB
    result_label_tab = tkinter.LabelFrame(frame, padx=5, pady=5)

    error_label_tab.grid(row=2, column=0, pady=5)

    error_label = tkinter.Label(error_label_tab, text="", padx=10, pady=10, width=40)
    error_label.grid(row=0, column=0)

    submit_button = tkinter.Button(error_label_tab, text="Lookup", font=10, command=lambda: submit_button_func(search=search_box.get(), scroll_map=scroll_times.get(), label=error_label, attempt_value=attempt.get(), progress=pb))
    submit_button.grid(row=1, column=0, sticky="news")

    # create_tree_v_layout(window)

    window.mainloop()

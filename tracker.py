from tkinter.messagebox import askokcancel
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from os import getcwd, path
import ttkbootstrap as ttk
from time import strftime
from calendar import isleap

# variables - DataFrame
get_dir = getcwd()
filename = path.join(get_dir, "tracker.csv")
df = pd.read_csv(filename)

# variables - input lists
year_min, month_max, date_max, mood_max = 2010, 12, 31, 10
date_options = [f"{i:02}" for i in range(1, date_max + 1)]
month_options = [f"{i:02}" for i in range(1, month_max + 1)]
month_days = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
month_names = {
    1: "January", 2: "February", 3: "March",
    4: "April", 5: "May", 6: "June",
    7: "July", 8: "August", 9: "September",
    10: "October", 11: "November", 12: "December"
}
year_options = [i for i in range(year_min, int(strftime("%Y")) + 1)]
mood_score = [i for i in range(1, mood_max + 1)]

# CONST
BTN_CONFIG = {"padx": 10, "pady": 20, "ipadx": 20, "ipady": 10, "row": 0}
GRID_LABEL = {"padx": 10, "pady": 10, "sticky": "nsew", "ipadx": 20}
INSIGHTS_OPTION = ["LOWEST MOOD", "HIGHEST MOOD", "MONTH AVR.", "YEAR AVR."]
COLOURS = {"white": "#FFFFFF", "dark": "#222222", "magenta": "#FF89FF", "lighter_dark": "#3B3B3B"}
TITLE_FONT = {"font": ("Helvetica", 16, "bold"), "anchor": "w"}
VALUE_FONT = {"font": ("Helvetica", 16), "anchor": "w"}
LABELS = {"y": "MOOD LEVEL", "x": "DAY OF MONTH"}
TICKS = {"axis": "both", "color": COLOURS["white"], "labelcolor": COLOURS["white"]}
SUB_ADJUST = {"left": 0.05, "right": 0.95, "top": 0.95, "bottom": 0.1}
LINE_STYLE = {"color": COLOURS["lighter_dark"], "linestyle": "--", "linewidth": 1.5, "alpha": 0.7}
Y_LINES = {"top": {"y": 8, **LINE_STYLE}, "mid": {"y": 5, **LINE_STYLE}, "base": {"y": 2, **LINE_STYLE}}
TEXT_STYLE = {"color": COLOURS["lighter_dark"], "fontsize": 10}
Y_TEXTS = {"top": {"x": 2, "y": 8.2, "s": "Hypomania", **TEXT_STYLE},
           "base": {"x": 2, "y": 2.2, "s": "Depression", **TEXT_STYLE}}


class Data:
    def __init__(self):
        self.original_df = df.copy()
        self.df = self.original_df
        self.year = None
        self.month = None
        self.date = None
        self.mood = 0
        self.axis = None
        self.entry_count = None
        self.plot_refresh = None

    def reset_dataframe(self):
        self.df = self.original_df.copy()

    def select_options(self):
        self.month = int(month_choice.get())
        self.year = int(year_choice.get())
        self.date = int(date_choice.get())
        self.mood = int(mood_choice.get())

    def update_csv(self):

        self.select_options()

        self.df['DATE'] = self.df['DATE'].astype(int)
        self.df['MONTH'] = self.df['MONTH'].astype(int)
        self.df['YEAR'] = self.df['YEAR'].astype(int)

        index_update = self.df[
            (self.df["MONTH"] == self.month) & (self.df["DATE"] == self.date) & (self.df["YEAR"] == self.year)].index

        if not index_update.empty:

            current_value = self.df.loc[index_update[0], "MOOD_LVL"]

            if not (pd.isna(current_value) or current_value == 0):
                overwrite_message = "There is an existing entry for this date.\nDo you wish to overwrite?"
                overwrite_warning = askokcancel(title="Overwrite", message=overwrite_message, icon="warning")
                if overwrite_warning:
                    self.df.loc[index_update[0], "MOOD_LVL"] = self.mood
            else:

                self.df.loc[index_update[0], "MOOD_LVL"] = self.mood
        else:

            new_entry = pd.DataFrame({"DATE": [self.date], "MONTH": [self.month],
                                      "YEAR": [self.year], "MOOD_LVL": [self.mood]})
            self.df = pd.concat([self.df, new_entry], ignore_index=True)

        # sort
        self.df = self.df.sort_values(["YEAR", "MONTH", "DATE"], ascending=[True, True, True])
        self.df = self.df.reset_index(drop=True)

        # save
        self.df.to_csv(filename, index=False)

    def plot_configuration(self, xticks=range(1, 32), yticks=range(1, 11), xlim=None, ylim=(0, 10)):

        self.axis.set_ylabel(LABELS["y"], color=COLOURS["white"])
        self.axis.set_xlabel(LABELS["x"], color=COLOURS["white"])
        self.axis.set_xticks(xticks)
        self.axis.set_yticks(yticks)
        self.axis.tick_params(**TICKS)
        self.axis.set_ylim(ylim)
        if xlim:
            self.axis.set_xlim(xlim)
        fig.patch.set_facecolor(COLOURS["dark"])
        self.axis.set_facecolor(COLOURS["dark"])
        [spine.set_edgecolor(COLOURS["white"]) for spine_type, spine in self.axis.spines.items()]
        fig.subplots_adjust(**SUB_ADJUST)
        self.axis.axhline(**Y_LINES["top"])
        self.axis.axhline(**Y_LINES["mid"])
        self.axis.axhline(**Y_LINES["base"])
        self.axis.text(**Y_TEXTS["top"])
        self.axis.text(**Y_TEXTS["base"])

        for spine_type, spine in self.axis.spines.items():
            spine.set_visible(False) if spine_type in ["top", "right"] else None

    def plot(self):
        if self.plot_refresh:
            root.after_cancel(self.plot_refresh)

        self.select_options()
        fig.clf()
        self.axis = fig.add_subplot(111)

        if not self.month or not self.year:
            self.plot_configuration()

        else:
            try:
                current_data = self.df[(self.df["MONTH"] == self.month) & (self.df["YEAR"] == self.year)]
                x_val = current_data["DATE"]
                y_val = current_data["MOOD_LVL"]
                self.plot_configuration(xticks=x_val, xlim=(min(x_val), max(x_val)))
                self.axis.plot(x_val, y_val, color=COLOURS["magenta"], linewidth="2.5")

            except ValueError:
                self.plot_configuration()

        # refresh
        canvas.draw()
        self.get_values()

        self.plot_refresh = root.after(100, self.plot)

    def get_values(self, analysis=None):

        if not analysis:

            selections = df[(df["YEAR"] == self.year) & (df["MONTH"] == self.month)]
            year_selections = df[(df["YEAR"] == self.year)]

            max_result = selections["MOOD_LVL"].max() if not selections.empty else 0.0
            min_result = selections["MOOD_LVL"].min() if not selections.empty else 0.0
            mean_result = round(selections["MOOD_LVL"].mean(), 1) if not selections.empty else 0.0
            year_mean_result = round(year_selections["MOOD_LVL"].mean(), 1) if not year_selections.empty else 0.0

            mean_mood.set(mean_result)
            year_mean.set(year_mean_result)
            max_mood.set(max_result)
            min_mood.set(min_result)

        else:
            # analysis screen

            # get total yearly entries
            check_for_value = self.df[(self.df["YEAR"] == self.year) & (self.df["MOOD_LVL"] >= 1)]
            self.entry_count = check_for_value["MOOD_LVL"].count()

            year = int(year_choice.get())

            if isleap(int(year)):
                total_entries.set(f"{self.entry_count} / 366")
            else:
                total_entries.set(f"{self.entry_count} / 365")

            # get best month (max counts between lvl 4 and lvl 6)
            top_month_df = self.df[(self.df["YEAR"] == self.year) & (self.df["MOOD_LVL"] >= 4) & (df["MOOD_LVL"] <= 6)]
            monthly_count = top_month_df.groupby("MONTH").size().reset_index(name="COUNT").max()

            # convert month to string
            best_month = monthly_count["MONTH"]
            if best_month in month_names:
                best_month = month_names[best_month]
                most_stable.set(best_month)
            most_stable.set(best_month)


def build_cell(pframe, widget_content):
    cell = ttk.Frame(pframe)

    if isinstance(widget_content, ttk.StringVar) or isinstance(widget_content, ttk.IntVar):
        label = ttk.Label(cell, textvariable=widget_content, **VALUE_FONT)

    else:
        label = ttk.Label(cell, text=widget_content, **TITLE_FONT)

    label.grid(**GRID_LABEL)

    return cell


def date_options_update(*args):
    month = int(month_choice.get())
    year = int(year_choice.get())

    days = month_days[month]

    if isleap(year):
        days += 1

    date_options_updated = [f"{i:02}" for i in range(1, days + 1)]
    date_dropdown["menu"].delete(0, "end")
    for day in date_options_updated:
        date_dropdown["menu"].add_command(label=day, command=lambda value=day: date_choice.set(value))

    date_choice.set(date_options_updated[0])


def analysis_initiate(main=None):

    if not main:
        insights_frame.grid_forget()
        figure_frame.grid_forget()
        selection_frame.grid_forget()

        # initiation get_values()
        d.get_values(analysis=True)
        root.geometry("")
        analysis_frame.grid(padx=50, pady=50)

        # "back" button
        button_frame.grid(row=1, column=0, sticky="se", padx=10, pady=10)
        back_button = ttk.Button(button_frame, text="Back", command=main_initiate)
        back_button.grid(**BTN_CONFIG)

        # build title cells
        total_entries_title = build_cell(analysis_frame, "Entry Total")
        best_month_title = build_cell(analysis_frame, "Best Month")

        # build value cells
        total_entries_label = build_cell(analysis_frame, total_entries)
        best_month_label = build_cell(analysis_frame, most_stable)

        total_entries_title.grid(row=0, column=0)
        total_entries_label.grid(row=1, column=0)
        best_month_title.grid(row=0, column=1)
        best_month_label.grid(row=1, column=1)


def main_initiate():

    for widget in analysis_widgets:
        widget.grid_forget()

    insights_frame.grid(row=0, column=0, pady=20)

    min_mood_title_label.grid(row=0, column=0, padx=20, pady=20)
    max_mood_title_label.grid(row=0, column=1, padx=20, pady=20)
    mean_mood_title_label.grid(row=0, column=2, padx=20, pady=20)
    year_mean_title_label.grid(row=0, column=3, padx=20, pady=20)

    min_mood_label.grid(row=1, column=0, padx=20, pady=20)
    max_mood_label.grid(row=1, column=1, padx=20, pady=20)
    mean_mood_label.grid(row=1, column=2, padx=20, pady=20)
    year_mean_label.grid(row=1, column=3, padx=20, pady=20)

    figure_frame.grid(row=1, column=0)
    canvas_embed.grid()

    [btns.grid(**BTN_CONFIG, column=column) for column, btns in enumerate(selection_btns)]
    selection_frame.grid(padx=20, pady=10)

    d.plot()


# main window
root = ttk.Window(themename="darkly")
root.resizable(False, False)
root.geometry("1660x880")
root.title("Mood Tracker")
d = Data()

# insights configuration
insights_frame = ttk.Frame(root)
max_mood, min_mood, mean_mood, year_mean = ttk.StringVar(), ttk.StringVar(), ttk.StringVar(), ttk.StringVar()
insights_frame.grid(row=0, column=0, pady=20)

# insights initiation
min_mood_title_label = ttk.Label(insights_frame, text=INSIGHTS_OPTION[0], **TITLE_FONT)
max_mood_title_label = ttk.Label(insights_frame, text=INSIGHTS_OPTION[1], **TITLE_FONT)
mean_mood_title_label = ttk.Label(insights_frame, text=INSIGHTS_OPTION[2], **TITLE_FONT)
year_mean_title_label = ttk.Label(insights_frame, text=INSIGHTS_OPTION[3], **TITLE_FONT)

min_mood_label = ttk.Label(insights_frame, textvariable=min_mood, **VALUE_FONT)
max_mood_label = ttk.Label(insights_frame, textvariable=max_mood, **VALUE_FONT)
mean_mood_label = ttk.Label(insights_frame, textvariable=mean_mood, **VALUE_FONT)
year_mean_label = ttk.Label(insights_frame, textvariable=year_mean, **VALUE_FONT)

min_mood_title_label.grid(row=0, column=0, padx=20, pady=20)
max_mood_title_label.grid(row=0, column=1, padx=20, pady=20)
mean_mood_title_label.grid(row=0, column=2, padx=20, pady=20)
year_mean_title_label.grid(row=0, column=3, padx=20, pady=20)

min_mood_label.grid(row=1, column=0, padx=20, pady=20)
max_mood_label.grid(row=1, column=1, padx=20, pady=20)
mean_mood_label.grid(row=1, column=2, padx=20, pady=20)
year_mean_label.grid(row=1, column=3, padx=20, pady=20)

# figure configuration
figure_frame = ttk.Frame(root)
figure_frame.grid(row=1, column=0)
fig = Figure(figsize=(15, 5), dpi=110)
canvas = FigureCanvasTkAgg(fig, master=figure_frame)
canvas_embed = canvas.get_tk_widget()
canvas_embed.grid()

# main configuration
selection_frame = ttk.Frame(root)
year_choice, month_choice, date_choice = ttk.StringVar(), ttk.StringVar(), ttk.StringVar()
mood_choice = ttk.StringVar()
year_choice.set(strftime("%Y")), month_choice.set(strftime("%m")), date_choice.set(strftime("%d"))

# analysis configuration
total_entries, most_stable = ttk.StringVar(), ttk.StringVar()
analysis_frame = ttk.Frame(root)
button_frame = ttk.Frame(root)
analysis_widgets = [analysis_frame, button_frame]

# selection dropdown menu initiation
date_dropdown = ttk.OptionMenu(selection_frame, date_choice, strftime("%d"), *date_options)
month_view_dropdown = ttk.OptionMenu(selection_frame, month_choice, strftime(f"%m"), *month_options)
year_view_dropdown = ttk.OptionMenu(selection_frame, year_choice, strftime(f"%Y"), *year_options)

mood_dropdown = ttk.OptionMenu(selection_frame, mood_choice, "0", *mood_score)
save_btn = ttk.Button(selection_frame, text="Update", command=d.update_csv)
analysis_btn = ttk.Button(selection_frame, command=analysis_initiate, text="Analysis")
selection_btns = [date_dropdown, month_view_dropdown, year_view_dropdown, mood_dropdown, save_btn, analysis_btn]
[btns.grid(**BTN_CONFIG, column=column) for column, btns in enumerate(selection_btns)]
selection_frame.grid(padx=20, pady=10)

month_choice.trace("w", date_options_update)
year_choice.trace("w", date_options_update)

d.plot()
root.mainloop()

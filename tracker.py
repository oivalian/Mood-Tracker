from tkinter.messagebox import askokcancel
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from os import getcwd, path
import ttkbootstrap as ttk
from time import strftime

# variables - DataFrame
get_dir = getcwd()
filename = path.join(get_dir, "tracker.csv")
df = pd.read_csv(filename)

# variables - input lists
year_min, month_max, date_max, mood_max = 2010, 12, 31, 10
date_options = [f"{i:02}" for i in range(1, date_max + 1)]
month_options = [f"{i:02}" for i in range(1, month_max + 1)]
month_days = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
year_options = [i for i in range(year_min, int(strftime("%Y")) + 1)]
mood_score = [i for i in range(1, mood_max + 1)]

# CONST
BTN_CONFIG = {"padx" : 10, "pady" : 20, "ipadx" : 20, "ipady" : 10, "anchor" : "w", "side" : "left"}
INSIGHTS_VALUE = {"padx" : 20, "side" : "top", "anchor" : "w"}
INSIGHTS_TITLE = {"padx" : 20, "pady" : 5, "side" : "top", "anchor" : "w"}
INSIGHTS_OPTION = ["LOWEST MOOD", "HIGHEST MOOD", "MONTH AVR.", "YEAR AVR."]
COLOURS = {"white" : "#FFFFFF", "dark" : "#222222", "magenta" : "#FF89FF", "lighter_dark" : "#3B3B3B"}
TITLE_FONT = {"font" : ("Helvetica", 16, "bold"), "anchor" :"w"}
VALUE_FONT = {"font" : ("Helvetica", 16), "anchor" :"w"}
LABELS = {"y" : "MOOD LEVEL", "x" : "DAY OF MONTH"}
TICKS = {"axis" : "both", "color" : COLOURS["white"], "labelcolor" : COLOURS["white"]}
SUB_ADJUST = {"left" : 0.05, "right" : 0.95, "top" : 0.95, "bottom" : 0.1}
LINE_STYLE = {"color" : COLOURS["lighter_dark"], "linestyle" : "--", "linewidth" : 1.5, "alpha" : 0.7}
Y_LINES = {"top": {"y": 8, **LINE_STYLE}, "mid": {"y": 5, **LINE_STYLE}, "base": {"y": 2, **LINE_STYLE}}
TEXT_STYLE = {"color" : COLOURS["lighter_dark"], "fontsize" : 10}
Y_TEXTS = {"top": {"x": 2, "y": 8.2, "s": "Hypomania", **TEXT_STYLE},
            "base": {"x": 2, "y": 2.2, "s": "Depression", **TEXT_STYLE}}


class Data:
    def __init__(self):
        self.df = df
        self.year = None
        self.month = None
        self.date = None
        self.mood = 0
        self.axis = None

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

        index_update = self.df[(self.df["MONTH"] == self.month) & (self.df["DATE"] == self.date) & (self.df["YEAR"] == self.year)].index

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
        root.after(100, d.plot)

    def get_values(self):
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

def date_options_update(*args):
    month = int(month_choice.get())
    year = int(year_choice.get())

    days = month_days[month]

    if month == 2 and ((year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)):
        days += 1

    date_options_updated = [f"{i:02}" for i in range(1, days + 1)]
    date_dropdown["menu"].delete(0, "end")
    for day in date_options_updated:
        date_dropdown["menu"].add_command(label=day, command=lambda value=day: date_choice.set(value))

    date_choice.set(date_options_updated[0])

# main window
root = ttk.Window(themename="darkly")
root.resizable(False, False)
root.title("BPII Mood Tracker")
d = Data()

# insights configuration
insights_frame = ttk.Frame(root)
max_mood, min_mood, mean_mood, year_mean = ttk.StringVar(), ttk.StringVar(), ttk.StringVar(), ttk.StringVar()
insights_frame.pack(pady=20)

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

#figure configuration
figure_frame = ttk.Frame(root)
fig = Figure(figsize=(15, 5), dpi=110)
canvas = FigureCanvasTkAgg(fig, master=figure_frame)
canvas_embed = canvas.get_tk_widget()
canvas_embed.pack()
figure_frame.pack()

# selection configuration
selection_frame = ttk.Frame(root)
year_choice, month_choice, date_choice = ttk.StringVar(), ttk.StringVar(), ttk.StringVar()
mood_choice = ttk.StringVar()
year_choice.set(strftime("%Y")), month_choice.set(strftime("%m")), date_choice.set(strftime("%d"))


# selection dropdown menu initiation
date_dropdown = ttk.OptionMenu(selection_frame, date_choice, strftime("%d"), *date_options)
month_view_dropdown = ttk.OptionMenu(selection_frame, month_choice, strftime(f"%m"), *month_options)
year_view_dropdown = ttk.OptionMenu(selection_frame, year_choice, strftime(f"%Y"), *year_options)

mood_dropdown = ttk.OptionMenu(selection_frame, mood_choice, "0", *mood_score)
save_btn = ttk.Button(selection_frame, text="Update", command=d.update_csv)
selection_btns = [date_dropdown, month_view_dropdown, year_view_dropdown, mood_dropdown, save_btn]
[btns.pack(**BTN_CONFIG) for btns in selection_btns]
selection_frame.pack(padx=20, pady=10)

month_choice.trace("w", date_options_update)
year_choice.trace("w", date_options_update)


d.plot()
root.mainloop()

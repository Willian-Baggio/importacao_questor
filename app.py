import customtkinter as ctk
from tkinter import Tk, filedialog
from excel_reader import ExcelReader
from report_parser import ReportParser
from excel_reader import ExcelReader
from excel_service import ExcelService
from journal_generator import JournalGenerator

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class Application(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Importação Questor")
        self.geometry("700x650")

        self.selected_file = ""

        self.build_interface()

    def build_interface(self):

        title = ctk.CTkLabel(
            self,
            text="Accounting Automation",
            font=("Arial", 22, "bold")
        )
        title.pack(pady=20)

        self.file_label = ctk.CTkLabel(
            self,
            text="No file selected."
        )
        self.file_label.pack()

        select_button = ctk.CTkButton(
            self,
            text="Select Excel",
            command=self.select_file
        )
        select_button.pack(pady=10)

        date_label = ctk.CTkLabel(
            self,
            text="Date"
        )
        date_label.pack(pady=(20, 5))

        self.date_entry = ctk.CTkEntry(
            self,
            placeholder_text="DD/MM/YYYY"
        )
        self.date_entry.pack(fill="x", padx=20)

        generate_button = ctk.CTkButton(
            self,
            text="Generate Excel",
            command=self.generate
        )
        generate_button.pack(pady=30)

    def select_file(self):

        file = filedialog.askopenfilename(
            filetypes=[("Excel", "*.xlsx *.xls")]
        )

        if file:
            self.selected_file = file
            self.file_label.configure(text=file)

    def generate(self):

        if not self.selected_file:
            print("No file selected.")
            return

        rows = ExcelReader.read_first_column(self.selected_file)

        rows = ReportParser.clean(rows)

        dataframe = ReportParser.parse(rows)

        report_date = self.date_entry.get()

        output = ExcelService.build_output_dataframe(
            dataframe,
            report_date
        )

        output_folder = JournalGenerator.resolve_run_folder(report_date)

        output_path = output_folder / "Processed_Report.xlsx"

        ExcelService.save(output, output_path)

        JournalGenerator.generate(output, output_folder)

        self.clear_fields()

        self.file_label.configure(
            text=f"Saved to {output_path}"
        )

    def clear_fields(self):
        self.date_entry.delete(0, "end")

        self.selected_file = ""

        self.file_label.configure(
            text="No file selected."
    )

def select_excel_file() -> str:
    root = Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(
        title="Select Excel File",
        filetypes=[("Excel Files", "*.xlsx *.xls")]
    )

    return file_path
    
def main():

    file_path = select_excel_file()

    if not file_path:
        print("No file selected.")
        return

    rows = ExcelReader.read_first_column(file_path)

    rows = ReportParser.clean(rows)

    dataframe = ReportParser.parse(rows)

    output = ExcelService.build_output_dataframe(dataframe)

    ExcelService.save(output, "output.xlsx")
    JournalGenerator.generate(output)

    print("Excel generated successfully!")

if __name__ == "__main__":
    app = Application()
    app.mainloop()
from optparse import Values
import PySimpleGUI as sg
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import LETTER
from PyPDF2 import PdfFileWriter, PdfFileReader
from label_constants import *
from datetime import datetime
from ulc_malaria_flowcell_qc.gdrive_manager import GDriveManager


def verify_operator_ID_input(user_ID: str) -> bool:
    # Check if the user input is good
    # return if operator ID has characters in it or not
    return user_ID.strip() == ""


def luhn_checksum(serial_number):
    def digits_of(n):
        return [int(d) for d in str(n)]

    digits = digits_of(serial_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = 0
    checksum += sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d * 2))
    return checksum % 10


def verify_fc_ID(fc_ID):
    # return if it is a valid serial number or not
    return luhn_checksum(fc_ID) != 0


def verify_lot_number_input(lot_num: str) -> bool:
    # Check if they're numbers
    return lot_num.isdigit()


def verify_drop_down_input(drop_down: str) -> bool:
    # If there's a selection
    return drop_down == ""


def main():
    # log time, date (datetime.datetime)
    getDateTime = datetime.now()
    date = getDateTime.strftime("%m/%d/%Y")
    time = getDateTime.strftime("%H:%M:%S")

    sg.theme("BlueMono")  # Add a touch of color

    # All the stuff inside your window.
    layout = [
        [sg.Text("Flow cell sheet information", font=("Helvetica", 12))],
        [
            sg.Text("Consumable build guide version: ", font=("Helvetica", 12)),
            sg.Combo(["choice 1", "choice 2"], key="version"),
        ],
        [sg.Text("Operator ID: ", font=("Helvetica", 12)), sg.InputText()],
        [sg.Text("Scan QR Code: ", font=("Helvetica", 12)), sg.InputText()],
        [
            sg.Text("Acrylic Manufacturer: ", font=("Helvetica", 12)),
            sg.Combo(["Tru-Cast", "choice 2"], key="manufacturer"),
        ],
        [
            sg.Text("Coverslip Manufacturer: ", font=("Helvetica", 12)),
            sg.Combo(["Fisher", "Epredia"], key="coverslip_manufacturer"),
        ],
        [
            sg.Text("Coverslip Part Number: ", font=("Helvetica", 12)),
            sg.Combo(["12544B", "ZA0295"], key="part num"),
        ],
        [sg.Text("Coverslip Lot Number: ", font=("Helvetica", 12)), sg.InputText()],
        [
            sg.Text("Sheet Type: ", font=("Helvetica", 12)),
            sg.Combo(["Production", "R&D"], key="sheet type"),
        ],
        [sg.Text("R&D Notes: ", font=("Helvetica", 12)), sg.InputText()],
        [
            sg.Button("Save", font=("Helvetica", 12)),
            sg.Button("Cancel", font=("Helvetica", 12)),
        ],
    ]

    # Create the Window
    window = sg.Window("Flow Cell Sheet Labeling", layout)

    # Process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()

        if (
            event == sg.WIN_CLOSED or event == "Cancel"
        ):  # if user closes window or clicks cancel
            break
            # check if all the inputs are valid before closing the window
        elif verify_drop_down_input(values["version"]):
            print("Select a flowcell version.")
        elif verify_operator_ID_input(values[0]):
            print("Operator ID invalid.")
        elif verify_fc_ID(values[1]):
            print("Flowcell serial number invalid.")
        elif verify_drop_down_input(values["manufacturer"]):
            print("Select an acrylic manufacturer.")
        elif verify_drop_down_input(values["coverslip_manufacturer"]):
            print("Select an coverslip manufacturer.")    
        elif verify_drop_down_input(values["part num"]):
            print("Select a coverslip part number.")
        elif verify_lot_number_input(values[2]) == 0:
            print("Enter a valid coverslip lot number.")
        elif verify_drop_down_input(values["sheet type"]):
            print("Select a sheet type.")
        else:
            print("Serial Number From QR Code: ", values[1])

            # Print labels to PDF
            fc_id_pdf = Canvas("fc_ID.pdf", pagesize=LETTER)
            
            x_loc_pt = 31 # adjust initial x location here 30.5
            x_location = x_loc_pt * mm2pt 
            y_location = 35.0 * mm2pt
            ID = ""
            IDnum = [8, 7, 6, 5, 4, 3, 2, 1]
            alph = ["A", "B", "C", "D"]
            for i in range(8):
                if i > 0:
                    y_location += 31.9 * mm2pt
                for j in range(4):
                    if j > 0:
                        x_location += 50 * mm2pt
                    ID = values[1] + " " + alph[j] + str(IDnum[i])
                    fc_id_pdf.setFont("Helvetica", 7)
                    fc_id_pdf.drawString(x_location, y_location, ID)
                x_location = x_loc_pt * mm2pt
            fc_id_pdf.setFont("Helvetica", 7)
            # Actual bottom left corner of the paper = (x,y) = (-2.2, 1.5)
            fc_id_pdf.drawString(8 * mm2pt, 3 * mm2pt, date + ", " + time)
            fc_id_pdf.save()
            break

    window.close()

    # Add info to Google Sheet
    G = GDriveManager()
    # gets the file ID with this name
    sheet_label_file = G.get_files_by_name("Flowcell Sheet Labeling Information")[0]
    vals = [
        date,
        time,
        values["version"],
        values[0],
        values[1],
        values["manufacturer"],
        values["coverslip_manufacturer"],
        values["part num"],
        values[2],
        values["sheet type"],
        values[3],
    ]
    G.append_sheet_range(sheet_label_file["id"], vals)

    # Combine the graphic with the ID pdf
    output_file = PdfFileWriter()
    fc_graphic = PdfFileReader(open("fc_graphic.pdf", "rb")).getPage(0)
    input_file = PdfFileReader(open("fc_ID.pdf", "rb")).getPage(0)
    input_file.mergePage(fc_graphic)
    output_file.addPage(input_file)

    with open("label_with_blood_drop.pdf", "wb") as outputStream:
        output_file.write(outputStream)


if __name__ == "__main__":
    main()

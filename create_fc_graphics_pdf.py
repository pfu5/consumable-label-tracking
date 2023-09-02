from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import LETTER
from label_constants import *

# fc_id_pdf.setPageSize(landscape(LETTER)) # Change to landscape
# Create the watermark from an image
fc_graphics_pdf = Canvas("fc_graphic.pdf", pagesize=LETTER)

x_loc_pt = 17.2 # adjust initial x location here 16.5
x_blood_location = x_loc_pt * mm2pt 
y_blood_location = 28.3 * mm2pt
for i in range(8):
    if i > 0:
        y_blood_location += 31.9 * mm2pt
    for j in range(4):
        if j > 0:
            x_blood_location += 49.75 * mm2pt
        fc_graphics_pdf.drawImage(
            "blood_drop_arrow.png",
            x_blood_location,
            y_blood_location,
            width=13.5,
            height=13.5,
        )
    x_blood_location = x_loc_pt * mm2pt
fc_graphics_pdf.save()

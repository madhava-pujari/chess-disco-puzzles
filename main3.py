import chess
import chess.svg
from PIL import Image
import os
import cairosvg
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

pdfmetrics.registerFont(TTFont('Playtime', 'Playtime.ttf'))
def fen_to_png(fen, output_file):
    board = chess.Board(fen)
    svg_image = chess.svg.board(board=board, colors={
        'square light': '#e6e6fa',  # Light violet
        'square dark': '#9f8fb4',
        'margin': '#ffffff',        # White margin
        'coord': '#000000',         # Black coordinates
        'inner border': '#ffffff',  # White inner border
        'outer border': '#ffffff'   # Dark violet
    })
    cairosvg.svg2png(bytestring=svg_image.encode('utf-8'), write_to=output_file)

def create_pdf_with_images(fen_strings, output_pdf):
    c = canvas.Canvas(output_pdf, pagesize=letter)

    # Set up the title section
    c.setFillColorRGB(0.9, 0.9, 0.9)  # Light green-grey color
    c.roundRect(40, 650, 537, 115, 10, fill=True, stroke=False)
    c.setFont("Playtime", 60)  # Set font to Helvetica Bold and size 60
    c.setFillColorRGB(0.2, 0.2, 0.2)  # Dark grey color for title
    c.drawString(130, 685, "Puzzles")

    logo_path = "logo4.jpg"  # Path to your logo image
    c.drawImage(logo_path, 400, 650, width=110, height=110)

    # Add images to the PDF
    row_count = 0
    for idx, fen in enumerate(fen_strings):
        output_file = f"chess_board_{idx}.png"
        fen_to_png(fen, output_file)
        if idx % 2 == 0:
            row_count += 1
        x_position = 45 + (idx % 2) * 275
        y_position = 675 - (row_count) * 300
        c.drawImage(output_file, x_position, y_position, width=250, height=250)
        
        # Add text under the image
        if chess.Board(fen).turn == chess.WHITE:
            text = "White to move"
        else:
            text = "Black to move"
        c.setFont("Helvetica-Bold", 17)  # Set font to Helvetica Bold and size 17
        c.setFillColorRGB(0.2, 0.2, 0.2)  # Dark grey color
        text_width = c.stringWidth(text)
        text_x = x_position + 116 - text_width / 2  # Center text horizontally
        text_y = y_position - 26  # Position text below the image
        c.drawString(text_x, text_y, f"{idx+1}) {text}")  # Include numbering
        
        os.remove(output_file)  # Remove the temporary PNG file

    c.save()

# Example usage:
if __name__ == "__main__":
    df = pd.read_csv("fen_strings.csv")
    fen_strings = df['FEN'].tolist()
    for i in range(0, len(fen_strings) // 4):
        output_pdf = f"chess_puzzles_{i+1}.pdf"
        create_pdf_with_images(fen_strings[i * 4:(i + 1) * 4], output_pdf)

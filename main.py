import chess
import chess.svg
from PIL import Image
import cairosvg
import os
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color
from reportlab.lib.colors import HexColor
from bs4 import BeautifulSoup

def fen_to_png(fen, output_file):
    custom_colors = {
        'square light': '#ebecd0',  # Light violet
        'square dark': '#739552',
        'margin': '#F0F8FF',  # White margin
        'coord': '#000000',  # Black coordinates
        'inner border': '#F0F8FF',  # White inner border
        'outer border': '#F0F8FF',  # Dark violet
    }

    board = chess.Board(fen)

    svg_image = chess.svg.board(
        board=board,
        colors=custom_colors,
        borders=True,
        orientation=board.turn,
    )
    cairosvg.svg2png(bytestring=svg_image.encode('utf-8'), write_to=output_file)

def create_pdf_with_images(fen_strings, output_pdf,week_no=0):
    c = canvas.Canvas(output_pdf, pagesize=letter)
    
    
    width, height = letter
    bg_color = HexColor("#F0F8FF")  # Example: AliceBlue

    c.setFillColor(bg_color)
    c.rect(0, 0, width, height, fill=1)

    c.setFillColorRGB(0.9, 0.9, 0.9)  # Light green-grey color
    c.roundRect(40, 625, 537, 140, 10, fill=True, stroke=False)
    c.setFont("Times-Bold", 75)  # Set font to Helvetica Bold and size 60
    c.setFillColorRGB(0.2, 0.2, 0.2)  # Dark grey color for title
    c.drawString(60, 680, "Puzzles")
    week_heading=f"#{week_no*10:03}"
    c.setFont("Helvetica", 23)  # Set font to Helvetica Bold and size 60
    c.drawString(60, 650,week_heading )

    logo_path = "logo4.jpg"  # Path to your logo image
    c.drawImage(logo_path, 400, 625, width=170, height=140)

    # Add images to the PDF
    row_count = 0
    for idx, fen in enumerate(fen_strings):
        output_file = f"chess_board_{idx}.png"
        fen_to_png(fen, output_file)
        if idx % 2 == 0:
            row_count += 1
        x_position = 50 + (idx % 2) * 275
        y_position = 650 - (row_count) * 300
        c.drawImage(output_file, x_position, y_position, width=250, height=250)
        
        # Add text under the image
        if chess.Board(fen).turn == chess.WHITE:
            text = "White to Move"
        else:
            text = "Black to Move"
        c.setFont("Helvetica", 17)  # Set font to Helvetica Bold and size 17
        c.setFillColorRGB(0.2, 0.2, 0.2)  # Dark grey color
        text_width = c.stringWidth(text)
        text_x = x_position + 115 - text_width / 2  # Center text horizontally
        text_y = y_position - 26  # Position text below the image
        c.drawString(text_x, text_y, f"{idx+1}) {text}")  # Include numbering
        
        
        

        
        os.remove(output_file)  # Remove the temporary PNG file
    c.setFont("Helvetica", 14)
    vertical_text = "BRS Chess Academy©"
    print(y_position)
    x, y = 290,200   # Position for the vertical text
    c.translate(x, y) 
    c.rotate(270)  # Rotate the canvas by 90 degrees
    c.drawString(0, 0, vertical_text)  # Draw the string at the rotated position

    c.save()

# Example usage:
if __name__ == "__main__":
    df = pd.read_csv("fen_strings.csv")
    fen_strings = df['FEN'].tolist()
    week_no=int(input("intial week number: "))
    for i in range(0, len(fen_strings) // 4):
        
        output_pdf = f"Puzzle_#{week_no*10:03}.pdf"
        create_pdf_with_images(fen_strings[i * 4:(i + 1) * 4], output_pdf,week_no)
        week_no+=1
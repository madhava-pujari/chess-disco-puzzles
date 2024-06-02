import chess
import chess.svg
from PIL import Image
import os
import cairosvg
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color

def fen_to_png(fen, output_file):
    board = chess.Board(fen)
    svg_image = chess.svg.board(board=board)
    cairosvg.svg2png(bytestring=svg_image.encode('utf-8'), write_to=output_file)

def create_pdf_with_images(fen_strings, output_pdf):
    c = canvas.Canvas(output_pdf, pagesize=letter)


    logo_path = "logo5.jpg"  # Path to your logo image
    c.drawImage(logo_path, 255, 50, width=100, height=100)

    # c.setFillColorRGB(0.9, 0.9, 0.9)

    # # Draw a rectangle over the image
    # c.rect(500, 640, 100, 100, fill=True,stroke=False)
    

    # Add images to the PDF
    row_count = 0
    for idx, fen in enumerate(fen_strings):
        print(idx)
        output_file = f"chess_board_daily{idx}.png"
        fen_to_png(fen, output_file)
        if idx % 3 == 0:
            row_count += 1
        x_position = 48 + (idx % 3) * 175
        y_position = 800 - (row_count) * 200
        
        c.drawImage(output_file, x_position, y_position, width=150, height=150)
        
        # Add text under the image
        if chess.Board(fen).turn == chess.WHITE:
            text = "White to move"
        else:
            text = "Black to move"
        c.setFont("Helvetica-Bold", 14)  # Set font to Helvetica Bold and size 17
        c.setFillColorRGB(0.2, 0.2, 0.2)  # Dark grey color
        text_width = c.stringWidth(text)
        text_x = x_position + 50 - text_width / 3  # Center text horizontally
        text_y = y_position - 26  # Position text below the image
        c.drawString(text_x, text_y, f"{idx+1}) {text}")  # Include numbering
        print(text_x,text_y)
        os.remove(output_file)  # Remove the temporary PNG file

    c.save()


# Example usage:
if __name__ == "__main__":
    df = pd.read_csv("fen_strings_daily.csv")
    fen_strings = df['FEN'].tolist()
    print(len(fen_strings))
    for i in range(0,len(fen_strings)//9):
        output_pdf = f"chess_puzzles_daily_{i+1}.pdf"
        create_pdf_with_images(fen_strings[i*9:(i+1)*9], output_pdf)


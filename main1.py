import chess
import chess.svg
from PIL import Image
import os
import cairosvg
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color
import csv


def sheet_code_gen(topic, num: int):
    first_letters = ''.join(word[0].upper() for word in topic.split())
    three_digit_number = str(num).zfill(3)
    return first_letters + three_digit_number


def fen_to_png(fen, output_file):
    custom_colors = {
        'square light': '#e6e6fa',  # Light violet
        'square dark': '#9f8fb4',
        'margin': '#ffffff',  # White margin
        'coord': '#000000',  # Black coordinates
        'inner border': '#ffffff',  # White inner border
        'outer border': '#ffffff',  # Dark violet
    }

    board = chess.Board(fen)

    svg_image = chess.svg.board(
        board=board,
        colors=custom_colors,
        borders=True,
        orientation=board.turn,
    )
    cairosvg.svg2png(bytestring=svg_image.encode('utf-8'), write_to=output_file)


def create_pdf_with_images(fen_strings, output_pdf, i, topic):
    c = canvas.Canvas(output_pdf, pagesize=letter)
    varu = sheet_code_gen(topic, i + 1)

    c.drawString(50, 750, "Name: ___________________________")
    c.drawString(50, 720, "Date: ____________________________")
    c.drawString(50, 690, f"Topic: {topic}")
    c.drawString(50, 660, f"Code: {varu}")

    logo_path = "logo5.jpg"  # Path to your logo image
    c.drawImage(logo_path, 390, 604, width=180, height=180)

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
        x_position = 30 + (idx % 3) * 190
        y_position = 660 - (row_count) * 200

        c.drawImage(output_file, x_position, y_position, width=170, height=170)

        # Add text under the image
        if chess.Board(fen).turn == chess.WHITE:
            text = "White to move"
        else:
            text = "Black to move"
        c.setFont("Helvetica", 14)  # Set font to Helvetica Bold and size 17
        c.setFillColorRGB(0.2, 0.2, 0.2)  # Dark grey color
        text_width = c.stringWidth(text)
        text_x = x_position + 60 - text_width / 3  # Center text horizontally
        text_y = y_position - 15  # Position text below the image
        c.drawString(text_x, text_y, f"{idx+1}) {text}")  # Include numbering
        print(text_x, text_y)
        os.remove(output_file)  # Remove the temporary PNG file

    c.save()


# Example usage:
if __name__ == "__main__":
    df = pd.read_csv("fen_strings_daily.csv")
    first_column_name = next(csv.reader(open('fen_strings_daily.csv')))[0]
    fen_strings = df['FEN'].tolist()
    print(len(fen_strings))
    TOPIC = "Mate in two"
    for i in range(0, len(fen_strings) // 9):
        output_pdf = f"chess_puzzles_{TOPIC}_{i+1}.pdf"
        create_pdf_with_images(fen_strings[i * 9 : (i + 1) * 9], output_pdf, i, TOPIC)

import chess
import chess.svg
from PIL import Image
import cairosvg
import os
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color
from bs4 import BeautifulSoup

def fen_to_png(fen, output_file, piece_set_path):
    custom_colors = {
        'square light': '#e6e6fa',  # Light violet
        'square dark': '#9f8fb4',
        'margin': '#ffffff',        # White margin
        'coord': '#000000',         # Black coordinates
        'inner border': '#ffffff',  # White inner border
        'outer border': '#ffffff'   # Dark violet
    }
    
    board = chess.Board(fen)
  
    svg_image = chess.svg.board(board=board, colors=custom_colors, borders=True,orientation=board.turn, )

    # Parse the SVG using BeautifulSoup
    soup = BeautifulSoup(svg_image, 'xml')

    piece_names = ['k', 'q', 'r', 'b', 'n', 'p']
    colors = ['w', 'b']
    
    for color in colors:
        for piece in piece_names:
            piece_key = f"{color}{piece}"
            custom_piece_path = os.path.join(piece_set_path, f"{piece_key}.svg")
            with open(custom_piece_path, "r") as f:
                custom_piece_svg = f.read()

            # Find all use elements referring to this piece
            use_elements = soup.find_all("use", {"href": f"#{piece_key}"})
            for use_element in use_elements:
                # Replace use element with custom SVG
                custom_piece_soup = BeautifulSoup(custom_piece_svg, 'xml')
                for svg_elem in custom_piece_soup.find_all('svg'):
                    svg_elem['x'] = use_element['x']
                    svg_elem['y'] = use_element['y']
                    use_element.replace_with(svg_elem)

    # Convert the modified SVG back to a string
    modified_svg = str(soup)

    cairosvg.svg2png(bytestring=modified_svg.encode('utf-8'), write_to=output_file)

def create_pdf_with_images(fen_strings, output_pdf,week_no=0):
    c = canvas.Canvas(output_pdf, pagesize=letter)

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
        fen_to_png(fen, output_file, piece_set_path="images/kosal")
        if idx % 2 == 0:
            row_count += 1
        x_position = 45 + (idx % 2) * 275
        y_position = 650 - (row_count) * 300
        c.drawImage(output_file, x_position, y_position, width=250, height=250)
        
        # Add text under the image
        if chess.Board(fen).turn == chess.WHITE:
            text = "White to move"
        else:
            text = "Black to move"
        c.setFont("Helvetica-Bold", 17)  # Set font to Helvetica Bold and size 17
        c.setFillColorRGB(0.2, 0.2, 0.2)  # Dark grey color
        text_width = c.stringWidth(text)
        text_x = x_position + 125 - text_width / 2  # Center text horizontally
        text_y = y_position - 26  # Position text below the image
        c.drawString(text_x, text_y, f"{idx+1}) {text}")  # Include numbering
        
        os.remove(output_file)  # Remove the temporary PNG file

    c.save()

# Example usage:
if __name__ == "__main__":
    df = pd.read_csv("fen_strings.csv")
    fen_strings = df['FEN'].tolist()
    week_no=int(input("intial week number: "))
    for i in range(0, len(fen_strings) // 4):
        output_pdf = f"chess_puzzles_{i + 1}.pdf"
        create_pdf_with_images(fen_strings[i * 4:(i + 1) * 4], output_pdf,week_no=0)

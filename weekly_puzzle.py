import random

import chess
import chess.svg
from PIL import Image
import cairosvg
import os
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color
from reportlab.lib.colors import HexColor
from bs4 import BeautifulSoup

from db_crud import get_puzzles_by_theme_and_rating


def fen_to_png(fen, output_file):
    custom_colors = {
        'square light': '#e6e6fa',  # Light violet
        'square dark': '#9f8fb4',
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







NINE_LAYOUT=9
SIX_LAYOUT=6
FOUR_LAYOUT=4
level_partition ={
    "level_1": {
        "level": 1,
        "min_rating": 0,
        "max_rating": 899,
    },
    "level_2": {
        "level": 2,
        "min_rating":900,
        "max_rating":1299,
    },
    "level_3": {
        "level": 3,
        "min_rating": 1300,
        "max_rating": 1699,
    },
    "level_4": {
        "level": 4,
        "min_rating": 1700,
        "max_rating": 2199,
    },
    "level_5": {
        "level": 5,
        "min_rating": 2200,
        "max_rating": 2700,
    }
}



def create_weekly_puzzle_sheet(puzzle_list, folder_name, sheet_code, ):

    os.makedirs(folder_name, exist_ok=True)
    output_pdf = os.path.join(folder_name, f"Weekly_puzzle_{sheet_code}.pdf")
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
    c.setFont("Helvetica", 23)  # Set font to Helvetica Bold and size 60
    c.drawString(60, 650, sheet_code)

    logo_path = "logo4.jpg"  # Path to your logo image
    c.drawImage(logo_path, 400, 625, width=170, height=140)
    # Add images to the PDF
    row_count = 0
    for idx, individual_puzzle in enumerate(puzzle_list):
        output_file = f"chess_board_{idx}.png"
        fen_to_png(individual_puzzle['FEN'], output_file)
        if idx % 2 == 0:
            row_count += 1
        x_position = 50 + (idx % 2) * 275
        y_position = 650 - (row_count) * 300
        c.drawImage(output_file, x_position, y_position, width=250, height=250)

        # Add text under the image
        if chess.Board(individual_puzzle['FEN']).turn == chess.WHITE:
            text = "White to Move"
        else:
            text = "Black to Move"
        c.setFont("Helvetica", 17)  # Set font to Helvetica Bold and size 17
        c.setFillColorRGB(0.2, 0.2, 0.2)  # Dark grey color
        text_width = c.stringWidth(text)
        text_x = x_position + 115 - text_width / 2  # Center text horizontally
        text_y = y_position - 26  # Position text below the image
        c.drawString(text_x, text_y, f"{idx + 1}) {text}")  # Include numbering

        os.remove(output_file)  # Remove the temporary PNG file
    c.setFont("Helvetica", 14)
    vertical_text = "BRS Chess Academy©"
    print(y_position)
    x, y = 290, 200  # Position for the vertical text
    c.translate(x, y)
    c.rotate(270)  # Rotate the canvas by 90 degrees
    c.drawString(0, 0, vertical_text)  # Draw the string at the rotated position
    c.save()

def create_answer_pdfs_with_header(data,folder_name, topic='Weekly_puzzles'):
    """Generates PDFs from a nested list of strings while ensuring each inner list stays on the same page.

    Args:
        data (list of list of str): The nested list of strings.
        topic (str): The topic string for the header.
        output_prefix (str): Prefix for output PDF filenames.
    """

    def draw_header(c, topic):
        """Draws the header on the current canvas."""
        # Get letter page dimensions
        width, height = letter

        # Background color (optional)
        # bg_color = HexColor("#F0F8FF")
        # c.setFillColor(bg_color)
        # c.rect(0, 0, width, height, fill=1)

        # Logo
        logo_path = "logo5.jpg"
        c.drawImage(logo_path, 390, 604, width=180, height=180)

        # Header Text
        c.setFont("Helvetica", 20)
        c.drawString(50, 750, f"Solutions--")
        c.drawString(50, 725, f"Topic: {topic}")

    # Constants for positioning
    margin = inch / 2
    line_height = 14
    max_lines_per_page = 40  # Adjust based on the content and page size

    # Page counter for multiple PDFs
    pdf_counter = 1
    os.makedirs(folder_name, exist_ok=True)
    output_pdf_name = os.path.join(folder_name, f"{topic}_solutions.pdf")
    c = canvas.Canvas(output_pdf_name, pagesize=letter)
    heading_height = 16

    draw_header(c, topic)

    # Current y-coordinate to write content
    y = 700  # Initial y-position under the header
    spacing = 16
    for index,(key,value) in enumerate(data.items()):
        # Calculate the block height
        block_height = len(value) * line_height + heading_height + spacing

        # If the block won't fit on the current page, create a new page
        if y - block_height < margin:
            c.showPage()
            draw_header(c, topic)
            y = 700  # Reset y position for the new page

        # Write each line in the current block
        c.setFont("Helvetica", 14)
        y -= spacing
        c.drawString(margin, y, key)
        y-= heading_height
        c.setFont("Helvetica", 12)

        for idx,line in enumerate(value):
            ans_str =", ".join(line["Moves"])
            fmt_ans_str =f"{idx}:({line["PuzzleId"]}) {ans_str}"
            c.drawString(margin, y, fmt_ans_str )
            y -= line_height

    # Save the current PDF
    c.save()
    print(f"PDF saved: {output_pdf_name}")



level_wise_puzzle_partition = {}

level_wise_puzzle_topic_partition = {
    "level_1": ["pin", "mateIn1", "fork", "skewer", "discoveredAttack", "mateIn2",
                 "backRankMate", "doubleCheck"],
    "level_2": ["capturingDefender","promotion","pin","mateIn1","fork","skewer","discoveredAttack","mateIn2","smotheredMate","backRankMate","doubleCheck"],
    "level_3": ["promotion","pin","fork","skewer","discoveredAttack","mateIn2","smotheredMate","backRankMate","doubleCheck"],
    "level_4": ["capturingDefender","mateIn4","promotion","trappedPiece","xRayAttack","mateIn3"],
}
weekly_puzzle_distribution = ["level_1","level_2","level_3","level_4"]


def weekly_puzzle_sheet_code_gen(week_no: int = 1):
    counter = week_no
    while True:
        if counter < 100:
            code = str(counter).zfill(3)
        elif counter < 1000:
            code = str(counter).zfill(4)
        else:
            code = str(counter).zfill(5)
        return '#' + code
        counter += 1

def get_weekly_puzzles_list(nbsheets=1, intial_week=1):
    master_puzzle_list = dict()
    for idx,(level,topic_list) in enumerate(level_wise_puzzle_topic_partition.items()):
        level_wise_puzzle_partition[level]=[]

        for topic in topic_list:

            result = get_puzzles_by_theme_and_rating(themes=[topic], min_rating=level_partition[level]["min_rating"],
                                                     limit=50, max_rating=level_partition[level]["max_rating"],
                                                     nb_plays_lt=2000)
            level_wise_puzzle_partition[level].extend(result)


    for i in range(intial_week, intial_week + nbsheets+1):
        sheet_code = weekly_puzzle_sheet_code_gen(i)
        temp_list = list()
        for idx, (value) in enumerate(weekly_puzzle_distribution):
            picked_item = random.choice(level_wise_puzzle_partition[value])  # Pick a random item
            print(f"Picked: {picked_item}")
            level_wise_puzzle_partition[value].remove(picked_item)  # Remove the picked item
            temp_list.append(picked_item)
        master_puzzle_list[sheet_code] = temp_list
    return master_puzzle_list

if __name__ == "__main__":
    nbsheets = int(input("nb of sheets: "))
    intial_week = int(input("initialWeek: "))
    master_puzzle_dict = get_weekly_puzzles_list(nbsheets=nbsheets,intial_week=intial_week)
    folder_name = "Weekly_puzzles"

    for index2, (key2, value2) in enumerate(master_puzzle_dict.items()):
        create_weekly_puzzle_sheet(puzzle_list=value2,folder_name=folder_name,sheet_code=key2)
    create_answer_pdfs_with_header(data=master_puzzle_dict,folder_name=folder_name)


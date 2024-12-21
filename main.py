from db_crud import *
import chess
import chess.svg
import os
import cairosvg
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from puzzle_theme import puzzle_dict

NINE_LAYOUT=9
SIX_LAYOUT=6
FOUR_LAYOUT=4
level_partition ={
    "level_0": {
        "level": 0,
        "min_rating": 0,
        "max_rating": 749,
    },
    "level_1": {
        "level": 1,
        "min_rating":750,
        "max_rating":1099,
    },
    "level_2": {
        "level": 2,
        "min_rating": 1100,
        "max_rating": 1399,
    },
    "level_3": {
        "level": 3,
        "min_rating": 1400,
        "max_rating": 1699,
    },
    "level_4": {
        "level": 4,
        "min_rating": 1700,
        "max_rating": 2400,
    }
}

def sheet_code_gen(topic:str,level:int):
    counter = 1
    while True:
        first_letters = ''.join(word[0].upper() for word in topic.split())
        three_digit_number = str(counter).zfill(3)
        yield '#'+ 'V1L' + str(level) + first_letters + three_digit_number
        counter += 1

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


def create_puzzle_sheet(puzzle_list, output_pdf, topic, sheet_code):

    c = canvas.Canvas(output_pdf, pagesize=letter)
    
    width, height = letter
    bg_color = HexColor("#F0F8FF")  # Example: AliceBlue
    c.setFillColor(bg_color)
    c.rect(0, 0, width, height, fill=1)
    

    logo_path = "logo5.jpg"  # Path to your logo image
    c.drawImage(logo_path, 390, 604, width=180, height=180)


    # Add images to the PDF
    row_count = 0
    for idx, individual_puzzle in enumerate(puzzle_list):
        print(idx)
        output_file = f"chess_board_daily{idx}.png"
        fen_to_png(individual_puzzle["FEN"], output_file)
        if idx % 3 == 0:
            row_count += 1
        x_position = 30 + (idx % 3) * 190
        y_position = 660 - (row_count) * 200

        c.drawImage(output_file, x_position, y_position, width=170, height=170)

        # Text under puzzle
        if chess.Board(individual_puzzle["FEN"]).turn == chess.WHITE:
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
        os.remove(output_file) 

    c.drawString(50, 750, "Name: ___________________________")
    c.drawString(50, 720, "Date: ____________________________")
    c.drawString(50, 690, f"Topic: {topic}")
    c.drawString(50, 660, f"Code: {sheet_code}")

    # Watermark
    c.setFont("Helvetica", 11)
    vertical_text = "BRS Chess Academy©"
    print(y_position)
    x, y = 195,180   
    c.translate(x, y) 
    c.rotate(270) 
    c.drawString(0, 0, vertical_text)   

    c.save()


def create_answer_pdfs_with_header(data, topic, level):
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
    output_pdf_name = f"{topic}_solutions_lvl_{level}.pdf"
    c = canvas.Canvas(output_pdf_name, pagesize=letter)
    heading_height = 16

    draw_header(c, topic)

    # Current y-coordinate to write content
    y = 700  # Initial y-position under the header

    for index,(key,value) in enumerate(data):
        # Calculate the block height
        block_height = len(value) * line_height + heading_height

        # If the block won't fit on the current page, create a new page
        if y - block_height < margin:
            c.showPage()
            draw_header(c, topic)
            y = 700  # Reset y position for the new page

        # Write each line in the current block
        c.setFont("Helvetica", 14)
        c.drawString(margin, y, line["FEN"])
        y-= heading_height
        c.setFont("Helvetica", 12)

        for line in value:
            c.drawString(margin, y, line["FEN"])
            y -= line_height

    # Save the current PDF
    c.save()
    print(f"PDF saved: {output_pdf_name}")


def slice_puzzle_list(master_puzzle_list, layout_type,topic,level):

    result = {}
    code_gen = sheet_code_gen(topic=topic,level=level)

    for idx in range(0, len(master_puzzle_list), layout_type):
        result[next(code_gen)] = master_puzzle_list[idx:idx + layout_type]

    return result
# Example usage:

if __name__ == "__main__":
    theme_name = input("name of the theme: ")
    theme_data = puzzle_dict[theme_name]

    for index,(key,value) in enumerate(level_partition):
        layout_type = int(input("should i use 9 layout for this level? (y/n)"))
        level_partition[key]['sheet_count'] =int(input('number of sheets for this level? '))

        if layout_type == 9:
            level_partition[key]['layout']=NINE_LAYOUT
        elif layout_type == 6:
            level_partition[key]['layout'] = SIX_LAYOUT
        elif layout_type == 4:
            level_partition[key]['layout'] = FOUR_LAYOUT
        else:
            print('no such layout for now')


    for index,(key,value) in enumerate(level_partition):

        result = get_puzzles_by_theme_and_rating(themes=[theme_data["theme_name"],],min_rating=value['min_rating'],max_rating=value['max_rating'], limit=value['sheet_count']*value['layout'])

        master_puzzle_dict = slice_puzzle_list(master_puzzle_list=result,layout_type= NINE_LAYOUT,topic= theme_data["theme_name"],level= value['level'])
        print(master_puzzle_dict)
        for index2, (key2, value2) in enumerate(master_puzzle_dict):
            output_pdf = f"{theme_name_snake_case}_lvl{level}_code{key}.pdf"
            create_puzzle_sheet(value, theme_data)
        create_answer_pdfs_with_header(master_puzzle_dict,theme_name_snake_case,level)


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
    # "level_1": {
    #     "level": 1,
    #     "min_rating":750,
    #     "max_rating":1099,
    # },
    # "level_2": {
    #     "level": 2,
    #     "min_rating": 1100,
    #     "max_rating": 1399,
    # },
    # "level_3": {
    #     "level": 3,
    #     "min_rating": 1400,
    #     "max_rating": 1699,
    # },
    # "level_4": {
    #     "level": 4,
    #     "min_rating": 1700,
    #     "max_rating": 2400,
    # }
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


def create_puzzle_sheet(puzzle_list, topic_name,level,folder_name, sheet_code, layout_type):
    """
    Create a PDF sheet of chess puzzles with different layout options.
    layout_type: int (4, 6, or 9) - number of puzzles per sheet determining the layout
    """
    if layout_type not in [4, 6, 9]:
        raise ValueError("layout_type must be 4, 6, or 9")
    os.makedirs(folder_name, exist_ok=True)

    output_pdf = os.path.join(folder_name, f"{topic_name}_lvl{level}_code{sheet_code}.pdf")

    c = canvas.Canvas(output_pdf, pagesize=letter)
    width, height = letter

    # Set background
    bg_color = HexColor("#F0F8FF")
    c.setFillColor(bg_color)
    c.rect(0, 0, width, height, fill=1)

    # Draw logo
    logo_path = "logo5-Photoroom.png"
    c.drawImage(logo_path, 390, 604, width=180, height=180)

    # Layout configurations
    layout_configs = {
        4: {
            "rows": 2,
            "cols": 2,
            "x_spacing": 250,
            "y_spacing": 250,
            "img_size": 200,
            "watermark_x": 252,
            "watermark_y": 280
        },
        6: {
            "rows": 2,
            "cols": 3,
            "x_spacing": 200,
            "y_spacing": 270,
            "img_size": 190,
            "watermark_x": 198,
            "watermark_y": 280
        },
        9: {
            "rows": 3,
            "cols": 3,
            "x_spacing": 190,
            "y_spacing": 190,
            "img_size": 170,
            "watermark_x": 195,
            "watermark_y": 180
        }
    }

    config = layout_configs[layout_type]

    # Add images to the PDF
    for idx, (individual_puzzle) in enumerate(puzzle_list):
        print(idx)
        output_file = f"chess_board_daily{idx}.png"
        fen_to_png(individual_puzzle["FEN"], output_file)

        row = idx // config["cols"]
        col = idx % config["cols"]

        # Adjust starting x position based on layout type for better centering
        if layout_type == 4:
            start_y = 300
            start_x = 30
        elif layout_type == 6:
            start_x = 15
            start_y = 370
        else:
            start_y = 420
            start_x = 30

        x_position = start_x + col * config["x_spacing"]
        y_position = start_y - row * config["y_spacing"]

        c.drawImage(output_file, x_position, y_position,
                    width=config["img_size"],
                    height=config["img_size"])

        # Text under puzzle
        if chess.Board(individual_puzzle["FEN"]).turn == chess.WHITE:
            text = "White to move"
        else:
            text = "Black to move"

        c.setFont("Helvetica", 14)
        c.setFillColorRGB(0.2, 0.2, 0.2)
        text_width = c.stringWidth(text)
        text_x = x_position + (config["img_size"] / 2) - text_width / 2  # Center text horizontally
        text_y = y_position - 15
        c.drawString(text_x, text_y, f"{idx + 1}) {text}")

        os.remove(output_file)

    # Header information
    c.drawString(50, 750, "Name: ___________________________")
    c.drawString(50, 720, "Date: ____________________________")
    c.drawString(50, 690, f"Topic: {topic_name}")
    c.drawString(50, 660, f"Code: {sheet_code}")

    # Save current graphics state
    c.saveState()

    # Watermark with position based on layout
    c.setFont("Helvetica", 11)
    vertical_text = "BRS Chess Academy©"
    x, y = config["watermark_x"], config["watermark_y"]
    c.translate(x, y)
    c.rotate(270)
    c.drawString(0, 0, vertical_text)

    # Restore graphics state
    c.restoreState()

    c.save()

def create_answer_pdfs_with_header(data,folder_name, topic, level):
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
    output_pdf_name = os.path.join(folder_name, f"{topic}_solutions_lvl_{level}.pdf")
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

    for index,(key,value) in enumerate(level_partition.items()):
        layout_type = int(input("number of puzzles per sheet? "))
        level_partition[key]['sheet_count'] =int(input('number of sheets for this level? '))

        if layout_type == 9:
            level_partition[key]['layout']=NINE_LAYOUT
        elif layout_type == 6:
            level_partition[key]['layout'] = SIX_LAYOUT
        elif layout_type == 4:
            level_partition[key]['layout'] = FOUR_LAYOUT
        else:
            print('no such layout for now')


    for index,(key,value) in enumerate(level_partition.items()):

        result = get_puzzles_by_theme_and_rating(themes=[theme_data["theme_name"],],min_rating=value['min_rating'],max_rating=value['max_rating'], limit=value['sheet_count']*value['layout'])

        master_puzzle_dict = slice_puzzle_list(master_puzzle_list=result,layout_type= value['layout'],topic= theme_data["complete_theme_name"],level= value['level'])
        folder_name = f"{key}_{theme_data["theme_name"]}"
        print(master_puzzle_dict)
        for index2, (key2, value2) in enumerate(master_puzzle_dict.items()):
            create_puzzle_sheet(puzzle_list=value2,folder_name=folder_name,sheet_code=key2,level=value['level'],layout_type=value['layout'],topic_name=theme_data["theme_name"])
        create_answer_pdfs_with_header(data=master_puzzle_dict,folder_name=folder_name,topic=theme_data['theme_name'],level=value['level'])


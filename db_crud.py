import chess
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker

import pandas as pd
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Create SQLAlchemy Base and define the model
Base = declarative_base()


class ChessPuzzle(Base):
    __tablename__ = 'chess_puzzles'
    PuzzleId = Column(String(10), primary_key=True, name='puzzleid')
    FEN = Column(String(100), name='fen')
    Moves = Column(String(255), name='moves')
    Rating = Column(Integer, name='rating')
    RatingDeviation = Column(Integer, name='ratingdeviation')
    Popularity = Column(Integer, name='popularity')
    NbPlays = Column(Integer, name='nbplays')
    Themes = Column(String(255), name='themes')
    GameUrl = Column(String(255), name='gameurl')
    OpeningTags = Column(String(255), name='openingtags')


def get_db_connection_string(
    username='master_user',
    password='master_password',
    host='localhost',
    port='5432',
    database='Chess',
):
    """
    Generate PostgreSQL connection string with default local settings

    :param username: PostgreSQL username
    :param password: PostgreSQL password
    :param host: Database host
    :param port: Database port
    :param database: Database name
    :return: SQLAlchemy connection string
    """
    return f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}'

def get_puzzles_by_theme_and_rating(
    themes=None, 
    min_rating=None, 
    max_rating=None, 
    limit=None,
    exclude_puzzles=None
):
    """
    Retrieve chess puzzles based on themes and rating range.
    
    Parameters:
    - themes: List of themes to filter by (case-insensitive partial match)
    - min_rating: Minimum puzzle rating
    - max_rating: Maximum puzzle rating
    - limit: Maximum number of puzzles to retrieve
    - exclude_puzzles: List of puzzle IDs to exclude
    
    Returns:
    List of ChessPuzzle objects matching the criteria
    """
    connection_str = get_db_connection_string()
    
    engine = create_engine(connection_str,echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    query = session.query(ChessPuzzle)
    
    if themes:
        theme_conditions = []
        for theme in themes:
            theme_conditions.append(ChessPuzzle.Themes.ilike(f'%{theme}%'))
        query = query.filter(or_(*theme_conditions))
    
    if min_rating is not None:
        query = query.filter(ChessPuzzle.Rating >= min_rating)
    
    if max_rating is not None:
        query = query.filter(ChessPuzzle.Rating <= max_rating)
    
    if exclude_puzzles:
        query = query.filter(~ChessPuzzle.PuzzleId.in_(exclude_puzzles))

    query = query.order_by(ChessPuzzle.NbPlays.desc())
    if  limit:
        query = query.limit(limit)

    puzzles = query.all()
    return [
        {
            'PuzzleId': puzzle.PuzzleId,
            'FEN': process_first_move(puzzle.FEN, puzzle.Moves)['fen'],
            'Moves': process_first_move(puzzle.FEN, puzzle.Moves)['san_moves'],
            'Rating': puzzle.Rating,
            'RatingDeviation': puzzle.RatingDeviation,
            'Popularity': puzzle.Popularity,
            'NbPlays': puzzle.NbPlays,
            'Themes': puzzle.Themes,
            'GameUrl': puzzle.GameUrl,
            'OpeningTags': puzzle.OpeningTags
        }
        for puzzle in puzzles
    ]


import chess

def process_first_move(initial_fen, uci_moves):
    """
    Process the first move from a list of UCI moves and return updated FEN and moves in SAN notation,
    excluding the first move from the input.

    Parameters:
    - initial_fen: Starting position FEN string
    - uci_moves: String of moves in UCI notation, separated by spaces

    Returns:
    Dict containing:
    - 'fen': Updated FEN after the first move
    - 'san_moves': List of moves in Standard Algebraic Notation (SAN), excluding the first move
    """
    # Create a board from the initial FEN
    board = chess.Board(initial_fen)

    # Convert UCI moves string to a list
    uci_moves = uci_moves.split()

    # Stores SAN moves for tracking
    san_moves = []

    # Process the first move if moves are provided
    if uci_moves:
        # Convert the first UCI move to a chess.Move object
        first_move = chess.Move.from_uci(uci_moves[0])

        # Validate and apply the first move
        if first_move in board.legal_moves:
            board.push(first_move)
            result_fen =board.fen()
        else:
            # Return initial state if the first move is illegal
            return {
                'fen': initial_fen,
                'san_moves': [],
                'error': f'Illegal move: {uci_moves[0]}'
            }

    # Process the remaining moves and convert them to SAN
    for move_uci in uci_moves[1:]:
        move = chess.Move.from_uci(move_uci)
        if move in board.legal_moves:
            san_moves.append(board.san(move))
            board.push(move)
        else:
            return {
                'fen': board.fen(),
                'san_moves': san_moves,
                'error': f'Illegal move: {move_uci}'
            }

    return {
        'fen': result_fen,
        'san_moves': san_moves
    }




# Utility function to parse themes
def parse_themes(themes_string):
    """
    Parse the themes string into a list of themes.
    
    Parameters:
    - themes_string: Comma or space-separated themes string
    
    Returns:
    List of cleaned themes
    """
    if not themes_string:
        return []
    
    # Split by comma or space, remove extra whitespace, convert to lowercase
    return [theme.strip().lower() for theme in themes_string.replace(',', ' ').split() if theme.strip()]

# Additional helper function for advanced filtering
def filter_puzzles_by_opening(
    session, 
    opening_tags=None, 
    themes=None, 
    min_rating=None, 
    max_rating=None, 
    limit=100
):
    """
    Advanced puzzle filtering with opening tags support
    
    Parameters:
    - session: SQLAlchemy session
    - opening_tags: List of opening tags to filter by
    - themes: List of themes to filter by
    - min_rating: Minimum puzzle rating
    - max_rating: Maximum puzzle rating
    - limit: Maximum number of puzzles to retrieve
    
    Returns:
    List of ChessPuzzle objects matching the criteria
    """
    query = session.query(ChessPuzzle)
    
    # Filter by opening tags
    if opening_tags:
        opening_conditions = []
        for tag in opening_tags:
            opening_conditions.append(ChessPuzzle.OpeningTags.ilike(f'%{tag}%'))
        query = query.filter(or_(*opening_conditions))
    
    # Reuse theme filtering logic
    if themes:
        theme_conditions = []
        for theme in themes:
            theme_conditions.append(ChessPuzzle.Themes.ilike(f'%{theme}%'))
        query = query.filter(or_(*theme_conditions))
    
    # Rating filters
    if min_rating is not None:
        query = query.filter(ChessPuzzle.Rating >= min_rating)
    
    if max_rating is not None:
        query = query.filter(ChessPuzzle.Rating <= max_rating)
    
    # Limit results
    query = query.limit(limit)
    
    return query.all()

# Add a simple puzzle composition checker
def check_puzzle_composition(puzzle):
    """
    Basic validation of a chess puzzle's data
    
    Parameters:
    - puzzle: ChessPuzzle object
    
    Returns:
    Dict with composition details and potential issues
    """
    result = {
        'is_valid': True,
        'issues': []
    }
    
    # Check FEN
    if not puzzle.FEN or len(puzzle.FEN.split()) < 6:
        result['is_valid'] = False
        result['issues'].append('Invalid FEN string')
    
    # Check Moves
    if not puzzle.Moves:
        result['is_valid'] = False
        result['issues'].append('No moves provided')
    
    # Check Rating
    if puzzle.Rating is None or puzzle.Rating < 0:
        result['issues'].append('Unusual rating')
    
    # Check Themes
    if not puzzle.Themes:
        result['issues'].append('No themes specified')
    
    return result





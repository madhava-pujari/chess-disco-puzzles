import pandas as pd

def write_fen_to_csv(fen_strings, filename):
    df = pd.DataFrame({'FEN': fen_strings})
    df.to_csv(filename, index=False)

# Example usage:
if __name__ == "__main__":
    fen_strings = [
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5Q2/PPPP1PPP/RNB1K1NR b KQkq - 0 4",
    "rnbqkbnr/pppp1ppp/8/4p3/3P4/8/PPP1PPPP/RNBQKBNR w KQkq - 0 3",
    "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2",
    "rnbqkbnr/ppp1pppp/3p4/8/3PP3/8/PPP2PPP/RNBQKBNR b KQkq - 0 3",
    "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5Q2/PPPP1PPP/RNB1K1NR b KQkq - 0 4",
    "rnbqkb1r/pppp1ppp/5n2/4p3/2B1P3/5Q2/PPPP1PPP/RNB1K1NR b KQkq - 0 4",
    "rnbqkbnr/pppp1ppp/8/4p3/3P4/8/PPP1PPPP/RNBQKBN1 w Qkq - 0 3",
    "rnbqkbnr/pppp1ppp/8/8/4p3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2",
    "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
    "rnbqkbnr/ppp1pppp/3p4/8/3PP3/8/PPP2PPP/RNBQKBNR b KQkq - 0 3",
    "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5Q2/PPPP1PPP/RNB1K1NR b KQkq - 0 4",
    "rnbqkb1r/pppp1ppp/5n2/4p3/2B1P3/5Q2/PPPP1PPP/RNB1K1NR b KQkq - 0 4",
    "rnbqkbnr/pppp1ppp/4p3/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2",
    "rnbqkb1r/pppp1ppp/5n2/4p3/2B1P3/5Q2/PPPP1PPP/RNB1K1NR b KQkq - 0 4",
    "rnbqkb1r/pppp1ppp/5n2/4p3/2B1P3/5Q2/PPPP1PPP/RNB1K1NR b KQkq - 0 4",
    "rnbqkbnr/pppp1ppp/8/8/4p3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2",
    "rnbqkb1r/pppp1ppp/5n2/4p3/2B1P3/5Q2/PPPP1PPP/RNB1K1NR b KQkq - 0 4"
]

    filename = 'fen_strings_daily.csv'
    write_fen_to_csv(fen_strings, filename)
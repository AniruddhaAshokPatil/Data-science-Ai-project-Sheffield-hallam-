import asyncio

from src.simulator.http_streamer import stream_over_http
from src.simulator.load_csv_streamer import load_transactions_from_csv
from src.simulator.random_transactions import stream_random_transactions
from src.simulator.websocket_streamer import stream_over_websocket


def start_http():
    # I load the sample rows in this wrapper so each mode keeps its own clear entry point.
    dataframe = load_transactions_from_csv(50)
    stream_over_http(dataframe)


def start_ws():
    # I call asyncio.run here because the WebSocket streamer is async but this menu file is synchronous.
    dataframe = load_transactions_from_csv(50)
    asyncio.run(stream_over_websocket(dataframe))


def start_random():
    # I keep the random mode separate because it is useful when I want a quick demo without CSV data.
    stream_random_transactions(30)


if __name__ == "__main__":
    print("\n=== Transaction Simulator ===")
    print("1) HTTP streaming")
    print("2) WebSocket streaming")
    print("3) Random transactions\n")

    user_choice = input("Choose a mode (1/2/3): ")

    if user_choice == "1":
        start_http()
    elif user_choice == "2":
        start_ws()
    elif user_choice == "3":
        start_random()
    else:
        print("Invalid choice.")
        
        

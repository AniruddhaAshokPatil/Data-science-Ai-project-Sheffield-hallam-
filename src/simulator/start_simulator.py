import asyncio

from src.simulator.http_streamer import stream_over_http
from src.simulator.load_csv_streamer import load_transactions_from_csv
from src.simulator.random_transactions import stream_random_transactions
from src.simulator.websocket_streamer import stream_over_websocket


def start_http():
    df = load_transactions_from_csv(50)
    stream_over_http(df)


def start_ws():
    df = load_transactions_from_csv(50)
    asyncio.run(stream_over_websocket(df))


def start_random():
    stream_random_transactions(30)


if __name__ == "__main__":
    print("\n=== Transaction Simulator ===")
    print("1) HTTP streaming")
    print("2) WebSocket streaming")
    print("3) Random transactions\n")

    choice = input("Choose a mode (1/2/3): ")

    if choice == "1":
        start_http()
    elif choice == "2":
        start_ws()
    elif choice == "3":
        start_random()
    else:
        print("Invalid choice.")
        
        

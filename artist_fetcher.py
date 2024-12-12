import requests
import json
import time
import csv
import sys
import argparse
from datetime import datetime, timedelta

URL = 'https://ra.co/graphql'
HEADERS = {
    'Content-Type': 'application/json',
    'Referer': 'https://ra.co/events/de/cologne',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
}
QUERY_TEMPLATE_PATH = "graphql_artist_query_template.json"
DELAY = 1  # Adjust this value as needed


class EventFetcher:
    """
    A class to fetch and print event details from RA.co
    """

    def __init__(self, artist):
        self.payload = self.generate_payload(artist)

    @staticmethod
    def generate_payload(artist):
        """
        Generate the payload for the GraphQL request.

        :param areas: The area code to filter events.
        :param listing_date_gte: The start date for event listings (inclusive).
        :param listing_date_lte: The end date for event listings (inclusive).
        :return: The generated payload.
        """
        with open(QUERY_TEMPLATE_PATH, "r") as file:
            payload = json.load(file)

        payload["variables"]["filters"][0]["value"] = artist
        payload["variables"]["baseFilters"][0]["value"] = artist

        return payload

    def get_events(self, page_number):
        """
        Fetch events for the given page number.

        :param page_number: The page number for event listings.
        :return: A list of events.
        """
        self.payload["variables"]["page"] = page_number
        response = requests.post(URL, headers=HEADERS, json=self.payload)

        try:
            response.raise_for_status()
            data = response.json()
        except (requests.exceptions.RequestException, ValueError):
            print(f"Error: {response.status_code}")
            return []

        if 'data' not in data:
            print(f"Error: {data}")
            return []
        

        return data["data"]["listing"]["data"]

    @staticmethod
    def print_event_details(events):
        """
        Print the details of the events.

        :param events: A list of events.
        """
        for event in events:
            event_data = event["event"]
            print(f"Event name: {event_data['title']}")
            print(f"Date: {event_data['date']}")
            print(f"Start Time: {event_data['startTime']}")
            print(f"End Time: {event_data['endTime']}")
            print(f"artist: {[artist['name'] for artist in event_data['artist']]}")
            print(f"Venue: {event_data['venue']['name']}")
            print(f"Event URL: {event_data['contentUrl']}")
            print(f"Number of guests attending: {event_data['attending']}")
            print("-" * 80)

    def fetch_and_print_all_events(self):
        """
        Fetch and print all events.
        """
        page_number = 1

        while True:
            events = self.get_events(page_number)

            if not events:
                break

            self.print_event_details(events)
            page_number += 1
            time.sleep(DELAY)

    def fetch_all_events(self):
        """
        Fetch all events and return them as a list.

        :return: A list of all events.
        """
        all_events = []
        page_number = 1

        while True:
            events = self.get_events(page_number)

            if not events:
                break

            all_events.extend(events)
            print(f"Fetched page {page_number}, Overall {len(all_events)} events")

            page_number += 1
            time.sleep(DELAY)

        return all_events

    def save_events_to_csv(self, events, output_file="events.csv"):
        """
        Save events to a CSV file.

        :param events: A list of events.
        :param output_file: The output file path. (default: "events.csv")
        """
        with open(output_file, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Event name", "Evend ID", "Date", "Start Time", "Event URL", "Artist ID", "Artist", "Venue ID", "Venue Name", "Venue URL", "Venue Area ID", "Venue Area Name", "Venue Area Country ID", "Venue Area Country URL Code", "guests"])

            for event in events:
                for artist in event['artists']:
                    writer.writerow([event['title'], 
                                    event['id'],
                                    event['date'], 
                                    event['startTime'],
                                    event['contentUrl'],
                                    artist['id'],
                                    artist['name'],
                                    event['venue']['id'],
                                    event['venue']['name'],
                                    event['venue']['contentUrl'],
                                    event['venue']['area']['id'],
                                    event['venue']['area']['name'],
                                    event['venue']['area']['country']['id'],
                                    event['venue']['area']['country']['urlCode'],
                                    event['interestedCount']])
                

def main():
    parser = argparse.ArgumentParser(description="Fetch events from ra.co and save them to a CSV file.")
    parser.add_argument("artist", type=str, help="The artist code to filter events.")
    parser.add_argument("-o", "--output", type=str, default="events.csv", help="The output file path (default: events.csv).")
    args = parser.parse_args()

    event_fetcher = EventFetcher(args.artist)

    event_fetcher.payload = event_fetcher.generate_payload(args.artist)
    events = event_fetcher.fetch_all_events()

    print(f"Fetched {len(events)} events")

    event_fetcher.save_events_to_csv(events, args.output)


if __name__ == "__main__":
    main()
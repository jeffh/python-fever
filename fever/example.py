from fever import FeverAPI
import getpass

def get_all_items(fever):
    "This is never called, but as an example of how to get all the items. This takes awhile."
    max_id = 0
    items_hash = {}

    items_count = 0
    items_received = 99999

    while items_received:
        items_received = 0
        json = fever.get_items(max_id=max_id)

        for item in json['items']:
            if not items_hash.get(item['id'], None):
                items_received += 1
                items_count += items_received
                max_id = min(item['id'], max_id or 999999999)
                items_hash[item['id']] = item
        print items_received, "=>", items_count, "items (%s&max_id=%d)" % (fever.items_url, max_id)
    return items_hash
    
def create_fever():
    "Creates a fever object interactively"
    fever = FeverAPI(raw_input('Fever URL: '))
    fever.authenticate(raw_input('Email Address: '), getpass.getpass('Password: '))
    return fever

"""
In command line
>>> from fever import example
>>> fever = example.create_fever()
# asks for fever info and authenticates
>>> fever.get_groups()
"""
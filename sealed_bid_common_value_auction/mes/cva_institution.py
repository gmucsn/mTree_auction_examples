from mTree.microeconomic_system.institution import Institution
from mTree.microeconomic_system.directive_decorators import *
from mTree.microeconomic_system.message import Message
import math
import random
import logging

EXPERIMENT = 25


@directive_enabled_class
class CVAInstitution(Institution):
    def __init__(self):
        self.auctions = 20

        self.agents = None

        self.min_item_value = 10
        self.max_item_value = 55

        self.error_permissible = [4,5,6,8]

        self.bids_outstanding = None

        self.item_for_auction = None
        self.error_for_auction = None
        self.bids = []

    @directive_decorator("init_institution")
    def init_institution(self, message:Message):
        if self.debug:
            print("Institution: received institution init ...")

    @directive_decorator("start_experiment")
    def start_experiment(self, message:Message):
        # send instructions and prompt lender for rate_of_return_offer
        if self.debug:
            print("INSTITUTION: Start Experiment")

    @directive_decorator("start_auction", message_schema=["agents"], message_callback="send_agents_start")
    def start_auction(self, message:Message):
        print("STARTING AN AUCTION")
        if self.auctions > 0:
            self.auctions -= 1
            print("INSTITUTION: Starting Auction")
            self.agents = message.get_payload()["agents"]
            self.bids = []
            self.bids_outstanding = len(self.agents)
            self.item_for_auction = random.randint(self.min_item_value, self.max_item_value)
            self.error_for_auction = self.error_permissible[random.randint(0, len(self.error_permissible)-1)]
            
            for agent in self.agents:
                agent_value = random.randint(self.item_for_auction - self.error_for_auction, self.item_for_auction + self.error_for_auction)

                new_message = Message()  # declare message
                new_message.set_sender(self.myAddress)  # set the sender of message to this actor
                new_message.set_directive("item_for_bidding")
                new_message.set_payload({"value": agent_value, "error": self.error_for_auction})
                self.send(agent, new_message)  # receiver_of_message, message
    
    @message_source("item_for_bidding")
    def send_agents_start(self):
        for agent in self.agents:
            agent_value = random.randint(self.item_for_auction - self.error_for_auction, self.item_for_auction + self.error_for_auction)

            new_message = Message()  # declare message
            new_message.set_sender(self.myAddress)  # set the sender of message to this actor
            new_message.set_directive("item_for_bidding")
            new_message.set_payload({"value": agent_value, "error": self.error_for_auction})
            self.send(agent, new_message)  # receiver_of_message, message

    def complete_auction(self):
        bids = sorted(self.bids, key=lambda elem: elem[0] ,reverse=True)

        winner = bids.pop(0)
        logging.log(EXPERIMENT, "Institution auction Winner: %s -> %s -> all bids -> %s", str(winner), self.item_for_auction, bids)
        new_message = Message()  # declare message
        new_message.set_sender(self.myAddress)  # set the sender of message to this actor
        new_message.set_directive("auction_result")
        new_message.set_payload({"status": "winner", "real_value": self.item_for_auction})

        self.send(winner[1], new_message)  # receiver_of_message, message

        for agent in bids:
            new_message = Message()  # declare message
            new_message.set_sender(self.myAddress)  # set the sender of message to this actor
            new_message.set_directive("auction_result")
            new_message.set_payload({"status": "loser"})
            self.send(agent[1], new_message)  # receiver_of_message, message

        new_message = Message()  # declare message
        new_message.set_sender(self.myAddress)  # set the sender of message to this actor
        new_message.set_directive("start_auction")
        new_message.set_payload({"agents": self.agents})
        self.send(self.myAddress, new_message)  # receiver_of_message, message

    @directive_decorator("bid_for_item", message_schema=["bid"])
    def accept_bid(self, message: Message):
        bidder = message.get_sender()
        bid = message.get_payload()["bid"]
        self.bids.append((bid, bidder))
        self.bids_outstanding -= 1
        if self.bids_outstanding == 0:
            self.log_data("AUCTION COMPLETE")
            self.complete_auction()


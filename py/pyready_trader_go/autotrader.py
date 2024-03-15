# Copyright 2021 Optiver Asia Pacific Pty. Ltd.
#
# This file is part of Ready Trader Go.
#
#     Ready Trader Go is free software: you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     Ready Trader Go is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public
#     License along with Ready Trader Go.  If not, see
#     <https://www.gnu.org/licenses/>.


"""
test and optimize pure market making strategy
"""




import asyncio
import itertools
import csv

from typing import List

from ready_trader_go import BaseAutoTrader, Instrument, Lifespan, MAXIMUM_ASK, MINIMUM_BID, Side, account


LOT_SIZE = 20
POSITION_LIMIT = 100
TICK_SIZE_IN_CENTS = 100
MIN_BID_NEAREST_TICK = (MINIMUM_BID + TICK_SIZE_IN_CENTS) // TICK_SIZE_IN_CENTS * TICK_SIZE_IN_CENTS
MAX_ASK_NEAREST_TICK = MAXIMUM_ASK // TICK_SIZE_IN_CENTS * TICK_SIZE_IN_CENTS
BID_OFFER_PERCENT = 0.998
ASK_OFFER_PERCENT = 1.002


class AutoTrader(BaseAutoTrader):
    """
    The general Idea of this AutoTrader is to either take advantage of an 'arbitrage' oppurtunity (either we can buy the etf way below the future price or we can sell the etf way above the future price)
    in this case we also
    at the beginning of this autoTrader we work only if one bid and ask offer from our autotrader
    """

    def __init__(self, loop: asyncio.AbstractEventLoop, team_name: str, secret: str):
        """Initialise a new instance of the AutoTrader class."""
        super().__init__(loop, team_name, secret)
        self.order_ids = itertools.count(1)
        self.bids = set()
        self.asks = set()
        self.ask_id = self.ask_price = self.bid_id = self.bid_price = self.position = 0
        self.future_price = self.etf_price = 0 #nh
        self.active_orders = self.active_volume = 0 #nh
        self.position = 0 #nh
        self.spread_a = self.spread_b = 0 #nh
        self.etf_bid = self.etf_ask = self.future_bid = self.future_ask = 0
        self.spread_etf = 0
        self.data_bo = []
        self.data_ao = []
        self.count_bid = self.count_ask = 0
        self.order_case = 0
                
        
        

    def on_error_message(self, client_order_id: int, error_message: bytes) -> None:
        """Called when the exchange detects an error.

        If the error pertains to a particular order, then the client_order_id
        will identify that order, otherwise the client_order_id will be zero.
        """
        self.logger.warning("error with order %d: %s", client_order_id, error_message.decode())
        if client_order_id != 0 and (client_order_id in self.bids or client_order_id in self.asks):
            self.on_order_status_message(client_order_id, 0, 0, 0)

    def on_hedge_filled_message(self, client_order_id: int, price: int, volume: int) -> None:
        """Called when one of your hedge orders is filled.

        The price is the average price at which the order was (partially) filled,
        which may be better than the order's limit price. The volume is
        the number of lots filled at that price.
        """
        self.logger.info("received hedge filled for order %d with average price %d and volume %d", client_order_id,
                         price, volume)

    def on_order_book_update_message(self, instrument: int, sequence_number: int, ask_prices: List[int],
                                     ask_volumes: List[int], bid_prices: List[int], bid_volumes: List[int]) -> None:
        """Called periodically to report the status of an order book.

        The sequence number can be used to detect missed or out-of-order
        messages. The five best available ask (i.e. sell) and bid (i.e. buy)
        prices are reported along with the volume available at each of those
        price levels.
        

        self.logger.info("received order book for instrument %d with sequence number %d", instrument,
                         sequence_number)
        """
        
        if instrument == Instrument.ETF:
            self.etf_price = (ask_prices[0]+bid_prices[0])/2
            self.etf_bid = bid_prices[0]
            self.etf_ask = ask_prices[0]
            
            
        

        if instrument == Instrument.FUTURE and self.etf_bid != 0 and self.etf_ask != 0:
            
            # calculate the 'fair' price of the future as the midpoint of best bid and best ask because the future should be liquid
            self.future_price = (ask_prices[0]+bid_prices[0])/2
                        

            # now calculate the bid and ask prices that we want to show to the market
            # now calculation very easy might do it differently
            # new_bid_price = int(round(self.future_price*(BID_OFFER_PERCENT)/TICK_SIZE_IN_CENTS)*TICK_SIZE_IN_CENTS) # -((self.position//10)*0.0004)
            # new_ask_price = int(round(self.future_price*(ASK_OFFER_PERCENT)/TICK_SIZE_IN_CENTS)*TICK_SIZE_IN_CENTS) #-((self.position//10)*0.0004)
            
            """
            if self.position > 50:
                if self.position > 80:
                    new_bid_price = int(self.future_price*0.995//TICK_SIZE_IN_CENTS*TICK_SIZE_IN_CENTS)
                    new_ask_price = int(self.future_price*1.001//TICK_SIZE_IN_CENTS*TICK_SIZE_IN_CENTS)
                else:
                    new_bid_price = int(self.future_price*0.996//TICK_SIZE_IN_CENTS*TICK_SIZE_IN_CENTS)
                    new_ask_price = int(self.future_price*1.002//TICK_SIZE_IN_CENTS*TICK_SIZE_IN_CENTS)
            elif self.position < -50:
                if self.position < -80:
                    new_bid_price = int(self.future_price*0.999//TICK_SIZE_IN_CENTS*TICK_SIZE_IN_CENTS)
                    new_ask_price = int(self.future_price*1.005//TICK_SIZE_IN_CENTS*TICK_SIZE_IN_CENTS)
                else:
                    new_bid_price = int(self.future_price*0.998//TICK_SIZE_IN_CENTS*TICK_SIZE_IN_CENTS)
                    new_ask_price = int(self.future_price*1.004//TICK_SIZE_IN_CENTS*TICK_SIZE_IN_CENTS)
            """

            pos_over_p50 = False
            pos_over_p70 = False
            pos_under_n50 = False
            pos_under_n70 = False

            if self.position > 50:
                if self.position > 80:
                    new_bid_price = int(round(self.future_price*(BID_OFFER_PERCENT-((self.position/10)*0.00025))/TICK_SIZE_IN_CENTS)*TICK_SIZE_IN_CENTS) # just do - 0.002
                    pos_over_p70 = pos_over_p50 = True
                else:
                    new_bid_price = int(round(self.future_price*(BID_OFFER_PERCENT-((self.position/10)*0.0002))/TICK_SIZE_IN_CENTS)*TICK_SIZE_IN_CENTS)
                    pos_over_p50 = True
            else:
                new_bid_price = int(round(self.future_price*(BID_OFFER_PERCENT)/TICK_SIZE_IN_CENTS)*TICK_SIZE_IN_CENTS)
            if self.position < -50:
                if self.position < -80:
                    new_ask_price = int(round(self.future_price*(ASK_OFFER_PERCENT-((self.position/10)*0.00025))/TICK_SIZE_IN_CENTS)*TICK_SIZE_IN_CENTS)
                    pos_under_n50 = pos_under_n70 = True
                else:
                    new_ask_price = int(round(self.future_price*(ASK_OFFER_PERCENT-((self.position/10)*0.0002))/TICK_SIZE_IN_CENTS)*TICK_SIZE_IN_CENTS)
                    pos_under_n50 = True
            else:
                new_ask_price = int(round(self.future_price*(ASK_OFFER_PERCENT)/TICK_SIZE_IN_CENTS)*TICK_SIZE_IN_CENTS)

            # the first case is that the price of the future went down and so we want to lower our offer for the etf
            # function also gets called when there is no active bid price provided by my autotrader
            
            if self.bid_price == 0 or (new_bid_price != self.bid_price and new_bid_price != 0):
                if pos_over_p50:
                    if pos_over_p70:
                        # first cancel the old bid order since we only want one order for the moment
                        if self.bid_id != 0:
                            self.send_cancel_order(self.bid_id)

                        # now send the new bid order
                        self.bid_id = next(self.order_ids)
                        self.bid_price = new_bid_price
                        lot_size = 0
                        """
                        if self.position < -30:
                            lot_size = abs(self.position)
                        else:
                        """
                        lot_size = LOT_SIZE - int(((self.position/10)*3))
                        if lot_size < 1:
                            lot_size = 1
                        
                        if lot_size + self.position > POSITION_LIMIT:
                            lot_size = 0
                        self.send_insert_order(self.bid_id, Side.BUY, self.bid_price, lot_size, Lifespan.GOOD_FOR_DAY)
                        self.bids.add(self.bid_id)
                        self.order_case = 0
                        self.logger.info('order ID: %d order case: %d price: %d size: %d', self.bid_id, self.order_case, self.bid_price, lot_size)
                        
                        
                    else:
                        # first cancel the old bid order since we only want one order for the moment
                        if self.bid_id != 0:
                            self.send_cancel_order(self.bid_id)

                        # now send the new bid order
                        self.bid_id = next(self.order_ids)
                        self.bid_price = new_bid_price
                        lot_size = 0
                        """
                        if self.position < -30:
                            lot_size = abs(self.position)
                        else:
                        """
                        lot_size = LOT_SIZE - int(((self.position/10)*3))
                        if lot_size < 1:
                            lot_size = 1
                        
                        if lot_size + self.position > POSITION_LIMIT:
                            lot_size = 0
                        self.send_insert_order(self.bid_id, Side.BUY, new_bid_price, lot_size, Lifespan.GOOD_FOR_DAY)
                        self.bids.add(self.bid_id)
                        self.order_case = 1
                        self.logger.info('order ID: %d order case: %d price: %d size: %d', self.bid_id, self.order_case, self.bid_price, lot_size)
                        
                else:
                    # first cancel the old bid order since we only want one order for the moment
                    if self.bid_id != 0:
                        self.send_cancel_order(self.bid_id)

                    # now send the new bid order
                    self.bid_id = next(self.order_ids)
                    self.bid_price = new_bid_price
                    lot_size = 0
                    """
                    if self.position < -30:
                        lot_size = abs(self.position)
                    else:
                    """
                    lot_size = LOT_SIZE - int(((self.position/10)*2))
                    if lot_size < 1:
                        lot_size = 1
                    
                    if lot_size + self.position > POSITION_LIMIT:
                        lot_size = 0
                    self.send_insert_order(self.bid_id, Side.BUY, new_bid_price, lot_size, Lifespan.GOOD_FOR_DAY)
                    self.bids.add(self.bid_id)
                    self.order_case = 2
                    self.logger.info('order ID: %d order case: %d price: %d size: %d', self.bid_id, self.order_case, self.bid_price, lot_size)
                    


            
                
            if self.ask_price == 0 or (new_ask_price != self.ask_price and new_ask_price != 0):
                if pos_under_n50:
                    if pos_under_n70:
                        # frist cancel the old ask order
                        if self.ask_id != 0:
                            self.send_cancel_order(self.ask_id)
                        
                        # now send new ask order
                        self.ask_id = next(self.order_ids)
                        self.ask_price = new_ask_price
                        lot_size = 0
                        """
                        if self.position > 30:
                            lot_size = self.position
                        else:
                        """
                        lot_size = LOT_SIZE + int(((self.position/10)*3))
                        if lot_size < 1:
                            lot_size = 1
                        
                        if self.position - lot_size < -POSITION_LIMIT:
                            lot_size = 0
                        self.send_insert_order(self.ask_id, Side.SELL, self.ask_price, lot_size, Lifespan.GOOD_FOR_DAY)
                        self.asks.add(self.ask_id)
                        self.order_case = 3
                        self.logger.info('order ID: %d order case: %d price: %d size: %d', self.ask_id, self.order_case, self.ask_price, lot_size)
                                           
                    else:
                        # frist cancel the old ask order
                        if self.ask_id != 0:
                            self.send_cancel_order(self.ask_id)
                        
                        # now send new ask order
                        self.ask_id = next(self.order_ids)
                        self.ask_price = new_ask_price
                        lot_size = 0
                        """
                        if self.position > 30:
                            lot_size = self.position
                        else:
                        """
                        lot_size = LOT_SIZE + int(((self.position/10)*3))
                        if lot_size < 1:
                            lot_size = 1
                        
                        if self.position - lot_size < -POSITION_LIMIT:
                            lot_size = 0
                        self.send_insert_order(self.ask_id, Side.SELL, new_ask_price, lot_size, Lifespan.GOOD_FOR_DAY)
                        self.asks.add(self.ask_id)
                        self.order_case = 4
                        self.logger.info('order ID: %d order case: %d price: %d size: %d', self.ask_id, self.order_case, self.ask_price, lot_size)
                        

                else:
                    if self.ask_price == 0 or (new_ask_price != self.ask_price and new_ask_price != 0):
                        # frist cancel the old ask order
                        if self.ask_id != 0:
                            self.send_cancel_order(self.ask_id)
                        
                        # now send new ask order
                        self.ask_id = next(self.order_ids)
                        self.ask_price = new_ask_price
                        lot_size = 0
                        """
                        if self.position > 30:
                            lot_size = self.position
                        else:
                        """
                        lot_size = LOT_SIZE + int(((self.position/10)*2))
                        if lot_size < 1:
                            lot_size = 1
                        
                        if self.position - lot_size < -POSITION_LIMIT:
                            lot_size = 0
                        self.send_insert_order(self.ask_id, Side.SELL, new_ask_price, lot_size, Lifespan.GOOD_FOR_DAY)
                        self.asks.add(self.ask_id)
                        self.order_case = 5
                        self.logger.info('order ID: %d order case: %d price: %d size: %d', self.ask_id, self.order_case, self.ask_price, lot_size)
                        
            

            
                
            
                

                            

                

    def on_order_filled_message(self, client_order_id: int, price: int, volume: int) -> None:
        """Called when one of your orders is filled, partially or fully.

        The price is the price at which the order was (partially) filled,
        which may be better than the order's limit price. The volume is
        the number of lots filled at that price.
        """
        self.logger.info("received order filled for order %d with price %d and volume %d", client_order_id,
                         price, volume)
        if client_order_id in self.bids:
            self.position += volume
            self.send_hedge_order(next(self.order_ids), Side.ASK, MIN_BID_NEAREST_TICK, volume)
            

        elif client_order_id in self.asks:
            self.position -= volume
            self.send_hedge_order(next(self.order_ids), Side.BID, MAX_ASK_NEAREST_TICK, volume)
             

    def on_order_status_message(self, client_order_id: int, fill_volume: int, remaining_volume: int,
                                fees: int) -> None:
        """Called when the status of one of your orders changes.

        The fill_volume is the number of lots already traded, remaining_volume
        is the number of lots yet to be traded and fees is the total fees for
        this order. Remember that you pay fees for being a market taker, but
        you receive fees for being a market maker, so fees can be negative.

        If an order is cancelled its remaining volume will be zero.
        """
        
        self.logger.info("received order status for order %d with fill volume %d remaining %d and fees %d",
                         client_order_id, fill_volume, remaining_volume, fees)
        if remaining_volume == 0:
            if client_order_id == self.bid_id:
                self.bid_id = 0
            elif client_order_id == self.ask_id:
                self.ask_id = 0

            # It could be either a bid or an ask
            self.bids.discard(client_order_id)
            self.asks.discard(client_order_id)

    def on_trade_ticks_message(self, instrument: int, sequence_number: int, ask_prices: List[int],
                               ask_volumes: List[int], bid_prices: List[int], bid_volumes: List[int]) -> None:
        """Called periodically when there is trading activity on the market.

        The five best ask (i.e. sell) and bid (i.e. buy) prices at which there
        has been trading activity are reported along with the aggregated volume
        traded at each of those price levels.

        If there are less than five prices on a side, then zeros will appear at
        the end of both the prices and volumes arrays.
        
        self.logger.info("received trade ticks for instrument %d with sequence number %d", instrument,
                         sequence_number)
        """
        # if possible implement a strategy that takes advantage when a trade happend and the price
        # is outside the normal price, check if we can also fill an order there
        # maybe with a fill and kill order

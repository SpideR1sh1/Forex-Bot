# region imports
from AlgorithmImports import *


# endregion

class TrailingCost(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2018, 12, 9)  # Set Start Date
        self.SetEndDate(2022, 3, 22)
        self.SetCash(100000)  # Set Strategy Cash
        self.qqq = self.AddEquity("QQQ", Resolution.Hour).Symbol

        self.entryTicket = None
        self.stopMarketTicket = None
        self.entryTime = datetime.min
        self.StopMarketOrderFillTime = datetime.min
        self.highestPrice = 0

    def OnData(self, data: Slice):
        if (self.Time - self.StopMarketOrderFillTime).days < 30:
            return

        price = self.Securities[self.qqq].Price

        # move limit price if not filled after 1 day
        if not self.Portfolio.Invested and not self.Transactions.GetOpenOrders(self.qqq):
            quantity = self.CalculateOrderQuantity(self.qqq, 0.9)
            self.entryTicket = self.LimitOrder(self.qqq, quantity, price, "Entry Order")
            self.entryime = self.Time

        # move up trailing stop price
        if self.stopMarketTicket is not None and self.Portfolio.Invested:
            if price > self.highestPrice:
                updateFiles = UpdateOrderFields()
                updateFields = UpdateOrderFields()
                updateFields.StopPrice = price * 0.95
                self.stopMarketTicket.Update(updateFields)

    def OnOrderEvent(self, orderEvent):
        if orderEvent.Status != OrderStatus.Filled:
            return

        if self.entryTicket is not None and self.entryTicket.OrderId == orderEvent.OrderId:
            self.stopMarketTicket = self.StopMarketOrder(self.qqq, -self.entryTicket.Quantity,
                                                         0.95 * self.entryTicket.AverageFillPrice)

        if self.stopMarketTicket is not None and self.stopMarketTicket.OrderId == orderEvent.OrderId:
            self.stopMarketOrderFillTime = self.Time
            self.highestPrice = 0
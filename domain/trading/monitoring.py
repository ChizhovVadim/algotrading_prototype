from domain.model.trader import PlannedPosition


class MonitoringService:
    def __init__(self, brokerRegistry):
        self._brokerRegistry = brokerRegistry

    def update(self, signals, positions: list[PlannedPosition]):
        totalBrokers = 0
        for client, broker in self._brokerRegistry.items():
            totalBrokers += 1
            print(client, type(broker).__name__)
        print(f"Total brokers: {totalBrokers}")

        for signal in signals:
            print(signal)
        print(f"Total signals: {len(signals)}")

        visitedPortfolios = set()
        for position in positions:
            portfolio = position.portfolio
            if portfolio in visitedPortfolios:
                continue
            visitedPortfolios.add(portfolio)

            limits = self._brokerRegistry.getPortfolioLimits(portfolio)
            varMargin = limits.accVarMargin + limits.varMargin
            if limits.startLimitOpenPos:
                varMarginRatio = varMargin / limits.startLimitOpenPos
                usedRatio = limits.usedLimOpenPos / limits.startLimitOpenPos
            else:
                varMarginRatio = 0
                usedRatio = 0
            status = {
                "Client": portfolio.clientKey,
                "Portfolio": portfolio.portfolio,
                "startLimitOpenPos": limits.startLimitOpenPos,
                "varMargin": varMargin,
                "varMarginRatio": varMarginRatio,
                "usedRatio": usedRatio,
            }
            print(status)
        print(f"Total portfolios: {len(visitedPortfolios)}")

        for position in positions:
            actualPosition = self._brokerRegistry.getPosition(
                position.portfolio, position.security
            )
            status = {
                "Client": position.portfolio.clientKey,
                "Portfolio": position.portfolio.portfolio,
                "Security": position.security.name,
                "PlannedPos": position.planned,
                "ActualPos": actualPosition,
                "Status": "+" if position.planned == actualPosition else "!",
            }
            print(status)
        print(f"Total strategies: {len(positions)}")

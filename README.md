# algotrading_prototype
Проект демонстрирует возможную архитектуру для автоторговли. Можно брать за основу при реализации автоторговли на любых языках программирования. Прект состоит из 3 основных частей:
- advisors: торговые советники
- history: тестирование торговых советников на истории
- trader: автоторговля по заданным стратегиям

## advisors
Советник рекомендует позицию в отрезке [-1;+1] от шорт "на все" до лонг "на все". Это позволяет гибко менять позицию. В качестве примера приводится простейшая стратегия (не рекомендуется для использования). Оснонвная идея строить стратегии из индикаторов как из кубиков:
```
def momentumAdvisor():
    ind = WeightSumIndicator(
        [MomentumIndicator(1),
         MomentumIndicator(2),
         MomentumIndicator(5),
         MomentumIndicator(10),
         MomentumIndicator(20)],
        [0.2, 0.2, 0.2, 0.2, 0.2])
    ind = EmaIndicator(1.0/25, ind)
    ind = CandleDecorator(ind)
    return advisorFromIndicator(ind)
```

## history
Пример тестирования стратегии на квартальных фьючерсах Si c 2009 года. Папка ~/TradingData//minutes5 должна содержать исторические котировки квартальных фьючерсов.
```
$python3 -m history --advisor sample_momentum --security Si --startyear 2009
```
## trader
Чтобы торговать, нужно реализовать протокол Trader. Проект содержит следующие реализации этого протокола:
- MockTrader: не выводит заявки, можно использовать для тестирования
- QuikTrader: для торговли через терминал Quik, по аналогии с проектом [QuikSharp](https://github.com/finsight/QUIKSharp). Для работы нужно установить [Lua скрипты для Quik](https://github.com/finsight/QUIKSharp/tree/master/src/QuikSharp/lua).
- MultyTrader: хранит словарь Trader и позволяет вызывать любой из них. Удобен, если надо работать со многими счетами, брокерами.

При необходимости можно реализовать другие Trader (finam, alor, T).

Запуск автоторговли:
```
$python3 -m trader
```
## Ссылки
- [QuikSharp](https://github.com/finsight/QUIKSharp)
- [QuikPy](https://github.com/cia76/QuikPy)

# algotrading_prototype
Проект демонстрирует возможную архитектуру для автоторговли.

## Тестирование
Пример тестирования стратегии на квартальных фьючерсах Si c 2009 года. Папка ~/TradingData/minutes5 должна содержать исторические котировки квартальных фьючерсов.
```
python3 -m app.advisorreport --security Si --startyear 2009
```
## Автоторговля
Запуск автоторговли:
```
$python3 -m app.trader
```
## Ссылки
- [QuikSharp](https://github.com/finsight/QUIKSharp)
- [QuikPy](https://github.com/cia76/QuikPy)

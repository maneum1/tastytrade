import os
from datetime import datetime
from decimal import Decimal


from unittest.mock import AsyncMock, patch
# from sqlalchemy.ext.asyncio import AsyncSession

import pytest
from anyio import sleep

from tastytrade import Account, Session
from tastytrade.instruments import Equity
from tastytrade.order import (
    NewComplexOrder,
    NewOrder,
    OrderAction,
    OrderTimeInForce,
    OrderType,
    PlacedOrder,
)

pytestmark = pytest.mark.anyio


@pytest.fixture(scope="module")
def session(anyio_backend: str) -> Session:
    return Session(os.environ["TT_SECRET"], os.environ["TT_REFRESH"])


@pytest.fixture(scope="module")
def account_number() -> str:
    return os.environ["TT_ACCOUNT"]


@pytest.fixture(scope="module")
async def account(anyio_backend: str, session: Session, account_number: str):
    yield await Account.get(session, account_number)



#@pytest.mark.asyncio
@patch.object(Session, '_get', new_callable=AsyncMock)
async def test_get_accounts_new(mock_get: AsyncMock, session: Session):
    # Setup the mock response
    mock_response = {
        'items': [
            {
                'account': {
                    'account-number': '5WT12345',
                    'account-type-name': 'Roth IRA',
                    'created-at': '2020-01-21T05:16:31.201+00:00',
                    'day-trader-status': False,
                    'ext-crm-id': 'test-ext-crm-id1',
                    'external-id': 'A00000external-id',
                    'funding-date': '2020-01-22',
                    'futures-account-purpose': 'SPECULATING',
                    'investment-objective': 'SPECULATION',
                    'is-closed': False,
                    'is-firm-error': False,
                    'is-firm-proprietary': False,
                    'is-foreign': False,
                    'is-futures-approved': True,
                    'margin-or-cash': 'Cash',
                    'nickname': 'Nickname account 1',
                    'opened-at': '2020-01-21T05:22:31.110+00:00',
                    'regulatory-domain': 'USA',
                    'suitable-options-level': 'Defined Risk Spreads Plus Naked'
                    },
                'authority-level': 'owner'
            },
            {
                'account': {
                    'account-number': '5WT67890',
                    'account-type-name': 'Individual',
                    'created-at': '2021-01-05T06:09:28.222+00:00',
                    'day-trader-status': False,
                    'ext-crm-id': 'test-ext-crm-id2',
                    'external-id': 'A00001external-id',
                    'funding-date': '2021-01-05',
                    'futures-account-purpose': 'SPECULATING',
                    'investment-objective': 'SPECULATION',
                    'is-closed': True,
                    'is-firm-error': False,
                    'is-firm-proprietary': False,
                    'is-foreign': False,
                    'is-futures-approved': True,
                    'margin-or-cash': 'Margin',
                    'nickname': 'Individual',
                    'opened-at': '2021-01-05T03:17:38.123+00:00',
                    'regulatory-domain': 'USA',
                    'suitable-options-level': 'No Restrictions'
                },
                'authority-level': 'owner'
            }
        ]
    }

    # Configure the mock to return the above response
    mock_get.return_value = mock_response
    
    # Call the method under test
    accounts = await Account.get(session)

    # Assertions
    assert accounts is not None  
    assert isinstance(accounts, list)  
    assert len(accounts) == 1  # Assuming include_closed is False, only open accounts should be included
    assert accounts[0].account_number == "5WT12345"  # Validate the expected account's number


#@pytest.mark.asyncio
@patch.object(Session, '_get', new_callable=AsyncMock)
async def test_get_specific_account(mock_get: AsyncMock, session: Session):
    # Setup mock for a specific account retrieval
    account_number = "5WT12345"
    # mock_get.return_value = {"account": {"account-number": account_number, "is-closed": False}}
    mock_get.return_value ={
                    'account-number': account_number,
                    'account-type-name': 'Roth IRA',
                    'created-at': '2020-01-21T05:16:31.201+00:00',
                    'day-trader-status': False,
                    'ext-crm-id': 'test-ext-crm-id1',
                    'external-id': 'A00000external-id',
                    'funding-date': '2020-01-22',
                    'futures-account-purpose': 'SPECULATING',
                    'investment-objective': 'SPECULATION',
                    'is-closed': False,
                    'is-firm-error': False,
                    'is-firm-proprietary': False,
                    'is-foreign': False,
                    'is-futures-approved': True,
                    'margin-or-cash': 'Cash',
                    'nickname': 'Nickname account 1',
                    'opened-at': '2020-01-21T05:22:31.110+00:00',
                    'regulatory-domain': 'USA',
                    'suitable-options-level': 'Defined Risk Spreads Plus Naked'
                }
    
    account = await Account.get(session, account_number=account_number)
    
    # Assertions
    assert account is not None
    assert account.account_number == account_number



async def test_get_account(account: Account):
    pass


async def test_get_accounts(session: Session):
    assert await Account.get(session)


async def test_get_trading_status(session: Session, account: Account):
    await account.get_trading_status(session)


async def test_get_balances(session: Session, account: Account):
    await account.get_balances(session)


async def test_get_balance_snapshots(session: Session, account: Account):
    await account.get_balance_snapshots(session)


async def test_get_positions(session: Session, account: Account):
    await account.get_positions(session)


async def test_get_history(session: Session, account: Account):
    hist = await account.get_history(session, page_offset=0)
    tid = hist[0].id
    await account.get_transaction(session, tid)


async def test_get_total_fees(session: Session, account: Account):
    await account.get_total_fees(session)


async def test_get_margin_requirements(session: Session, account: Account):
    await account.get_margin_requirements(session)


@pytest.mark.parametrize(
    "time_back, start_time",
    [
        ("1y", None),
        (None, datetime(2024, 1, 1)),
        pytest.param(None, None, marks=pytest.mark.xfail, id="intentional_fail"),
    ],
)
async def test_get_net_liquidating_value_history(
    session: Session,
    account: Account,
    time_back: str | None,
    start_time: datetime | None,
):
    await sleep(1)
    await account.get_net_liquidating_value_history(
        session, time_back=time_back, start_time=start_time
    )


async def test_get_order_history(session: Session, account: Account):
    await account.get_order_history(session, page_offset=0)


async def test_get_complex_order_history(session: Session, account: Account):
    await account.get_complex_order_history(session, page_offset=0)


async def test_get_live_orders(session: Session, account: Account):
    await account.get_live_orders(session)


@pytest.fixture(scope="module")
async def new_order(session: Session) -> NewOrder:
    symbol = await Equity.get(session, "F")
    leg = symbol.build_leg(1, OrderAction.BUY_TO_OPEN)
    return NewOrder(
        time_in_force=OrderTimeInForce.GTC,
        order_type=OrderType.LIMIT,
        legs=[leg],
        price=Decimal(-2),
    )


@pytest.fixture(scope="module")
async def notional_order(session: Session) -> NewOrder:
    symbol = await Equity.get(session, "AAPL")
    leg = symbol.build_leg(None, OrderAction.BUY_TO_OPEN)
    return NewOrder(
        time_in_force=OrderTimeInForce.GTC,
        order_type=OrderType.NOTIONAL_MARKET,
        legs=[leg],
        value=Decimal(-5),
    )


@pytest.fixture(scope="module")
async def placed_order(
    session: Session, account: Account, new_order: NewOrder
) -> PlacedOrder:
    return (await account.place_order(session, new_order, dry_run=False)).order


async def test_place_order(placed_order: PlacedOrder):
    pass


async def test_place_notional_order(
    session: Session, account: Account, notional_order: NewOrder
):
    await account.place_order(session, notional_order, dry_run=True)


async def test_get_order(session: Session, account: Account, placed_order: PlacedOrder):
    await sleep(3)
    placed = await account.get_order(session, placed_order.id)
    assert placed.id == placed_order.id


async def test_replace_and_delete_order(
    session: Session,
    account: Account,
    new_order: NewOrder,
    placed_order: PlacedOrder,
):
    modified_order = new_order.model_copy()
    modified_order.price = Decimal("-2.01")
    replaced = await account.replace_order(session, placed_order.id, modified_order)
    await sleep(3)
    await account.delete_order(session, replaced.id)


async def test_place_complex_order(session: Session, account: Account):
    await sleep(3)
    symbol = await Equity.get(session, "AAPL")
    opening = symbol.build_leg(1, OrderAction.BUY_TO_OPEN)
    closing = symbol.build_leg(1, OrderAction.SELL_TO_CLOSE)
    otoco = NewComplexOrder(
        trigger_order=NewOrder(
            time_in_force=OrderTimeInForce.GTC,
            order_type=OrderType.LIMIT,
            legs=[opening],
            price=Decimal("-2"),  # won't fill
        ),
        orders=[
            NewOrder(
                time_in_force=OrderTimeInForce.GTC,
                order_type=OrderType.LIMIT,
                legs=[closing],
                price=Decimal("400"),  # won't fill
            ),
            NewOrder(
                time_in_force=OrderTimeInForce.GTC,
                order_type=OrderType.STOP,
                legs=[closing],
                stop_trigger=Decimal("1.5"),  # won't fill
            ),
        ],
    )
    resp = await account.place_complex_order(session, otoco, dry_run=False)
    await sleep(3)
    await account.delete_complex_order(session, resp.complex_order.id)


async def test_get_live_complex_orders(session: Session, account: Account):
    orders = await account.get_live_complex_orders(session)
    assert orders != []


async def test_place_oco_order(session: Session, account: Account):
    # account must have a share of F for this to work
    symbol = await Equity.get(session, "F")
    closing = symbol.build_leg(1, OrderAction.SELL_TO_CLOSE)
    oco = NewComplexOrder(
        orders=[
            NewOrder(
                time_in_force=OrderTimeInForce.GTC,
                order_type=OrderType.LIMIT,
                legs=[closing],
                price=Decimal(1000),  # will never fill
            ),
            NewOrder(
                time_in_force=OrderTimeInForce.GTC,
                order_type=OrderType.STOP,
                legs=[closing],
                stop_trigger=Decimal(1),  # will never fill
            ),
        ]
    )
    resp2 = await account.place_complex_order(session, oco, dry_run=False)
    await sleep(3)
    # test get complex order
    _ = await account.get_complex_order(session, resp2.complex_order.id)
    await account.delete_complex_order(session, resp2.complex_order.id)


async def test_place_otoco_order(session: Session, account: Account):
    symbol = await Equity.get(session, "AAPL")
    opening = symbol.build_leg(1, OrderAction.BUY_TO_OPEN)
    closing = symbol.build_leg(1, OrderAction.SELL_TO_CLOSE)
    otoco = NewComplexOrder(
        trigger_order=NewOrder(
            time_in_force=OrderTimeInForce.GTC,
            order_type=OrderType.LIMIT,
            legs=[opening],
            price=Decimal("-2"),  # won't fill
        ),
        orders=[
            NewOrder(
                time_in_force=OrderTimeInForce.GTC,
                order_type=OrderType.LIMIT,
                legs=[closing],
                price=Decimal(400),  # won't fill
            ),
            NewOrder(
                time_in_force=OrderTimeInForce.GTC,
                order_type=OrderType.STOP,
                legs=[closing],
                stop_trigger=Decimal("1.5"),  # won't fill
            ),
        ],
    )
    resp = await account.place_complex_order(session, otoco, dry_run=False)
    await sleep(3)
    await account.delete_complex_order(session, resp.complex_order.id)

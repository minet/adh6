import json
from unittest.mock import MagicMock

import pytest
from adh6.entity import AbstractAccount, AbstractTransaction
from adh6.treasury.router import _parse_account_filter, _parse_transaction_filter
from fastapi import Request


class TestParseAccountFilter:
    def test_json_filter(self):
        request = MagicMock(spec=Request)
        raw_filter = '{"id": 1, "name": "Test Account"}'
        result = _parse_account_filter(request, raw_filter)
        assert isinstance(result, AbstractAccount)
        assert result.id == 1
        assert result.name == "Test Account"

    def test_query_params_filter(self):
        # filter[id]=1&filter[name]=Test&filter[actif]=true&filter[pinned]=false&filter[compteCourant]=true
        query_params = [
            ("filter[id]", "1"),
            ("filter[name]", "Test"),
            ("filter[actif]", "true"),
            ("filter[pinned]", "false"),
            ("filter[compteCourant]", "true"),
            ("other", "value"),
        ]
        request = MagicMock(spec=Request)
        request.query_params.multi_items.return_value = query_params

        result = _parse_account_filter(request, None)
        assert result is not None
        assert result.id == 1
        assert result.name == "Test"
        assert result.actif is True
        assert result.pinned is False
        assert result.compte_courant is True

    def test_empty_filter(self):
        request = MagicMock(spec=Request)
        request.query_params.multi_items.return_value = []
        result = _parse_account_filter(request, None)
        assert result is None


class TestParseTransactionFilter:
    def test_json_filter(self):
        request = MagicMock(spec=Request)
        raw_filter = '{"id": 100, "pendingValidation": true}'
        result = _parse_transaction_filter(request, raw_filter)
        assert isinstance(result, AbstractTransaction)
        assert result.id == 100
        assert result.pending_validation is True

    def test_query_params_filter(self):
        query_params = [
            ("filter[id]", "100"),
            ("filter[src]", "1"),
            ("filter[dst]", "2"),
            ("filter[paymentMethod]", "3"),
            ("filter[pendingValidation]", "true"),
        ]
        request = MagicMock(spec=Request)
        request.query_params.multi_items.return_value = query_params

        result = _parse_transaction_filter(request, None)
        assert result is not None
        assert result.id == 100
        assert result.src == 1
        assert result.dst == 2
        assert result.payment_method == 3
        assert result.pending_validation is True

    def test_json_filter_invalid(self):
        request = MagicMock(spec=Request)
        raw_filter = "invalid json"
        with pytest.raises(json.JSONDecodeError):
            _parse_transaction_filter(request, raw_filter)

    def test_query_params_filter_minimal(self):
        query_params = [("filter[id]", "1")]
        request = MagicMock(spec=Request)
        request.query_params.multi_items.return_value = query_params
        result = _parse_transaction_filter(request, None)
        assert result is not None
        assert result.id == 1

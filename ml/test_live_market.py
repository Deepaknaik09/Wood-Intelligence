"""Unit tests for ml/live_market.py."""

import copy
import unittest

import live_market


class TestLiveMarket(unittest.TestCase):
    def test_next_month_labels_year_rollover(self):
        labels = live_market.next_month_labels("2026-11", 3)
        self.assertEqual(labels, ["Dec '26 (Pred)", "Jan '27 (Pred)", "Feb '27 (Pred)"])

    def test_offline_fallback_builds_all_species(self):
        snap = {
            "status": "offline",
            "months_ym": live_market._rolling_months("2026-10", 12),
            "month_labels": [live_market.format_ym_label(ym) for ym in live_market._rolling_months("2026-10", 12)],
            "quotes": {},
        }
        wdata, mlabels, last_ym = live_market.build_live_wood_price_data(snap)
        self.assertEqual(len(wdata), 8)
        self.assertEqual(len(mlabels), 12)
        self.assertEqual(last_ym, "2026-10")
        for wid, item in wdata.items():
            self.assertEqual(len(item["history"]), 12, f"{wid} history len != 12")
            self.assertGreater(item["current_price"], 0)

    def test_prices_change_dynamically_with_market_moves(self):
        months = live_market._rolling_months("2026-11", 12)
        base_quotes = {
            "LBR=F": {"live_price": 500.0, "monthly": {m: 500.0 for m in months}},
            "USDINR=X": {"live_price": 90.0, "monthly": {m: 90.0 for m in months}},
            "WOOD": {"live_price": 70.0, "monthly": {m: 70.0 for m in months}},
            "CENTURYPLY.NS": {"live_price": 750.0, "monthly": {m: 750.0 for m in months}},
            "GREENPLY.NS": {"live_price": 280.0, "monthly": {m: 280.0 for m in months}},
        }
        snap_low = {
            "status": "live",
            "months_ym": months,
            "month_labels": [live_market.format_ym_label(m) for m in months],
            "quotes": base_quotes,
        }
        snap_high = copy.deepcopy(snap_low)
        snap_high["quotes"]["LBR=F"]["monthly"][months[-1]] = 650.0
        snap_high["quotes"]["USDINR=X"]["monthly"][months[-1]] = 98.0
        snap_high["quotes"]["CENTURYPLY.NS"]["monthly"][months[-1]] = 900.0

        w_low, _, _ = live_market.build_live_wood_price_data(snap_low)
        w_high, _, _ = live_market.build_live_wood_price_data(snap_high)

        self.assertGreater(w_high["pine"]["current_price"], w_low["pine"]["current_price"])
        self.assertGreater(w_high["teak"]["current_price"], w_low["teak"]["current_price"])
        self.assertGreater(w_high["plywood"]["current_price"], w_low["plywood"]["current_price"])

    def test_indiamart_html_parser_and_pricing_integration(self):
        sample_state = {
            "priceWidgetData": [{"Arrival_Date": "12/11/2026", "price_range": "₹ 1,350/Cubic Feet"}],
            "data": [
                {
                    "p_nm": "Burma Border Teak Wood Log",
                    "pr": "₹ 3,000/Cubic Feet",
                    "prd_price": "3000",
                    "CMP": "Sun City Corporation",
                    "city": "Mangalore",
                    "p_url": "https://www.indiamart.com/proddetail/test.html",
                },
                {
                    "p_nm": "Red Cedar Wood",
                    "pr": "₹ 1,800/Cubic Feet",
                    "prd_price": "1800",
                    "CMP": "Bombay Saw Mills",
                    "city": "Mangalore",
                    "p_url": "",
                },
            ],
        }
        import json
        html_doc = (
            "<html><body><script>"
            f"window.__INITIAL_STATE__ = {json.dumps(sample_state)};"
            "</script></body></html>"
        )
        parsed = live_market.parse_indiamart_html(html_doc, city_slug="mangalore")
        self.assertEqual(parsed["modal_cft"], 1350.0)
        self.assertEqual(parsed["median_cft"], 2400.0)
        self.assertEqual(len(parsed["listings"]), 2)
        self.assertGreater(parsed["city_index_ratio"], 1.0)

        months = live_market._rolling_months("2026-11", 12)
        snap = {
            "status": "live",
            "months_ym": months,
            "month_labels": [live_market.format_ym_label(m) for m in months],
            "quotes": {
                "LBR=F": {"live_price": 544.0, "monthly": {m: 544.0 for m in months}},
                "USDINR=X": {"live_price": 89.2, "monthly": {m: 89.2 for m in months}},
                "WOOD": {"live_price": 71.5, "monthly": {m: 71.5 for m in months}},
                "CENTURYPLY.NS": {"live_price": 790.0, "monthly": {m: 790.0 for m in months}},
                "GREENPLY.NS": {"live_price": 285.0, "monthly": {m: 285.0 for m in months}},
            },
        }
        w_base, _, _ = live_market.build_live_wood_price_data(snap)
        w_city, _, _ = live_market.build_live_wood_price_data(snap, indiamart_data=parsed)
        self.assertGreater(w_city["teak"]["current_price"], w_base["teak"]["current_price"])
        self.assertEqual(len(w_city["teak"]["local_quotes"]), 1)

    def test_live_api_fetch_end_to_end(self):
        snap = live_market.fetch_live_market_snapshot()
        self.assertIn(snap["status"], ("live", "partial", "cached", "offline"))
        self.assertEqual(len(snap["months_ym"]), 12)
        self.assertGreater(len(snap["quotes"]), 0)
        wdata, _, _ = live_market.build_live_wood_price_data(snap)
        self.assertEqual(len(wdata), 8)


if __name__ == "__main__":
    unittest.main()


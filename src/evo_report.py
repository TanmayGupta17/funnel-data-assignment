import pandas as pd
import sqlite3
import json
import argparse
import os
from pathlib import Path

class EvoAnalysis:
    def __init__(self, events_file, messages_file, orders_file, output_dir):
        self.events_file = events_file
        self.messages_file = messages_file
        self.orders_file = orders_file
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.conn = sqlite3.connect(':memory:')

    def load_data(self):
        print("Loading data...")
        pd.read_csv(self.events_file).to_sql('events', self.conn, index=False, if_exists='replace')
        pd.read_csv(self.messages_file).to_sql('messages', self.conn, index=False, if_exists='replace')
        pd.read_csv(self.orders_file).to_sql('orders', self.conn, index=False, if_exists='replace')

    def run_funnel_analysis(self):
        print("Running funnel analysis...")
        query = """
        SELECT
          device,
          COUNT(DISTINCT CASE WHEN event_name='Loaded'   THEN user_id END) AS loaded_users,
          COUNT(DISTINCT CASE WHEN event_name='Interact' THEN user_id END) AS interact_users,
          COUNT(DISTINCT CASE WHEN event_name='Clicks'   THEN user_id END) AS clicks_users,
          COUNT(DISTINCT CASE WHEN event_name='Purchase' THEN user_id END) AS purchase_users,
          ROUND(
            100.0
            * COUNT(DISTINCT CASE WHEN event_name='Interact' THEN user_id END)
            / NULLIF(COUNT(DISTINCT CASE WHEN event_name='Loaded' THEN user_id END), 0),
            2
          ) AS conv_loaded_to_interact_pct,
          ROUND(
            100.0
            * COUNT(DISTINCT CASE WHEN event_name='Clicks' THEN user_id END)
            / NULLIF(COUNT(DISTINCT CASE WHEN event_name='Interact' THEN user_id END), 0),
            2
          ) AS conv_interact_to_clicks_pct,
          ROUND(
            100.0
            * COUNT(DISTINCT CASE WHEN event_name='Purchase' THEN user_id END)
            / NULLIF(COUNT(DISTINCT CASE WHEN event_name='Clicks' THEN user_id END), 0),
            2
          ) AS conv_clicks_to_purchase_pct
        FROM events
        WHERE event_name IN ('Loaded','Interact','Clicks','Purchase')
        GROUP BY device
        ORDER BY device;
        """
        return pd.read_sql_query(query, self.conn)

    def run_intent_analysis(self):
        print("Running intent analysis...")
        query = """
        SELECT
          CASE WHEN detected_intent IS NULL OR TRIM(detected_intent) = '' THEN 'unknown'
               ELSE detected_intent
          END AS intent,
          COUNT(*) AS total_intents,
          ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM messages), 2) AS pct_of_total,
          ROUND(
            100.0 * SUM(CASE WHEN e.event_name = 'Purchase' THEN 1 ELSE 0 END)
            / NULLIF(COUNT(DISTINCT m.session_id), 0),
            2
          ) AS purchase_conversion_rate
        FROM messages m
        LEFT JOIN events e ON m.session_id = e.session_id
        GROUP BY intent
        ORDER BY total_intents DESC;
        """
        return pd.read_sql_query(query, self.conn)

    def run_cancellation_analysis(self):
        print("Running cancellation analysis...")
        query = """
                        SELECT
                COUNT(*) AS total_orders,
                SUM(CASE
                        WHEN canceled_at IS NOT NULL THEN 1
                        ELSE 0
                    END) AS canceled,
                SUM(CASE
                        WHEN canceled_at IS NOT NULL
                            AND (julianday(canceled_at) - julianday(created_at)) * 24 * 60 > 60
                        THEN 1
                        ELSE 0
                    END) AS violations,
                ROUND(
                    100.0 * SUM(CASE
                                    WHEN canceled_at IS NOT NULL
                                        AND (julianday(canceled_at) - julianday(created_at)) * 24 * 60 > 60
                                    THEN 1
                                    ELSE 0
                                END)
                    / COUNT(*),
                    2
                ) AS violation_rate_pct
            FROM
                orders;


        """
        df = pd.read_sql_query(query, self.conn)
        return df.iloc[0].to_dict()

    def generate_report(self, funnel_df, intent_df, cancellation_dict):
        print("Generating report...")
        report = {
            "funnel": funnel_df.to_dict('records'),
            "intents": intent_df.to_dict('records'),
            "cancellation_sla": cancellation_dict
        }
        with open(self.output_dir / 'report.json', 'w') as f:
            json.dump(report, f, indent=2)
        print(f"Report saved to {self.output_dir / 'report.json'}")

    def run(self):
        self.load_data()
        funnel_df = self.run_funnel_analysis()
        intent_df = self.run_intent_analysis()
        cancellation = self.run_cancellation_analysis()
        self.generate_report(funnel_df, intent_df, cancellation)
        print("Analysis complete!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evo Report Analysis")
    parser.add_argument('--events', required=True, help='Path to events.csv')
    parser.add_argument('--messages', required=True, help='Path to messages.csv')
    parser.add_argument('--orders', required=True, help='Path to orders.csv')
    parser.add_argument('--out', required=True, help='Output directory')
    args = parser.parse_args()
    EvoAnalysis(args.events, args.messages, args.orders, args.out).run()

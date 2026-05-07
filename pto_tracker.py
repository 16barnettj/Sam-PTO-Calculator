#!/usr/bin/env python3
"""
PTO Tracker - Track your paid time off accrual and usage
"""

import json
import os
from datetime import datetime, timedelta
from collections import defaultdict


class PTOTracker:
    def __init__(self, data_file='pto_data.json'):
        self.data_file = data_file
        self.data = self.load_data()

    def load_data(self):
        """Load PTO data from JSON file"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                return json.load(f)
        return {
            'start_date': None,
            'hours_per_week': None,
            'accrual_rate': None,
            'vacation_days': []  # List of {'date': 'YYYY-MM-DD', 'hours': 8}
        }

    def save_data(self):
        """Save PTO data to JSON file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=2)
        print(f"✓ Data saved to {self.data_file}")

    def setup(self):
        """Initial setup - collect user inputs"""
        print("\n" + "="*60)
        print("PTO TRACKER SETUP")
        print("="*60)

        # Start date
        while True:
            start_date_str = input("\nEnter start date (YYYY-MM-DD): ").strip()
            try:
                datetime.strptime(start_date_str, '%Y-%m-%d')
                self.data['start_date'] = start_date_str
                break
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD")

        # Hours per week
        while True:
            try:
                hours_per_week = float(input("Enter hours worked per week (e.g., 40): ").strip())
                if hours_per_week > 0:
                    self.data['hours_per_week'] = hours_per_week
                    break
                print("Hours must be greater than 0")
            except ValueError:
                print("Invalid number. Please enter a number like 40")

        # Accrual rate
        print("\nEnter PTO accrual rate:")
        print("  Examples:")
        print("    - 0.0577 = ~3 weeks/year (120 hours)")
        print("    - 0.0769 = ~4 weeks/year (160 hours)")
        print("    - 0.0385 = ~2 weeks/year (80 hours)")
        while True:
            try:
                accrual_rate = float(input("PTO hours earned per hour worked: ").strip())
                if accrual_rate > 0:
                    self.data['accrual_rate'] = accrual_rate
                    break
                print("Accrual rate must be greater than 0")
            except ValueError:
                print("Invalid number. Please enter a decimal like 0.0577")

        self.save_data()
        print("\n✓ Setup complete!")

    def calculate_pto_balance(self, up_to_date=None):
        """Calculate PTO balance up to a specific date"""
        if not all([self.data['start_date'], self.data['hours_per_week'], self.data['accrual_rate']]):
            print("Error: Please complete setup first")
            return None

        start_date = datetime.strptime(self.data['start_date'], '%Y-%m-%d')
        if up_to_date is None:
            up_to_date = datetime.now()

        # Calculate total hours worked
        days_worked = (up_to_date - start_date).days
        if days_worked < 0:
            return 0

        # Assuming work is spread evenly across all days
        hours_per_day = self.data['hours_per_week'] / 7
        total_hours_worked = days_worked * hours_per_day

        # Calculate PTO accrued
        pto_accrued = total_hours_worked * self.data['accrual_rate']

        # Subtract vacation days taken
        vacation_hours_used = 0
        for vacation in self.data['vacation_days']:
            vacation_date = datetime.strptime(vacation['date'], '%Y-%m-%d')
            if vacation_date <= up_to_date:
                vacation_hours_used += vacation['hours']

        return pto_accrued - vacation_hours_used

    def show_daily_balance(self, days=30):
        """Show PTO balance day by day"""
        if not all([self.data['start_date'], self.data['hours_per_week'], self.data['accrual_rate']]):
            print("Error: Please complete setup first")
            return

        print("\n" + "="*60)
        print("PTO BALANCE - DAILY BREAKDOWN")
        print("="*60)

        start_date = datetime.strptime(self.data['start_date'], '%Y-%m-%d')
        today = datetime.now()

        # Create a dict of vacation days for quick lookup
        vacation_dict = {}
        for vacation in self.data['vacation_days']:
            vacation_dict[vacation['date']] = vacation['hours']

        # Show from start or last N days
        if (today - start_date).days > days:
            display_start = today - timedelta(days=days)
            print(f"(Showing last {days} days)\n")
        else:
            display_start = start_date
            print("(Showing all days since start)\n")

        print(f"{'Date':<12} {'Accrued':<10} {'Used':<10} {'Balance':<10}")
        print("-" * 60)

        current_date = display_start
        while current_date <= today:
            date_str = current_date.strftime('%Y-%m-%d')
            balance = self.calculate_pto_balance(current_date)

            # Check if vacation was taken on this day
            vacation_used = vacation_dict.get(date_str, 0)

            # Calculate accrual for this day
            hours_per_day = self.data['hours_per_week'] / 7
            daily_accrual = hours_per_day * self.data['accrual_rate']

            used_str = f"-{vacation_used:.2f}" if vacation_used > 0 else ""
            print(f"{date_str:<12} {daily_accrual:<10.2f} {used_str:<10} {balance:<10.2f}")

            current_date += timedelta(days=1)

    def add_vacation_day(self):
        """Add a planned vacation day"""
        print("\n" + "="*60)
        print("ADD VACATION DAY")
        print("="*60)

        # Date
        while True:
            date_str = input("\nEnter vacation date (YYYY-MM-DD): ").strip()
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
                break
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD")

        # Hours
        while True:
            try:
                hours = float(input("Enter hours to deduct (e.g., 8 for full day): ").strip())
                if hours > 0:
                    break
                print("Hours must be greater than 0")
            except ValueError:
                print("Invalid number")

        # Add to data
        self.data['vacation_days'].append({
            'date': date_str,
            'hours': hours
        })

        # Sort vacation days by date
        self.data['vacation_days'].sort(key=lambda x: x['date'])

        self.save_data()
        print(f"\n✓ Added {hours} hours of vacation on {date_str}")

    def remove_vacation_day(self):
        """Remove a vacation day"""
        if not self.data['vacation_days']:
            print("\nNo vacation days to remove")
            return

        print("\n" + "="*60)
        print("REMOVE VACATION DAY")
        print("="*60)
        print("\nPlanned vacation days:")
        for i, vacation in enumerate(self.data['vacation_days'], 1):
            print(f"  {i}. {vacation['date']} - {vacation['hours']} hours")

        try:
            choice = int(input(f"\nSelect vacation to remove (1-{len(self.data['vacation_days'])}): ").strip())
            if 1 <= choice <= len(self.data['vacation_days']):
                removed = self.data['vacation_days'].pop(choice - 1)
                self.save_data()
                print(f"\n✓ Removed vacation day: {removed['date']} ({removed['hours']} hours)")
            else:
                print("Invalid choice")
        except ValueError:
            print("Invalid input")

    def show_summary(self):
        """Show current PTO summary"""
        print("\n" + "="*60)
        print("PTO SUMMARY")
        print("="*60)

        if not all([self.data['start_date'], self.data['hours_per_week'], self.data['accrual_rate']]):
            print("\n⚠ Setup not complete. Please run setup first.")
            return

        print(f"\nStart Date: {self.data['start_date']}")
        print(f"Hours per Week: {self.data['hours_per_week']}")
        print(f"Accrual Rate: {self.data['accrual_rate']} hours PTO per hour worked")

        start_date = datetime.strptime(self.data['start_date'], '%Y-%m-%d')
        days_since_start = (datetime.now() - start_date).days
        print(f"Days Since Start: {days_since_start}")

        current_balance = self.calculate_pto_balance()
        print(f"\n{'Current PTO Balance:':<25} {current_balance:.2f} hours ({current_balance/8:.2f} days)")

        # Calculate total accrued and used
        total_accrued = self.calculate_pto_balance(datetime.now())
        total_used = sum(v['hours'] for v in self.data['vacation_days']
                        if datetime.strptime(v['date'], '%Y-%m-%d') <= datetime.now())

        print(f"{'Total Accrued:':<25} {total_accrued + total_used:.2f} hours")
        print(f"{'Total Used:':<25} {total_used:.2f} hours")

        # Show planned vacation
        future_vacation = [v for v in self.data['vacation_days']
                          if datetime.strptime(v['date'], '%Y-%m-%d') > datetime.now()]

        if future_vacation:
            print(f"\nPlanned Vacation Days: {len(future_vacation)}")
            for vacation in future_vacation[:5]:  # Show next 5
                print(f"  - {vacation['date']}: {vacation['hours']} hours")
            if len(future_vacation) > 5:
                print(f"  ... and {len(future_vacation) - 5} more")


def main():
    tracker = PTOTracker()

    while True:
        print("\n" + "="*60)
        print("PTO TRACKER")
        print("="*60)
        print("\n1. Show Summary")
        print("2. Show Daily Balance")
        print("3. Add Vacation Day")
        print("4. Remove Vacation Day")
        print("5. Setup/Reconfigure")
        print("6. Exit")

        choice = input("\nSelect an option (1-6): ").strip()

        if choice == '1':
            tracker.show_summary()
        elif choice == '2':
            days_input = input("\nShow how many days? (default: 30): ").strip()
            days = int(days_input) if days_input else 30
            tracker.show_daily_balance(days)
        elif choice == '3':
            tracker.add_vacation_day()
        elif choice == '4':
            tracker.remove_vacation_day()
        elif choice == '5':
            tracker.setup()
        elif choice == '6':
            print("\nGoodbye!")
            break
        else:
            print("\nInvalid choice. Please select 1-6.")


if __name__ == "__main__":
    main()

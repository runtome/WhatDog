#!/usr/bin/env python3
"""
Simple Log Viewer for LINE Chatbot (no external dependencies)
Usage: python view_logs_simple.py [date]
Example: python view_logs_simple.py 05-02-2026
         python view_logs_simple.py today
         python view_logs_simple.py yesterday
         python view_logs_simple.py list
"""

import csv
import os
import sys
from datetime import datetime, timedelta


def get_date_string(date_arg=None):
    """Convert date argument to DD-MM-YYYY format."""
    if date_arg is None or date_arg == "today":
        return datetime.now().strftime("%d-%m-%Y")
    elif date_arg == "yesterday":
        yesterday = datetime.now() - timedelta(days=1)
        return yesterday.strftime("%d-%m-%Y")
    else:
        return date_arg


def read_log_file(date_str):
    """Read log file for a given date."""
    csv_filename = os.path.join("logs", f"{date_str}.csv")
    
    if not os.path.exists(csv_filename):
        print(f"\n❌ No log file found for {date_str}")
        print(f"   Looking for: {csv_filename}")
        return None
    
    logs = []
    try:
        with open(csv_filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                logs.append(row)
        
        return logs
    except Exception as e:
        print(f"\n❌ Error reading log file: {e}")
        return None


def display_logs(logs, date_str):
    """Display logs in a simple format."""
    if not logs:
        print(f"\n📭 No conversations logged for {date_str}")
        return
    
    print(f"\n{'='*80}")
    print(f"📊 Conversation Logs for {date_str}")
    print(f"{'='*80}\n")
    
    for i, log in enumerate(logs, 1):
        print(f"[{i}] {log['time']}")
        print(f"    👤 User: {log['line_user']}")
        print(f"    ❓ Question: {log['question']}")
        print(f"    💬 Answer: {log['answer_reply']}")
        print(f"    ⏱️  Response Time: {log['response_time']}")
        print(f"    {'-'*76}")
    
    # Display statistics
    print(f"\n{'='*80}")
    print(f"📈 Statistics for {date_str}")
    print(f"{'='*80}")
    print(f"📝 Total conversations: {len(logs)}")
    
    # Count unique users
    unique_users = len(set(log['line_user'] for log in logs))
    print(f"👥 Unique users: {unique_users}")
    
    # Count image vs text
    image_count = sum(1 for log in logs if '[IMAGE]' in log['question'])
    text_count = len(logs) - image_count
    print(f"💬 Text messages: {text_count}")
    print(f"🖼️  Image messages: {image_count}")
    
    # Average response time
    try:
        response_times = [float(log['response_time'].replace('s', '')) for log in logs]
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        min_response_time = min(response_times)
        
        print(f"\n⏱️  Response times:")
        print(f"   • Average: {avg_response_time:.3f}s")
        print(f"   • Fastest: {min_response_time:.3f}s")
        print(f"   • Slowest: {max_response_time:.3f}s")
    except:
        pass
    
    print(f"{'='*80}\n")


def list_all_logs():
    """List all available log files."""
    logs_dir = "logs"
    
    if not os.path.exists(logs_dir):
        print("\n❌ No logs directory found")
        return
    
    csv_files = [f for f in os.listdir(logs_dir) if f.endswith('.csv')]
    
    if not csv_files:
        print("\n📭 No log files found")
        return
    
    print(f"\n{'='*80}")
    print(f"📁 Available log files")
    print(f"{'='*80}\n")
    
    for csv_file in sorted(csv_files, reverse=True):
        filepath = os.path.join(logs_dir, csv_file)
        
        # Get file size
        file_size = os.path.getsize(filepath)
        
        # Count lines in file
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                line_count = sum(1 for line in f) - 1  # Subtract header
            
            print(f"📄 {csv_file:<25} {line_count:>4} conversations  ({file_size:,} bytes)")
        except:
            print(f"📄 {csv_file:<25} ({file_size:,} bytes)")
    
    print(f"\n{'='*80}")
    print(f"💡 View a specific log: python view_logs_simple.py DD-MM-YYYY")
    print(f"   Example: python view_logs_simple.py {datetime.now().strftime('%d-%m-%Y')}")
    print(f"{'='*80}\n")


def export_to_summary(date_str):
    """Export summary statistics."""
    logs = read_log_file(date_str)
    if not logs:
        return
    
    summary_file = os.path.join("logs", f"summary_{date_str}.txt")
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(f"Summary Report for {date_str}\n")
        f.write(f"{'='*60}\n\n")
        f.write(f"Total conversations: {len(logs)}\n")
        f.write(f"Unique users: {len(set(log['line_user'] for log in logs))}\n")
        
        image_count = sum(1 for log in logs if '[IMAGE]' in log['question'])
        f.write(f"Text messages: {len(logs) - image_count}\n")
        f.write(f"Image messages: {image_count}\n\n")
        
        # Response times
        try:
            response_times = [float(log['response_time'].replace('s', '')) for log in logs]
            f.write(f"Average response time: {sum(response_times) / len(response_times):.3f}s\n")
            f.write(f"Fastest response: {min(response_times):.3f}s\n")
            f.write(f"Slowest response: {max(response_times):.3f}s\n")
        except:
            pass
    
    print(f"\n✅ Summary exported to: {summary_file}")


def main():
    """Main function."""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║            LINE Chatbot Log Viewer (Simple)                   ║
╚═══════════════════════════════════════════════════════════════╝
""")
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "list":
            list_all_logs()
        elif sys.argv[1] == "export":
            if len(sys.argv) > 2:
                date_str = get_date_string(sys.argv[2])
            else:
                date_str = get_date_string("today")
            export_to_summary(date_str)
        else:
            date_str = get_date_string(sys.argv[1])
            logs = read_log_file(date_str)
            if logs is not None:
                display_logs(logs, date_str)
    else:
        # Default to today
        date_str = get_date_string("today")
        logs = read_log_file(date_str)
        if logs is not None:
            display_logs(logs, date_str)
        else:
            # If today's log doesn't exist, list all logs
            print("\n💡 No log found for today. Here are all available logs:\n")
            list_all_logs()


if __name__ == "__main__":
    main()
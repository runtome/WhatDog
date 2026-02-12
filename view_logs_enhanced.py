#!/usr/bin/env python3
"""
Enhanced Log Viewer for LINE Chatbot with Thinking Process
Usage: python view_logs_enhanced.py [date] [--show-thinking]
Example: python view_logs_enhanced.py 05-02-2026
         python view_logs_enhanced.py today --show-thinking
         python view_logs_enhanced.py yesterday
         python view_logs_enhanced.py list
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


def display_logs(logs, date_str, show_thinking=False):
    """Display logs in a simple format."""
    if not logs:
        print(f"\n📭 No conversations logged for {date_str}")
        return
    
    print(f"\n{'='*80}")
    print(f"📊 Conversation Logs for {date_str}")
    if show_thinking:
        print(f"🧠 Showing thinking process")
    print(f"{'='*80}\n")
    
    for i, log in enumerate(logs, 1):
        print(f"[{i}] {log['time']}")
        print(f"    👤 User: {log['line_user']}")
        print(f"    ❓ Question: {log['question']}")
        print(f"    💬 Answer: {log['answer_reply'][:200]}{'...' if len(log['answer_reply']) > 200 else ''}")
        
        # Show thinking process if requested and available
        if show_thinking and 'thinking_process' in log and log['thinking_process']:
            print(f"    🧠 Thinking:")
            # Indent the thinking process
            thinking_lines = log['thinking_process'].split('\n')
            for line in thinking_lines:
                if line.strip():
                    print(f"       {line}")
        
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
    
    # Count entries with thinking process
    if 'thinking_process' in logs[0]:
        thinking_count = sum(1 for log in logs if log.get('thinking_process', '').strip())
        print(f"🧠 Entries with thinking process: {thinking_count}")
    
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


def display_single_entry(log, show_thinking=False):
    """Display a single log entry in detail."""
    print(f"\n{'='*80}")
    print(f"📋 Conversation Details")
    print(f"{'='*80}\n")
    
    print(f"⏰ Time: {log['time']}")
    print(f"👤 User: {log['line_user']}")
    print(f"⏱️  Response Time: {log['response_time']}")
    
    print(f"\n❓ Question:")
    print(f"   {log['question']}")
    
    if show_thinking and 'thinking_process' in log and log['thinking_process']:
        print(f"\n🧠 Thinking Process:")
        print(f"{'─'*80}")
        print(log['thinking_process'])
        print(f"{'─'*80}")
    
    print(f"\n💬 Answer:")
    print(f"{'─'*80}")
    print(log['answer_reply'])
    print(f"{'─'*80}\n")


def search_logs(logs, search_term):
    """Search logs for a specific term."""
    results = []
    for log in logs:
        if (search_term.lower() in log['question'].lower() or 
            search_term.lower() in log['answer_reply'].lower()):
            results.append(log)
    return results


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
            
            # Count thinking entries
            thinking_count = 0
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('thinking_process', '').strip():
                        thinking_count += 1
            
            print(f"📄 {csv_file:<25} {line_count:>4} conversations  (🧠 {thinking_count} with thinking)  ({file_size:,} bytes)")
        except:
            print(f"📄 {csv_file:<25} ({file_size:,} bytes)")
    
    print(f"\n{'='*80}")
    print(f"💡 View logs: python view_logs_enhanced.py DD-MM-YYYY")
    print(f"   Example: python view_logs_enhanced.py {datetime.now().strftime('%d-%m-%Y')}")
    print(f"   Show thinking: python view_logs_enhanced.py {datetime.now().strftime('%d-%m-%Y')} --show-thinking")
    print(f"{'='*80}\n")


def main():
    """Main function."""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║        LINE Chatbot Log Viewer (Enhanced with Thinking)      ║
╚═══════════════════════════════════════════════════════════════╝
""")
    
    show_thinking = '--show-thinking' in sys.argv or '-t' in sys.argv
    search_mode = '--search' in sys.argv or '-s' in sys.argv
    
    # Remove flags from arguments
    args = [arg for arg in sys.argv[1:] if not arg.startswith('--') and not arg.startswith('-')]
    
    if 'list' in sys.argv:
        list_all_logs()
    elif search_mode and len(args) >= 2:
        # Search mode: view_logs_enhanced.py --search TERM [date]
        search_term = args[0]
        date_str = get_date_string(args[1] if len(args) > 1 else "today")
        
        logs = read_log_file(date_str)
        if logs:
            results = search_logs(logs, search_term)
            if results:
                print(f"\n🔍 Found {len(results)} results for '{search_term}' in {date_str}")
                display_logs(results, date_str, show_thinking)
            else:
                print(f"\n🔍 No results found for '{search_term}' in {date_str}")
    elif len(args) >= 1:
        # View specific date
        date_str = get_date_string(args[0])
        logs = read_log_file(date_str)
        if logs is not None:
            display_logs(logs, date_str, show_thinking)
    else:
        # Default to today
        date_str = get_date_string("today")
        logs = read_log_file(date_str)
        if logs is not None:
            display_logs(logs, date_str, show_thinking)
        else:
            # If today's log doesn't exist, list all logs
            print("\n💡 No log found for today. Here are all available logs:\n")
            list_all_logs()


if __name__ == "__main__":
    main()

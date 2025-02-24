import psutil
import csv
import time
import platform
import sys
from datetime import datetime
from pathlib import Path
from collections import defaultdict

class ConnectionTracker:
    def __init__(self):
        # Separate tracking for TCP and UDP connections
        self.tcp_connections = defaultdict(lambda: {'count': 0, 'first_seen': None, 'last_seen': None, 'info': None})
        self.udp_connections = defaultdict(lambda: {'count': 0, 'first_seen': None, 'last_seen': None, 'info': None})
        self.total_tcp_tracked = 0
        self.total_udp_tracked = 0
    
    @property
    def total_tracked(self):
        """Total number of unique connections tracked (TCP + UDP)"""
        return self.total_tcp_tracked + self.total_udp_tracked

    def get_connection_key(self, conn_info):
        """
        Creates a unique key for a connection based on its endpoints.
        """
        local_ip, local_port, remote_ip, remote_port, status, protocol = conn_info
        # For UDP endpoints without a remote address, use only local information
        if protocol == 'UDP' and not remote_ip:
            return f"{protocol}-{local_ip}:{local_port}"
        
        # Create keys for both directions and use the smaller one to ensure uniqueness
        key1 = f"{protocol}-{local_ip}:{local_port}-{remote_ip}:{remote_port}"
        key2 = f"{protocol}-{remote_ip}:{remote_port}-{local_ip}:{local_port}"
        return min(key1, key2)

    def update(self, new_connections):
        """
        Update the connection history with new connections.
        Returns newly discovered connections for both TCP and UDP.
        """
        current_time = datetime.now()
        newly_discovered = []

        for conn_info in new_connections:
            protocol = conn_info[5]  # Get protocol from the extended connection info
            connections_dict = self.tcp_connections if protocol == 'TCP' else self.udp_connections
            
            key = self.get_connection_key(conn_info)
            if connections_dict[key]['first_seen'] is None:
                # This is a new connection we haven't seen before
                connections_dict[key].update({
                    'first_seen': current_time,
                    'info': conn_info,
                    'count': 1
                })
                newly_discovered.append(conn_info)
                if protocol == 'TCP':
                    self.total_tcp_tracked += 1
                else:
                    self.total_udp_tracked += 1
            else:
                # We've seen this connection before
                connections_dict[key]['count'] += 1
            
            # Update last seen time
            connections_dict[key]['last_seen'] = current_time

        return newly_discovered

def check_privileges():
    """
    Check if the script has the necessary privileges to access network information.
    """
    try:
        psutil.net_connections(kind='inet')
        return True
    except psutil.AccessDenied:
        return False

def get_current_connections():
    """
    Get current network connections including both TCP and UDP.
    Returns a list of tuples containing connection information.
    """
    connections = []
    try:
        # Get TCP connections
        for conn in psutil.net_connections(kind='inet'):
            try:
                if conn.raddr:  # Only include connections with remote address for TCP
                    local_ip = conn.laddr.ip
                    local_port = conn.laddr.port
                    remote_ip = conn.raddr.ip
                    remote_port = conn.raddr.port
                    status = conn.status
                    protocol = 'TCP'
                    
                    connections.append((local_ip, local_port, remote_ip, remote_port, status, protocol))
            except (IndexError, AttributeError):
                continue

        # Get UDP connections
        for conn in psutil.net_connections(kind='udp'):
            try:
                local_ip = conn.laddr.ip
                local_port = conn.laddr.port
                
                # Handle case where there might not be a remote address (common in UDP)
                remote_ip = conn.raddr.ip if conn.raddr else ''
                remote_port = conn.raddr.port if conn.raddr else 0
                
                status = conn.status
                protocol = 'UDP'
                
                connections.append((local_ip, local_port, remote_ip, remote_port, status, protocol))
            except (IndexError, AttributeError):
                continue
                
    except psutil.AccessDenied:
        print("Access denied. Try running with administrator/root privileges.")
        sys.exit(1)
    
    return connections

def get_local_backup_directory():
    """
    Create and return path to local backup directory in the same folder as the script.
    Returns:
        Path: Path object pointing to the backup directory
    """
    script_dir = Path(__file__).parent
    backup_dir = script_dir / 'backups'
    
    try:
        backup_dir.mkdir(exist_ok=True)
    except Exception as e:
        print(f"Error creating backup directory: {e}")
        # Fallback to user's home directory if we can't create in script directory
        backup_dir = Path.home() / 'netconmon_backups'
        backup_dir.mkdir(exist_ok=True)
    
    return backup_dir

def get_output_directory():
    """
    Get the appropriate output directory for the current platform.
    """
    system = platform.system().lower()
    if system == 'windows':
        return Path.home() / 'Documents'
    else:  # macOS and Linux
        return Path.home()

def write_to_csv(tracker, filename, create_parent=True):
    """
    Write connection history to a CSV file.
    
    Args:
        tracker: ConnectionTracker instance
        filename: Path to save the CSV file
        create_parent: If True, create parent directories if they don't exist
    """
    path = Path(filename)
    if create_parent:
        path.parent.mkdir(parents=True, exist_ok=True)
        
    try:
        with path.open('w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Protocol', 'Local IP', 'Local Port', 'Remote IP', 'Remote Port', 'Status', 
                           'First Seen', 'Last Seen', 'Connection Count'])
            
            # Write TCP connections
            for conn_data in tracker.tcp_connections.values():
                if conn_data['first_seen']:
                    info = conn_data['info']
                    writer.writerow([
                        'TCP', info[0], info[1], info[2], info[3], info[4],
                        conn_data['first_seen'].strftime('%Y-%m-%d %H:%M:%S'),
                        conn_data['last_seen'].strftime('%Y-%m-%d %H:%M:%S'),
                        conn_data['count']
                    ])
            
            # Write UDP connections
            for conn_data in tracker.udp_connections.values():
                if conn_data['first_seen']:
                    info = conn_data['info']
                    writer.writerow([
                        'UDP', info[0], info[1], info[2], info[3], info[4],
                        conn_data['first_seen'].strftime('%Y-%m-%d %H:%M:%S'),
                        conn_data['last_seen'].strftime('%Y-%m-%d %H:%M:%S'),
                        conn_data['count']
                    ])
    except PermissionError:
        print(f"Error: Cannot write to {filename}. Permission denied.")
        return False
    except Exception as e:
        print(f"Error writing CSV: {e}")
        return False
    return True

def write_to_txt(tracker, filename, create_parent=True):
    """
    Write connection history to a text file.
    
    Args:
        tracker: ConnectionTracker instance
        filename: Path to save the text file
        create_parent: If True, create parent directories if they don't exist
    """
    path = Path(filename)
    if create_parent:
        path.parent.mkdir(parents=True, exist_ok=True)
        
    try:
        with path.open('w', encoding='utf-8') as txtfile:
            txtfile.write("Network Connections Log\n")
            txtfile.write(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            txtfile.write(f"System: {platform.system()} {platform.release()}\n")
            txtfile.write("-" * 80 + "\n\n")
            
            # Write TCP connections
            txtfile.write("TCP Connections:\n")
            txtfile.write("=" * 40 + "\n")
            for conn_data in tracker.tcp_connections.values():
                if conn_data['first_seen']:
                    info = conn_data['info']
                    txtfile.write(f"Local: {info[0]}:{info[1]} → Remote: {info[2]}:{info[3]} ({info[4]})\n")
                    txtfile.write(f"  First seen: {conn_data['first_seen'].strftime('%Y-%m-%d %H:%M:%S')}\n")
                    txtfile.write(f"  Last seen: {conn_data['last_seen'].strftime('%Y-%m-%d %H:%M:%S')}\n")
                    txtfile.write(f"  Connection count: {conn_data['count']}\n")
                    txtfile.write("-" * 40 + "\n")
            
            # Write UDP connections
            txtfile.write("\nUDP Connections:\n")
            txtfile.write("=" * 40 + "\n")
            for conn_data in tracker.udp_connections.values():
                if conn_data['first_seen']:
                    info = conn_data['info']
                    remote_info = f"Remote: {info[2]}:{info[3]}" if info[2] else "No remote endpoint"
                    txtfile.write(f"Local: {info[0]}:{info[1]} → {remote_info} ({info[4]})\n")
                    txtfile.write(f"  First seen: {conn_data['first_seen'].strftime('%Y-%m-%d %H:%M:%S')}\n")
                    txtfile.write(f"  Last seen: {conn_data['last_seen'].strftime('%Y-%m-%d %H:%M:%S')}\n")
                    txtfile.write(f"  Connection count: {conn_data['count']}\n")
                    txtfile.write("-" * 40 + "\n")
    except PermissionError:
        print(f"Error: Cannot write to {filename}. Permission denied.")
        return False
    except Exception as e:
        print(f"Error writing TXT: {e}")
        return False
    return True

def main():
    if not check_privileges():
        if platform.system().lower() == 'windows':
            print("Please run this script as Administrator (right-click, Run as Administrator)")
        else:
            print("Please run this script with sudo privileges (sudo python3 network_monitor.py)")
        sys.exit(1)

    # Configuration
    SAMPLE_INTERVAL = 0.1  # seconds between checks
    STATS_INTERVAL = 5.0   # seconds between performance stats updates

    print(f"Network Connection Monitor Starting on {platform.system()}...")
    print(f"Sampling every {SAMPLE_INTERVAL} seconds...")
    print("Monitoring for new connections... Press Ctrl+C to stop and save results.")
    
    tracker = ConnectionTracker()
    
    # Performance monitoring variables
    last_stats_time = time.time()
    samples_since_stats = 0
    total_sample_time = 0
    
    try:
        while True:
            sample_start = time.time()
            
            current_connections = get_current_connections()
            new_connections = tracker.update(current_connections)
            
            # Print information about new connections
            for conn in new_connections:
                protocol = conn[5]
                remote_info = f"Remote: {conn[2]}:{conn[3]}" if conn[2] else "No remote endpoint"
                print(f"\nNew {protocol} connection detected:")
                print(f"Local: {conn[0]}:{conn[1]} → {remote_info} ({conn[4]})")
            
            # Update status line
            print(f"\rTotal connections tracked - TCP: {tracker.total_tcp_tracked}, "
                  f"UDP: {tracker.total_udp_tracked}", end='', flush=True)
            
            # Calculate performance metrics
            sample_end = time.time()
            sample_duration = sample_end - sample_start
            total_sample_time += sample_duration
            samples_since_stats += 1
            
            # Print performance stats every STATS_INTERVAL seconds
            if sample_end - last_stats_time >= STATS_INTERVAL:
                avg_sample_time = (total_sample_time / samples_since_stats) * 1000  # Convert to milliseconds
                cpu_percent = psutil.cpu_percent()
                print(f"\nPerformance Stats:")
                print(f"  Average sample time: {avg_sample_time:.2f}ms")
                print(f"  CPU usage: {cpu_percent}%")
                
                # Reset stats
                last_stats_time = sample_end
                samples_since_stats = 0
                total_sample_time = 0
            
            # Sleep for remaining time in the interval
            time_to_sleep = max(0, SAMPLE_INTERVAL - (sample_end - sample_start))
            if time_to_sleep > 0:
                time.sleep(time_to_sleep)
            
    except KeyboardInterrupt:
        print("\n\nSaving results...")
        
        output_dir = get_output_directory()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_filename = output_dir / f'network_connections_{timestamp}.csv'
        txt_filename = output_dir / f'network_connections_{timestamp}.txt'
        
        csv_success = write_to_csv(tracker, csv_filename)
        txt_success = write_to_txt(tracker, txt_filename)
        
        if csv_success and txt_success:
            print(f"Results saved to:")
            print(f"CSV: {csv_filename}")
            print(f"TXT: {txt_filename}")
        else:
            print("There were some errors saving the files. Please check the error messages above.")

if __name__ == "__main__":
    main()
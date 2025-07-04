import subprocess
from ib_insync import IB

def get_windows_host_ip():
    """
    Gets the IP of the Windows host from within WSL2.
    This is necessary to connect to services running on the host.
    """
    try:
        # The nameserver in resolv.conf is the IP of the host in WSL2
        cmd = "grep nameserver /etc/resolv.conf | awk '{print $2}'"
        result = subprocess.check_output(cmd, shell=True, text=True).strip()
        if not result:
            raise ValueError("Command returned an empty string.")
        return result
    except (subprocess.CalledProcessError, FileNotFoundError, ValueError) as e:
        print(f"⚠️  Warning: Could not determine Windows host IP from WSL. Error: {e}")
        print("Falling back to '127.0.0.1'. This will likely fail in a WSL2 environment.")
        return '127.0.0.1'

def main():
    """
    Main function to connect to IBKR Gateway.
    """
    # --- Configuration ---
    # 1. Dynamically get the host IP. This is the correct way.
    HOST_IP = get_windows_host_ip()

    # 2. Set the port for the IBKR Gateway.
    #    - 4001 is for live trading Gateway.
    #    - 4002 is for simulated/paper trading Gateway.
    GATEWAY_PORT = 4002

    # 3. Choose a unique client ID for this connection.
    CLIENT_ID = 1

    print("--- Connection Details ---")
    print(f"Host IP Target: {HOST_IP}")
    print(f"Gateway Port:   {GATEWAY_PORT}")
    print(f"Client ID:      {CLIENT_ID}")
    print("--------------------------\n")

    ib = IB()

    try:
        print("Attempting to connect...")
        # CORRECT: Using the variables for host, port, and client ID.
        ib.connect(HOST_IP, GATEWAY_PORT, clientId=CLIENT_ID, timeout=15)

        if ib.isConnected():
            print("\n✅ Success! Connection established.")
            print(f"   Server Version:  {ib.serverVersion()}")
            print(f"   Connection Time: {ib.twsConnectionTime()}")
        else:
            # This is a rare case but good to handle.
            print("\n❌ Failed to connect. The connect call returned but isConnected() is false.")

    except ConnectionRefusedError:
        print(f"\n❌ Connection Refused. Could not connect to {HOST_IP}:{GATEWAY_PORT}.")
        print("   Please check the following:")
        print("   1. Is IBKR Gateway running on your Windows host?")
        print(f"   2. Is the port correct? (Script is using {GATEWAY_PORT})")
        print("   3. Is 'Allow connections from localhost only' UNCHECKED in Gateway settings?")
        print("   4. Is the Windows Firewall blocking the connection for private networks?")
    except TimeoutError:
         print(f"\n❌ Connection Timed Out. Could not reach {HOST_IP}:{GATEWAY_PORT} within the timeout period.")
         print("   This usually indicates a firewall issue or an incorrect IP address.")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
    finally:
        if ib.isConnected():
            print("\nDisconnecting from IBKR Gateway.")
            ib.disconnect()

if __name__ == "__main__":
    main()
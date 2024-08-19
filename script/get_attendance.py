import psycopg2
import logging
from zk import ZK
from datetime import datetime

# Database connection parameters
DB_HOST = 'localhost'
DB_NAME = 'attendance_db'
DB_USER = 'Fares'
DB_PASSWORD = 'azertysd10'

# ZKTeco device parameters
DEVICE_IP = '192.168.100.201'
DEVICE_PORT = 4370

# Configure logging
logging.basicConfig(
    filename='attendance_log_attendance.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def connect_to_db():
    """ Connect to the PostgreSQL database. """
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn

def create_table_if_not_exists(conn):
    """ Create table if it does not exist. """
    table_exists = False
    with conn.cursor() as cur:
        cur.execute("""
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables 
                WHERE table_name = 'attendance'
            );
        """)
        table_exists = cur.fetchone()[0]
        
        if not table_exists:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS attendance (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER,
                    timestamp TIMESTAMPTZ,
                    attendance_type VARCHAR(10),
                    UNIQUE (user_id, timestamp)
                );
            """)
            conn.commit()
            logging.info('Table "attendance" was created.')
        else:
            logging.info('Table "attendance" already exists.')

def fetch_attendance_data(zk):
    """ Fetch attendance data from ZKTeco device. """
    attendance_data = zk.get_attendance()
    for record in attendance_data:
        print(f"user_id: {record.user_id}, timestamp: {record.timestamp}, status: {record.status}, punch: {record.punch}")
    return attendance_data


def store_data_in_db(conn, data):
    """ Store the attendance data in PostgreSQL. """
    new_records = 0
    with conn.cursor() as cur:
        for record in data:
            user_id = record.user_id
            timestamp = record.timestamp
            attendance_type = "check_out" if record.punch == 1 else "check_in"  # Adjust based on your device's output

            try:
                cur.execute("""
                    INSERT INTO attendance (user_id, timestamp, attendance_type)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (user_id, timestamp) DO NOTHING;
                """, (user_id, timestamp, attendance_type))
                
                if cur.rowcount > 0:
                    new_records += 1
            except Exception as e:
                logging.error(f"Failed to insert record {record}: {str(e)}")
        
        conn.commit()
        if new_records > 0:
            logging.info(f'{new_records} new record(s) added to the "attendance" table.')
        else:
            logging.info('No new records were added to the "attendance" table.')

def main():
    # Connect to ZKTeco device
    zk = ZK(DEVICE_IP, DEVICE_PORT)
    zk.connect()
    zk.disable_device()
    
    # Fetch attendance data
    attendance_data = fetch_attendance_data(zk)
    
    # Connect to PostgreSQL
    conn = connect_to_db()
    create_table_if_not_exists(conn)
    store_data_in_db(conn, attendance_data)
    
    # Disconnect from ZKTeco device
    zk.enable_device()
    zk.disconnect()
    conn.close()

if __name__ == '__main__':
    main()
